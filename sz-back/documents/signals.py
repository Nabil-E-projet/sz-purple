from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaySlip
from django.contrib.auth import get_user_model

@receiver(post_save, sender=PaySlip)
def trigger_payslip_analysis(sender, instance, created, **kwargs):
    """
    Déclenche l'analyse d'une fiche de paie après sa création
    """
    if created and instance.processing_status == 'pending':
        import logging
        logger = logging.getLogger('salariz.documents')
        User = get_user_model()
        try:
            user = User.objects.get(pk=instance.user_id)
            # Consommer 1 crédit si possible, sinon marquer paiement requis
            if hasattr(user, 'try_consume_credits') and user.try_consume_credits(1):
                from analysis.services.analysis_service import AnalysisService
                from analysis.services.gpt_vision_service import GPTVisionService
                gpt_service = GPTVisionService()
                analysis_service = AnalysisService(gpt_service)
                analysis_service.analyze_payslip(instance.id)
            else:
                instance.processing_status = 'payment_required'
                instance.save(update_fields=['processing_status'])
                logger.info(f"Crédits insuffisants pour l'utilisateur {user.id}. Fiche {instance.id} en 'payment_required'.")
        except Exception as e:
            logger = logging.getLogger('salariz.documents')
            logger.error(f"Erreur lors du déclenchement conditionnel de l'analyse {instance.id}: {str(e)}")