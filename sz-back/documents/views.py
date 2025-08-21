from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import PaySlip
from .serializers import PaySlipSerializer, PaySlipDashboardSerializer
from analysis.models import CONVENTION_CHOICES
from django.http import FileResponse, Http404
from wsgiref.util import FileWrapper
import mimetypes
import os
from rest_framework.throttling import UserRateThrottle
import logging
from rest_framework.views import APIView
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
        instance = serializer.save(user=self.request.user)
        logger.info(
            f"Upload de document: user={self.request.user.id}, "
            f"payslip_id={instance.id}, filename={instance.uploaded_file.name}"
        )
class PaySlipListView(generics.ListAPIView):
    serializer_class = PaySlipDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Ne retourner que les fiches de paie de l'utilisateur connecté
        # Optimisation: précharger les analyses pour éviter les requêtes N+1
        return PaySlip.objects.filter(user=self.request.user).select_related('analysis').order_by('-upload_date')

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