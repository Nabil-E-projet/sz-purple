import logging
import traceback
import datetime
import json
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation

from django.db import models

# On importe les modèles des bonnes applications
from documents.models import PaySlip
from analysis.models import BulkAnalysisItem, PayslipAnalysis # Import des modèles d'analyse
from .gpt_vision_service import GPTVisionService
from .reference_data import get_convention_collective_text

logger = logging.getLogger('salariz.analysis')


class AnalysisService:
    def __init__(self, gpt_vision_service=None):
        self.gpt_vision_service = gpt_vision_service or GPTVisionService()

    def analyze_payslip(self, payslip_id: int) -> Optional[PaySlip]:
        """
        Analyse une seule fiche de paie, met à jour son statut et ses données,
        et déclenche la mise à jour de la progression si elle fait partie d'un groupe.
        """
        payslip = None
        try:
            payslip = PaySlip.objects.get(id=payslip_id)
            logger.info(f"Début de l'analyse pour la fiche de paie {payslip.id}")
            
            # DEBUG: Log des données envoyées par l'utilisateur
            logger.info(f"=== DEBUG DONNEES UTILISATEUR ===")
            logger.info(f"Fichier uploadé: {payslip.uploaded_file.name if payslip.uploaded_file else 'Aucun'}")
            logger.info(f"Convention collective: {payslip.convention_collective}")
            logger.info(f"Salaire contractuel: {payslip.contractual_salary}")
            logger.info(f"Détails additionnels: {payslip.additional_details}")
            logger.info(f"Période: {payslip.period}")
            logger.info(f"Nom employé: {payslip.employee_name}")
            logger.info(f"Salaire net: {payslip.net_salary}")
            logger.info(f"Utilisateur: {payslip.user.username}")
            logger.info(f"Date upload: {payslip.upload_date}")
            logger.info(f"=== FIN DEBUG DONNEES UTILISATEUR ===")

            self._update_payslip_status(payslip, 'processing')

            if not payslip.uploaded_file or not hasattr(payslip.uploaded_file, 'path'):
                raise ValueError("Fichier PDF manquant ou chemin invalide")
            pdf_path = payslip.uploaded_file.path

            additional_data = {
                'contractual_salary': float(payslip.contractual_salary) if payslip.contractual_salary else None,
                'additional_details': payslip.additional_details,
                'convention_collective_text': get_convention_collective_text(payslip.convention_collective),
            }
            additional_data = {k: v for k, v in additional_data.items() if v is not None}

            result = self.gpt_vision_service.analyze_pdf(
                pdf_path=pdf_path,
                additional_data=additional_data
            )

            if not result or 'error' in result:
                msg = result.get('details', result.get('error', 'Erreur inconnue'))
                raise RuntimeError(f"Erreur GPT Vision: {msg}")

            # Mise à jour du PaySlip ET de son analyse associée
            self._update_payslip_from_analysis(payslip, result)
            
            self._update_payslip_status(payslip, 'completed')
            logger.info(f"Analyse terminée avec succès pour PaySlip {payslip.id}")

            # Gestion de l'analyse groupée
            group_item = BulkAnalysisItem.objects.filter(payslip=payslip).first()
            if group_item:
                logger.info(f"PaySlip {payslip.id} fait partie du groupe {group_item.group.id}. Mise à jour de la progression.")
                group_item.group.update_progress()

            return payslip

        except PaySlip.DoesNotExist:
            logger.error(f"PaySlip #{payslip_id} introuvable.")
            return None
        except Exception as e:
            logger.error(f"Erreur majeure lors de l'analyse du PaySlip {payslip_id if payslip else 'ID inconnu'}: {e}")
            logger.debug(traceback.format_exc())
            if payslip:
                self._handle_analysis_exception(e, payslip)
            return None

    def _update_payslip_from_analysis(self, payslip: PaySlip, analysis_result: Dict[str, Any]):
        """
        Met à jour le modèle PaySlip avec les données extraites ET crée/met à jour
        l'objet PayslipAnalysis associé avec les résultats complets.
        """
        # === ÉTAPE 1 : Calculer les scores et enrichir les résultats ===
        enriched_result = self._calculate_scores(analysis_result)
        
        # === ÉTAPE 2 : Sauvegarder le résultat complet dans PayslipAnalysis ===
        analysis, created = PayslipAnalysis.objects.get_or_create(
            payslip=payslip,
            defaults={
                'analysis_status': 'success',
                'analysis_details': enriched_result
            }
        )
        if not created:
            analysis.analysis_status = 'success'
            analysis.analysis_details = enriched_result
            analysis.save()
        
        # === ÉTAPE 3 : Mettre à jour les champs clés sur le PaySlip lui-même ===
        gpt_data = enriched_result.get('gpt_analysis', {})
        updated_fields = []
        
        # Période (texte et date)
        periode_data = gpt_data.get('periode', {})
        du = periode_data.get('periode_du')
        au = periode_data.get('periode_au')
        
        new_period_str = f"{du} - {au}" if du and au else du or au
        if new_period_str and payslip.period != new_period_str:
            payslip.period = new_period_str
            updated_fields.append('period')
            
            period_date_obj = self._parse_period_to_date(new_period_str)
            if period_date_obj:
                payslip.period_date = period_date_obj
                updated_fields.append('period_date')

        # Informations générales et rémunération
        info_gen = gpt_data.get('informations_generales', {})
        remu_data = gpt_data.get('remuneration', {})

        fields_mapping = {
            'employee_name': info_gen.get('nom_salarie'),
            'net_salary': remu_data.get('net_a_payer'),
        }

        for field_name, raw_value in fields_mapping.items():
            if raw_value is None: continue
            try:
                field_obj = payslip._meta.get_field(field_name)
                if isinstance(field_obj, models.DecimalField):
                    clean_value = str(raw_value).replace(',', '.').replace(' ', '')
                    if not clean_value: continue
                    new_value = Decimal(clean_value)
                else:
                    new_value = str(raw_value).strip()

                if getattr(payslip, field_name) != new_value:
                    setattr(payslip, field_name, new_value)
                    updated_fields.append(field_name)
            except (InvalidOperation, ValueError, TypeError) as e:
                logger.warning(f"Échec de conversion pour '{field_name}' avec la valeur '{raw_value}': {e}")

        if updated_fields:
            payslip.save(update_fields=list(set(updated_fields)))
            logger.info(f"PaySlip {payslip.id} mis à jour. Champs: {list(set(updated_fields))}")

    def _parse_period_to_date(self, period_str: str) -> Optional[datetime.date]:
        """Tente de parser une chaîne de période en un objet date."""
        if not period_str: return None
        try:
            if ' - ' in period_str:
                start_date_str = period_str.split(' - ')[0]
                return datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
            
            month_map = {
                'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
                'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
            }
            parts = period_str.lower().split()
            if len(parts) == 2 and parts[0] in month_map:
                month = month_map[parts[0]]
                year = int(parts[1])
                return datetime.date(year, month, 1)
        except (ValueError, IndexError) as e:
            logger.warning(f"Impossible de parser la date depuis la chaîne '{period_str}': {e}")
        return None

    def _update_payslip_status(self, payslip: PaySlip, status: str):
        """Met à jour le statut de traitement de la fiche de paie."""
        if payslip.processing_status != status:
            payslip.processing_status = status
            payslip.save(update_fields=['processing_status'])
            logger.info(f"Statut PaySlip {payslip.id} -> {status}")

    def _handle_analysis_exception(self, exc: Exception, payslip: PaySlip):
        """Gère les erreurs d'analyse, met à jour le statut et sauvegarde les détails."""
        payslip.processing_status = 'error'
        payslip.save(update_fields=['processing_status'])
        
        # Créer ou mettre à jour l'analyse avec l'erreur
        analysis, created = PayslipAnalysis.objects.get_or_create(
            payslip=payslip,
            defaults={
                'analysis_status': 'error',
                'analysis_details': {'error': str(exc), 'traceback': traceback.format_exc()}
            }
        )
        if not created:
            analysis.analysis_details = {'error': str(exc), 'traceback': traceback.format_exc()}
            analysis.analysis_status = 'error'
            analysis.save()
        
        # Mise à jour du groupe si applicable
        group_item = BulkAnalysisItem.objects.filter(payslip=payslip).first()
        if group_item:
            group_item.group.update_progress()
        
        logger.info(f"Statut 'error' enregistré pour PaySlip {payslip.id}.")

    def _calculate_scores(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les scores de conformité et global basés sur l'analyse GPT
        et enrichit les résultats avec ces scores.
        """
        gpt_data = analysis_result.get('gpt_analysis', {})
        anomalies = gpt_data.get('anomalies_potentielles_observees', [])
        
        # Calcul du score de conformité (basé sur les anomalies)
        conformity_score = self._calculate_conformity_score(anomalies)
        
        # Calcul du score global (basé sur conformité + autres facteurs)
        global_score = self._calculate_global_score(gpt_data, conformity_score)
        
        # Enrichir les résultats avec les scores
        enriched_result = analysis_result.copy()
        if 'gpt_analysis' in enriched_result:
            enriched_result['gpt_analysis']['note_conformite_legale'] = conformity_score
            enriched_result['gpt_analysis']['note_globale'] = global_score
            
        # Ajouter des métadonnées sur le scoring
        enriched_result['scoring_metadata'] = {
            'version': '1.0',
            'calculation_date': datetime.datetime.now().isoformat(),
            'total_anomalies': len(anomalies),
            'anomalies_by_severity': self._count_anomalies_by_severity(anomalies)
        }
        
        logger.info(f"Scores calculés - Conformité: {conformity_score}/10, Global: {global_score}/10")
        
        # DEBUG: Log détaillé des données GPT pour debugging
        logger.info(f"=== DEBUG ANALYSE GPT ===")
        logger.info(f"Données GPT reçues: {json.dumps(gpt_data, indent=2, ensure_ascii=False)}")
        logger.info(f"Nombre d'anomalies: {len(anomalies)}")
        for i, anomalie in enumerate(anomalies):
            logger.info(f"Anomalie {i+1}: Type={anomalie.get('type')}, Level={anomalie.get('level')}, Description={anomalie.get('description')}")
        logger.info(f"Score conformité calculé: {conformity_score}")
        logger.info(f"Score global calculé: {global_score}")
        logger.info(f"=== FIN DEBUG ===")
        
        return enriched_result

    def _calculate_conformity_score(self, anomalies: list) -> float:
        """
        Calcule le score de conformité légale basé sur les anomalies détectées.
        Score sur 10, où 10 = parfaitement conforme, 0 = très problématique.
        """
        if not anomalies:
            logger.info("Aucune anomalie détectée, score de conformité = 10.0")
            return 10.0
        
        # Pondération par gravité (compatible avec le champ 'level' de GPT)
        severity_weights = {
            'critical': 3.0,  # Anomalie critique = -3 points
            'haute': 3.0,     # Anomalie grave = -3 points  
            'warning': 1.5,   # Anomalie warning = -1.5 points
            'moyenne': 1.5,   # Anomalie moyenne = -1.5 points
            'info': 0.5,      # Anomalie info = -0.5 points
            'basse': 0.5,     # Anomalie mineure = -0.5 points
            'positive_check': 0.0  # Pas de pénalité pour les vérifications positives
        }
        
        total_penalty = 0.0
        logger.info(f"Calcul du score de conformité pour {len(anomalies)} anomalie(s):")
        
        for i, anomalie in enumerate(anomalies):
            # Compatibilité avec les deux formats (level et gravite)
            severity = anomalie.get('level', anomalie.get('gravite', 'basse')).lower()
            penalty = severity_weights.get(severity, 0.5)
            total_penalty += penalty
            logger.info(f"  Anomalie {i+1}: severity='{severity}' -> pénalité={penalty}")
        
        # Score final (minimum 0, maximum 10)
        score = max(0.0, min(10.0, 10.0 - total_penalty))
        logger.info(f"Score conformité: 10.0 - {total_penalty} = {score}")
        return round(score, 1)

    def _calculate_global_score(self, gpt_data: dict, conformity_score: float) -> float:
        """
        Calcule un score global tenant compte de la conformité et d'autres facteurs.
        """
        logger.info(f"Calcul du score global basé sur conformité: {conformity_score}")
        
        # Base : score de conformité (poids 60%)
        score = conformity_score * 0.6
        logger.info(f"  Score base (conformité * 0.6): {score}")
        
        # Facteur complétude des informations (poids 20%)
        completeness_score = self._calculate_completeness_score(gpt_data)
        score += completeness_score * 0.2
        logger.info(f"  Score complétude: {completeness_score}, ajout: {completeness_score * 0.2}")
        
        # Facteur clarté/lisibilité (poids 10%)
        clarity_score = self._calculate_clarity_score(gpt_data)
        score += clarity_score * 0.1
        logger.info(f"  Score clarté: {clarity_score}, ajout: {clarity_score * 0.1}")
        
        # Facteur bonus/malus spéciaux (poids 10%)
        special_score = self._calculate_special_factors_score(gpt_data)
        score += special_score * 0.1
        logger.info(f"  Score spécial: {special_score}, ajout: {special_score * 0.1}")
        
        final_score = round(min(10.0, max(0.0, score)), 1)
        logger.info(f"Score global final: {final_score}")
        
        return final_score

    def _calculate_completeness_score(self, gpt_data: dict) -> float:
        """
        Évalue la complétude des informations extraites.
        """
        required_fields = [
            ('informations_generales', 'nom_salarie'),
            ('periode', 'periode_du'),
            ('periode', 'periode_au'),
            ('remuneration', 'net_a_payer'),
            ('details_salaire', 'salaire_brut'),
        ]
        
        found_fields = 0
        for section, field in required_fields:
            if gpt_data.get(section, {}).get(field):
                found_fields += 1
        
        return (found_fields / len(required_fields)) * 10.0

    def _calculate_clarity_score(self, gpt_data: dict) -> float:
        """
        Évalue la clarté/lisibilité de la fiche de paie.
        """
        # Score basé sur la présence d'informations structurées
        clarity_indicators = [
            bool(gpt_data.get('convention_collective_detectee')),
            bool(gpt_data.get('details_salaire')),
            bool(gpt_data.get('cotisations_sociales')),
            len(gpt_data.get('anomalies_potentielles_observees', [])) == 0,  # Pas d'anomalies = plus clair
        ]
        
        return (sum(clarity_indicators) / len(clarity_indicators)) * 10.0

    def _calculate_special_factors_score(self, gpt_data: dict) -> float:
        """
        Calcule des bonus/malus spéciaux.
        """
        score = 5.0  # Score neutre de base
        
        # Bonus si convention collective détectée
        if gpt_data.get('convention_collective_detectee'):
            score += 2.0
        
        # Bonus si évaluation financière présente
        if gpt_data.get('evaluation_financiere_salarie'):
            score += 2.0
        
        # Malus si beaucoup d'anomalies
        anomalies_count = len(gpt_data.get('anomalies_potentielles_observees', []))
        if anomalies_count > 5:
            score -= 1.0
        
        return min(10.0, max(0.0, score))

    def _count_anomalies_by_severity(self, anomalies: list) -> dict:
        """
        Compte les anomalies par niveau de gravité.
        """
        counts = {'haute': 0, 'moyenne': 0, 'basse': 0}
        for anomalie in anomalies:
            severity = anomalie.get('gravite', 'basse').lower()
            if severity in counts:
                counts[severity] += 1
        return counts
