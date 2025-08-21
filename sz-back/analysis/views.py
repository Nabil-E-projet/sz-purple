from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from documents.models import PaySlip
from .models import PayslipAnalysis ,BulkAnalysisGroup, BulkAnalysisItem
from django.conf import settings
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import json
import uuid
from documents.serializers import PaySlipSerializer

# Import services
from .services.analysis_service import AnalysisService
from .services.gpt_vision_service import GPTVisionService
from .serializers import PayslipAnalysisSerializer # Assuming you might want to serialize the result

logger = logging.getLogger('salariz.analysis') # Use the correct logger name for this app

class PayslipAnalysisView(APIView):
    """
    Vue pour déclencher l'analyse d'une fiche de paie avec GPT Vision.
    """
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize services here or ensure they are injected/available
        # For simplicity, we instantiate them here
        gpt_vision_service = GPTVisionService() # Assuming API key is handled within
        self.analysis_service = AnalysisService(gpt_vision_service)

    def post(self, request, payslip_id):
        """
        Déclenche l'analyse d'une fiche de paie via GPT Vision.
        """
        logger.info(f"Requête reçue pour analyser la fiche de paie ID: {payslip_id} par l'utilisateur {request.user.id}")
        try:
            # Vérifier que la fiche appartient à l'utilisateur
            payslip = PaySlip.objects.get(id=payslip_id, user=request.user)
            logger.debug(f"Fiche de paie {payslip_id} trouvée pour l'utilisateur {request.user.id}.")

            # Lancer l'analyse (qui utilise maintenant les données supplémentaires stockées dans le modèle PaySlip)
            analysis_result = self.analysis_service.analyze_payslip(payslip_id) # Retourne un PaySlip ou None

            if not analysis_result:
                logger.error(f"Échec de l'analyse pour la fiche de paie {payslip_id}. Le service n'a retourné aucun résultat.")
                return Response({
                    "message": "Erreur lors de l'analyse",
                    "error": "Échec de l'analyse interne du service."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Récupérer l'objet d'analyse lié
            try:
                analysis = analysis_result.analysis  # related_name='analysis'
            except PayslipAnalysis.DoesNotExist:
                logger.error(f"Aucune analyse associée trouvée pour la fiche {payslip_id} après traitement.")
                return Response({
                    "message": "Analyse non disponible",
                    "error": "Analyse introuvable après traitement."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if analysis.analysis_status == 'error':
                error_details = analysis.analysis_details.get('error', 'Erreur inconnue lors de l\'analyse.')
                logger.warning(f"Analyse terminée avec statut 'error' pour la fiche {payslip_id}. Détails: {error_details}")
                return Response({
                    "message": "Erreur lors de l'analyse",
                    "status": analysis.analysis_status,
                    "error": error_details
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Ou 400/422 si c'est une erreur client/GPT

            # Si l'analyse est réussie
            logger.info(f"Analyse réussie pour la fiche de paie {payslip_id}. Statut: {analysis_result.analysis_status}")

            # Préparer la réponse avec les données extraites par GPT
            analysis_details = analysis.analysis_details
            # Ajuster le chemin si la structure de 'result' a changé dans GPTVisionService
            gpt_data = analysis_details.get('gpt_analysis', {}).get('result', {}) # Chemin vers les données JSON extraites

            return Response({
                "message": "Analyse terminée avec succès",
                "status": analysis.analysis_status,
                "payslip_id": payslip_id,
                "analysis_id": analysis.id,
                "analysis_data": gpt_data # Renvoyer les données JSON extraites
            }, status=status.HTTP_200_OK)

        except PaySlip.DoesNotExist:
            logger.warning(f"Tentative d'analyse de la fiche de paie {payslip_id} échouée: Fiche non trouvée ou non appartenant à l'utilisateur {request.user.id}.")
            return Response({
                "error": "Fiche de paie introuvable ou vous n'avez pas les droits."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Erreur inattendue lors de la tentative d'analyse de la fiche {payslip_id}: {str(e)}") # Use logger.exception to include traceback
            return Response({
                "error": f"Erreur serveur inattendue: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FullAnalysisResultView(APIView):
    """
    Vue pour récupérer l'analyse complète (y compris les détails bruts) d'une fiche de paie.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payslip_id):
        """
        Récupère les détails complets de l'analyse pour une fiche de paie donnée.
        """
        logger.info(f"Requête reçue pour récupérer l'analyse complète de la fiche {payslip_id} par l'utilisateur {request.user.id}")
        try:
            # Vérifier que la fiche appartient à l'utilisateur
            payslip = PaySlip.objects.get(id=payslip_id, user=request.user)
            logger.debug(f"Fiche de paie {payslip_id} trouvée pour l'utilisateur {request.user.id}.")

            # Récupérer l'analyse associée
            try:
                # CORRECTION: Utiliser le related_name 'analysis' défini dans le OneToOneField
                # du modèle PayslipAnalysis pour accéder à l'objet lié directement.
                analysis = payslip.analysis
                logger.debug(f"Analyse ID {analysis.id} trouvée pour la fiche {payslip_id}.")
            except PayslipAnalysis.DoesNotExist:
                 logger.warning(f"Aucune analyse trouvée pour la fiche de paie {payslip_id}.")
                 return Response({
                    "error": "Aucune analyse disponible pour cette fiche de paie."
                 }, status=status.HTTP_404_NOT_FOUND)

            # Sérialiser l'analyse complète (optionnel, si vous voulez une structure spécifique)
            # serializer = PayslipAnalysisSerializer(analysis)
            # return Response(serializer.data, status=status.HTTP_200_OK)

            # DEBUG: Log des données retournées à l'API
            logger.info(f"=== DEBUG RETOUR API ===")
            logger.info(f"Analysis ID: {analysis.id}")
            logger.info(f"Status: {analysis.analysis_status}")
            logger.info(f"Details keys: {list(analysis.analysis_details.keys()) if analysis.analysis_details else 'None'}")
            if 'gpt_analysis' in (analysis.analysis_details or {}):
                gpt_data = analysis.analysis_details['gpt_analysis']
                logger.info(f"GPT Analysis keys: {list(gpt_data.keys()) if gpt_data else 'None'}")
                logger.info(f"Note conformité dans DB: {gpt_data.get('note_conformite_legale', 'ABSENTE')}")
                logger.info(f"Note globale dans DB: {gpt_data.get('note_globale', 'ABSENTE')}")
            logger.info(f"=== FIN DEBUG API ===")
            
            # Ou retourner directement les détails stockés dans le modèle PayslipAnalysis
            return Response({
                "payslip_id": payslip.id,
                "analysis_id": analysis.id,
                "status": analysis.analysis_status,
                "date": analysis.analysis_date,
                "details": analysis.analysis_details # Contient tout ce qui a été sauvegardé par AnalysisService
            }, status=status.HTTP_200_OK)

        except PaySlip.DoesNotExist:
            logger.warning(f"Tentative de récupération d'analyse pour la fiche {payslip_id} échouée: Fiche non trouvée ou non appartenant à l'utilisateur {request.user.id}.")
            return Response({
                "error": "Fiche de paie introuvable ou vous n'avez pas les droits."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Erreur inattendue lors de la récupération de l'analyse complète pour la fiche {payslip_id}: {str(e)}")
            return Response({
                "error": f"Erreur serveur inattendue: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BulkAnalysisUploadView(APIView):
    """Vue pour l'upload de plusieurs fiches de paie à analyser ensemble."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """Reçoit plusieurs fichiers, les enregistre et crée un groupe d'analyse."""
        files = request.FILES.getlist('files')
        periods = json.loads(request.data.get('periods', '{}'))
        convention = request.data.get('convention_collective', 'AUTRE')
        name = request.data.get('name', 'Analyse groupée')

        # Validation
        if not files:
            return Response({"error": "Aucun fichier fourni"}, status=status.HTTP_400_BAD_REQUEST)
            
        if len(files) > 12:
            return Response({"error": "Maximum 12 fichiers autorisés"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Créer un groupe d'analyse
        analysis_group = BulkAnalysisGroup.objects.create(
            user=request.user,
            convention_collective=convention,
            name=name,
            total_files=len(files)
        )
        
        # Enregistrer chaque fichier et créer les fiches de paie
        payslips = []
        for index, file in enumerate(files):
            # Déterminer la période si fournie
            period_str = periods.get(str(index))
            
            # Créer le PaySlip
            serializer = PaySlipSerializer(data={
                'uploaded_file': file,
                'convention_collective': convention,
                'period': period_str
            })
            
            if serializer.is_valid():
                payslip = serializer.save(user=request.user)
                payslips.append(payslip)
                
                # Lier au groupe d'analyse
                BulkAnalysisItem.objects.create(
                    group=analysis_group,
                    payslip=payslip,
                    order=index
                )
            else:
                # En cas d'erreur, on nettoie et on renvoie l'erreur
                analysis_group.delete()
                for p in payslips:
                    p.delete()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Renvoyer l'ID du groupe pour suivi
        return Response({
            "message": f"{len(files)} fichiers uploadés et planifiés pour analyse",
            "bulk_analysis_id": analysis_group.id,
            "payslip_ids": [p.id for p in payslips]
        }, status=status.HTTP_201_CREATED)


class BulkAnalysisResultView(APIView):
    """Vue pour consulter les résultats d'une analyse groupée."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, analysis_id):
        """Récupère les résultats agrégés et détaillés d'une analyse groupée."""
        analysis_group = get_object_or_404(
            BulkAnalysisGroup, 
            id=analysis_id, 
            user=request.user
        )
        
        # Récupérer les items du groupe et leurs fiches associées
        items = BulkAnalysisItem.objects.filter(
            group=analysis_group
        ).select_related('payslip').order_by('order')
        
        # Construire la réponse
        response_data = {
            "id": analysis_group.id,
            "name": analysis_group.name,
            "status": analysis_group.status,
            "convention": analysis_group.convention_collective,
            "created_at": analysis_group.created_at,
            "progress": {
                "processed": analysis_group.processed_files,
                "total": analysis_group.total_files,
                "percentage": int((analysis_group.processed_files / max(analysis_group.total_files, 1)) * 100)
            },
            "payslips": [{
                "id": item.payslip.id,
                "period": item.payslip.period,
                "status": item.payslip.processing_status,
                "order": item.order
            } for item in items],
        }
        
        # Ajouter les résultats agrégés si l'analyse est terminée
        if analysis_group.status == 'completed':
            response_data.update({
                "total_amount_due": float(analysis_group.total_amount_due) if analysis_group.total_amount_due else 0,
                "missing_benefits": analysis_group.missing_benefits,
                "summary": analysis_group.summary
            })
        
        return Response(response_data)