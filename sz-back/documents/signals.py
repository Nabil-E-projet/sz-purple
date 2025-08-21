from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaySlip

@receiver(post_save, sender=PaySlip)
def trigger_payslip_analysis(sender, instance, created, **kwargs):
    """
    Déclenche l'analyse d'une fiche de paie après sa création
    """
    if created and instance.processing_status == 'pending':  # Modifié ici
        # Import ici pour éviter les imports circulaires
        from analysis.services.analysis_service import AnalysisService
        from analysis.services.gpt_vision_service import GPTVisionService
        
        try:
            gpt_service = GPTVisionService()
            analysis_service = AnalysisService(gpt_service)
            analysis_service.analyze_payslip(instance.id)
        except Exception as e:
            import logging
            logger = logging.getLogger('salariz.documents')
            logger.error(f"Erreur lors du déclenchement de l'analyse de la fiche {instance.id}: {str(e)}")