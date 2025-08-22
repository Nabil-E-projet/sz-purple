from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class PaySlip(models.Model):
    """
    Modèle pour stocker les fiches de paie uploadées par les utilisateurs.
    """
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('payment_required', _('Paiement requis')),
        ('processing', _('En cours de traitement')),
        ('completed', _('Traitement terminé')),
        ('error', _('Erreur de traitement')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name=_('Utilisateur')
    )
    
    uploaded_file = models.FileField(
        upload_to='payslips/',
        verbose_name=_('Fichier téléchargé')
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date d\'upload')
    )
    
    processing_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Statut de traitement')
    )
    
    analysis_type = models.CharField(
        max_length=20,
        default='single',
        verbose_name=_('Type d\'analyse')
    )
    
    # Données supplémentaires fournies à l'upload
    contractual_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Salaire brut mensuel contractuel')
    )
    
    additional_details = models.TextField(null=True, blank=True, verbose_name="Détails supplémentaires fournis par l'utilisateur")

    
    convention_collective = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Convention collective')
    )
    
    # Contexte optionnel pour améliorer l'analyse et permettre des calculs déterministes
    EMPLOYMENT_STATUS_CHOICES = [
        ('APPRENTI', _('Apprenti')), 
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('STAGIAIRE', _('Stagiaire')),
        ('TEMPS_PARTIEL', _('Temps partiel')),
        ('AUTRE', _('Autre')),
    ]
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_('Statut d\'emploi')
    )
    expected_smic_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Pourcentage du SMIC attendu pour cette période (ex: 75 pour 75%)'),
        verbose_name=_('Pourcentage SMIC attendu')
    )
    working_time_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=1.00,
        help_text=_('Ratio temps de travail (1.00 = temps plein, 0.80 = 80%)'),
        verbose_name=_('Ratio temps de travail')
    )
    
    # NOUVEAUX CHAMPS extraits par l'analyse GPT
    period = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Période de la fiche de paie')
    )
        # Dans documents/models.py, classe PaySlip
    period_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date de période (format date)')
    )
    
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Salaire net extrait')
    )
    
    employee_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Nom de l\'employé')
    )
    
    class Meta:
        verbose_name = _('Fiche de paie')
        verbose_name_plural = _('Fiches de paie')
        ordering = ['-upload_date']

    def __str__(self):
        return f"Fiche de paie de {self.user.username} ({self.upload_date.strftime('%d/%m/%Y')})"
    
    def delete(self, *args, **kwargs):
        """Supprime également le fichier physique lors de la suppression de l'entrée."""
        # Supprimer le fichier physique
        if self.uploaded_file:
            storage, path = self.uploaded_file.storage, self.uploaded_file.path
            if storage.exists(path):
                storage.delete(path)
        
        # Appeler la méthode delete du parent
        super().delete(*args, **kwargs)