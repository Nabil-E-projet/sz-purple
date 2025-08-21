from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from documents.models import PaySlip # On importe PaySlip depuis documents
from decimal import Decimal, InvalidOperation

# On définit les choix de convention ici pour être indépendant
CONVENTION_CHOICES = [
    ('SYNTEC', 'Syntec'),
    ('HCR', 'Hôtels, Cafés, Restaurants (HCR)'),
    ('METALLURGIE', 'Métallurgie'),
    ('COMMERCE', 'Commerce de détail et de gros'),
    ('AUTRE', 'Autre / Non spécifiée'),
]

# --- MODÈLE POUR L'ANALYSE UNIQUE ---
class PayslipAnalysis(models.Model):
    """Stocke les résultats de l'analyse d'une fiche de paie unique."""
    payslip = models.OneToOneField(
        PaySlip, 
        on_delete=models.CASCADE, 
        related_name='analysis',
        verbose_name=_('Fiche de paie')
    )
    analysis_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date d\'analyse'))
    analysis_status = models.CharField(
        max_length=20, 
        choices=[
            ('success', 'Succès'),
            ('error', 'Erreur'),
            ('warning', 'Avertissement')
        ],
        verbose_name=_('Statut de l\'analyse')
    )
    analysis_details = models.JSONField(default=dict, blank=True, verbose_name=_('Détails de l\'analyse'))

    class Meta:
        verbose_name = "Analyse de fiche de paie"
        verbose_name_plural = "Analyses de fiches de paie"

    def __str__(self):
        return f"Analyse #{self.id} pour {self.payslip}"


# --- NOUVEAUX MODÈLES POUR L'ANALYSE GROUPÉE ---
class BulkAnalysisGroup(models.Model):
    """Groupe d'analyse pour plusieurs fiches de paie."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='bulk_analysis_groups',
        verbose_name=_('Utilisateur')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date de création'))
    name = models.CharField(max_length=255, default=_('Analyse groupée'), verbose_name=_('Nom de l\'analyse'))
    
    # On utilise la liste de choix définie plus haut
    convention_collective = models.CharField(
        max_length=50,
        choices=CONVENTION_CHOICES,
        default='AUTRE',
        verbose_name=_('Convention collective')
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('processing', 'En cours'),
            ('completed', 'Terminée'),
            ('error', 'Erreur')
        ],
        default='pending',
        verbose_name=_('Statut')
    )
    total_files = models.IntegerField(default=0, verbose_name=_('Nombre total de fichiers'))
    processed_files = models.IntegerField(default=0, verbose_name=_('Fichiers traités'))
    
    # Résultats agrégés
    total_amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Montant total dû'))
    missing_benefits = models.JSONField(default=dict, blank=True, verbose_name=_('Avantages manquants'))
    summary = models.JSONField(default=dict, blank=True, verbose_name=_('Résumé'))
    
    class Meta:
        verbose_name = _('Analyse groupée')
        verbose_name_plural = _('Analyses groupées')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analyse groupée #{self.id} - {self.user.username}"

    def update_progress(self):
        """Met à jour la progression et lance l'agrégation si terminé."""
        self.processed_files = PayslipAnalysis.objects.filter(
            payslip__bulk_analysis_items__group=self,
            analysis_status__in=['success', 'error']
        ).count()
        
        if self.processed_files >= self.total_files:
            self.status = 'completed'
            self.aggregate_results()
        elif self.processed_files > 0:
            self.status = 'processing'
        
        self.save(update_fields=['processed_files', 'status'])

    def aggregate_results(self):
        """Calcule les résultats agrégés à partir des analyses individuelles."""
        total = Decimal('0.00')
        missing = {}
        
        analyses = PayslipAnalysis.objects.filter(
            payslip__bulk_analysis_items__group=self,
            analysis_status='success'
        ).select_related('payslip').order_by('payslip__period_date')

        for analysis in analyses:
            details = analysis.analysis_details.get('gpt_analysis', {})
            
            montant_du_str = details.get('evaluation_financiere_salarie', {}).get('montant_potentiel_du_salarie')
            if montant_du_str:
                try:
                    total += Decimal(str(montant_du_str).replace(',', '.').replace(' ', ''))
                except InvalidOperation:
                    pass
            
            primes = details.get('anomalies_potentielles_observees', [])
            for prime_anomaly in primes:
                if prime_anomaly.get('type') == 'prime_manquante':
                    prime_name = prime_anomaly.get('description', 'Prime inconnue')
                    missing[prime_name] = missing.get(prime_name, 0) + 1
        
        self.total_amount_due = total
        self.missing_benefits = missing
        self.save(update_fields=['total_amount_due', 'missing_benefits', 'status'])


class BulkAnalysisItem(models.Model):
    """Relie une fiche de paie à un groupe d'analyse."""
    group = models.ForeignKey(
        BulkAnalysisGroup, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('Groupe d\'analyse')
    )
    payslip = models.ForeignKey(
        PaySlip, 
        on_delete=models.CASCADE, 
        related_name='bulk_analysis_items',
        verbose_name=_('Fiche de paie')
    )
    order = models.IntegerField(default=0, verbose_name=_('Ordre'))
    
    class Meta:
        verbose_name = _('Élément d\'analyse groupée')
        verbose_name_plural = _('Éléments d\'analyse groupée')
        ordering = ['order']
        unique_together = ['group', 'payslip']