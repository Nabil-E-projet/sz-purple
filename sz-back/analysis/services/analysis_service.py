import logging
import traceback
import datetime
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
        # === ÉTAPE 1 : Sauvegarder le résultat complet dans PayslipAnalysis ===
        analysis, created = PayslipAnalysis.objects.get_or_create(
            payslip=payslip,
            defaults={
                'analysis_status': 'success',
                'analysis_details': analysis_result
            }
        )
        if not created:
            analysis.analysis_status = 'success'
            analysis.analysis_details = analysis_result
            analysis.save()
        
        # === ÉTAPE 2 : Mettre à jour les champs clés sur le PaySlip lui-même ===
        gpt_data = analysis_result.get('gpt_analysis', {})
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
