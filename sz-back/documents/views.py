from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import PaySlip
from analysis.models import PayslipAnalysis
from .serializers import PaySlipSerializer, PaySlipDashboardSerializer
from analysis.models import CONVENTION_CHOICES
from django.http import FileResponse, Http404
from wsgiref.util import FileWrapper
import mimetypes
import os
from rest_framework.throttling import UserRateThrottle
import logging
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from .models import PaySlip
logger = logging.getLogger('salariz.documents')

class PaySlipFileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            payslip = PaySlip.objects.get(pk=pk, user=request.user)
            file_path = payslip.uploaded_file.path
            
            # Vérification supplémentaire
            if not os.path.exists(file_path):
                raise Http404("Fichier non trouvé")
                
            # Vérifier le type de fichier
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type != 'application/pdf':
                return Response(
                    {"error": "Type de fichier non autorisé"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Servir le fichier de façon sécurisée
            response = FileResponse(
                FileWrapper(open(file_path, 'rb')), 
                content_type=content_type
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            return response
            
        except PaySlip.DoesNotExist:
            raise Http404("Fiche de paie non trouvée")

class UploadRateThrottle(UserRateThrottle):
    rate = '20/day'  # Limiter à 10 uploads par jour


class ConventionCollectiveListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        choices = CONVENTION_CHOICES
        return Response([{'value': v, 'label': l} for v, l in choices])
    
class PaySlipUploadView(generics.CreateAPIView):
    serializer_class = PaySlipSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UploadRateThrottle]
    
    def perform_create(self, serializer):
        # DEBUG: Log des données reçues dans l'upload
        logger.info(f"=== DEBUG UPLOAD BACKEND ===")
        logger.info(f"Utilisateur: {self.request.user.username} (ID: {self.request.user.id})")
        logger.info(f"Fichier reçu: {self.request.FILES.get('uploaded_file')}")
        logger.info(f"Données POST reçues: {dict(self.request.data)}")
        logger.info(f"Convention collective: {self.request.data.get('convention_collective')}")
        logger.info(f"Salaire contractuel: {self.request.data.get('contractual_salary')}")
        logger.info(f"Détails additionnels: {self.request.data.get('additional_details')}")
        logger.info(f"Période: {self.request.data.get('period')}")
        logger.info(f"=== FIN DEBUG UPLOAD BACKEND ===")
        
        instance = serializer.save(user=self.request.user)
        logger.info(
            f"Fiche de paie créée: user={self.request.user.id}, "
            f"payslip_id={instance.id}, filename={instance.uploaded_file.name}"
        )
class PaySlipListView(generics.ListAPIView):
    serializer_class = PaySlipDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetPagination
    
    def get_queryset(self):
        # Ne retourner que les fiches de paie de l'utilisateur connecté
        # Optimisation: précharger les analyses pour éviter les requêtes N+1
        return (
            PaySlip.objects
            .filter(user=self.request.user)
            .select_related('user', 'analysis')
            .only(
                'id', 'uploaded_file', 'upload_date', 'processing_status',
                'period', 'net_salary', 'employee_name', 'user__username',
                'analysis__analysis_details'
            )
            .order_by('-upload_date')
        )

class PaySlipDetailView(generics.RetrieveAPIView):
    serializer_class = PaySlipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Ne retourner que les fiches de paie de l'utilisateur connecté
        return PaySlip.objects.filter(user=self.request.user)
        


class PaySlipDeleteView(generics.DestroyAPIView):
    """
    Vue pour supprimer une fiche de paie.
    """
    queryset = PaySlip.objects.all()
    serializer_class = PaySlipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ne permettre la suppression que des fiches appartenant à l'utilisateur connecté
        return PaySlip.objects.filter(user=self.request.user)


class PaySlipStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        qs_payslips = PaySlip.objects.filter(user=user)
        total_analyses = qs_payslips.count()
        last_upload_date = qs_payslips.order_by('-upload_date').values_list('upload_date', flat=True).first()

        analyses = (
            PayslipAnalysis.objects
            .filter(payslip__user=user)
            .values_list('analysis_details', 'analysis_status')
        )

        total_errors = 0
        score_values = []
        conformity_values = []

        for analysis_details, analysis_status in analyses:
            try:
                details = analysis_details or {}
                gpt = details.get('gpt_analysis', {}) or {}
                anomalies = gpt.get('anomalies_potentielles_observees', []) or []
                total_errors += len(anomalies)

                score = gpt.get('note_globale')
                if score is not None:
                    try:
                        score_values.append(float(str(score).replace(',', '.')))
                    except Exception:
                        pass

                conf = gpt.get('note_conformite_legale')
                if conf is not None:
                    try:
                        conformity_values.append(float(str(conf).replace(',', '.')))
                    except Exception:
                        pass
            except Exception:
                continue

        avg_score = round(sum(score_values) / len(score_values), 1) if score_values else 0.0
        avg_conf = round(sum(conformity_values) / len(conformity_values), 1) if conformity_values else 0.0

        return Response({
            'totalAnalyses': total_analyses,
            'avgScore': avg_score,
            'avgConformityScore': avg_conf,
            'totalErrors': total_errors,
            'lastAnalysis': last_upload_date.isoformat() if last_upload_date else None,
        })