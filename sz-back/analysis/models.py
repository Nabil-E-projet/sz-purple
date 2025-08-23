from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from documents.models import PaySlip # On importe PaySlip depuis documents
from decimal import Decimal, InvalidOperation

# On définit les choix de convention ici pour être indépendant
CONVENTION_CHOICES = [
    ('ACTIVITES_DECHET', 'Activités du déchet'),
    ('AIDE_ET_SOINS_A_DOMICILE', 'Aide et soins à domicile'),
    ('ARTICLES_SPORT_LOISIRS', 'Articles de sport et loisirs'),
    ('ASSURANCES', 'Sociétés d\'assurances'),
    ('ATELIERS_CHANTIERS_INSERTION', 'Ateliers et chantiers d\'insertion'),
    ('AUDIOVISUEL_ELECTRONIQUE', 'Audiovisuel, électronique et équipement ménager'),
    ('BANQUE', 'Banque'),
    ('BATIMENT_CADRES', 'Bâtiment : Cadres'),
    ('BATIMENT_ETAM', 'Bâtiment : ETAM'),
    ('BATIMENT_OUVRIERS_MOINS_10', 'Bâtiment : Ouvriers (-10 salariés)'),
    ('BATIMENT_OUVRIERS_PLUS_10', 'Bâtiment : Ouvriers (+10 salariés)'),
    ('BOULANGERIE_ARTISANALE', 'Boulangerie-pâtisserie artisanale'),
    ('BRICOLAGE', 'Bricolage'),
    ('BUREAU_NUMERIQUE', 'Bureautique et numérique (CCN BETEM)'),
    ('CABINETS_DENTAIRES', 'Cabinets dentaires'),
    ('CABINETS_MEDICAUX', 'Cabinets médicaux'),
    ('CADRES_TRAVAUX_PUBLICS', 'Cadres des travaux publics'),
    ('CENTRES_SOCIAUX', 'Centres sociaux et socioculturels'),
    ('COIFFURE', 'Coiffure'),
    ('COMMERCE_ALIMENTAIRE', 'Commerce de détail alimentaire'),
    ('COMMERCE_DETAIL_ALIMENTAIRE', 'Commerce de détail alimentaire spécialisé'),
    ('COMMERCE_DETAIL_NON_ALIMENTAIRE', 'Commerce de détail non alimentaire'),
    ('COMMERCE_HABILLEMENT_TEXTILE', 'Commerce de l\'habillement et du textile'),
    ('COMMERCES_DE_GROS', 'Commerces de gros'),
    ('ECLAT', 'Éclat (Animation)'),
    ('ENSEIGNEMENT_PRIVE_INDEPENDANT', 'Enseignement privé indépendant'),
    ('ENSEIGNEMENT_PRIVE_NON_LUCATIF', 'Enseignement privé non lucratif (EPNL)'),
    ('ENTREPRISES_DE_PROPRETE', 'Entreprises de propreté'),
    ('ESTHETIQUE_COSMETIQUE', 'Esthétique-cosmétique'),
    ('EXPERTS_COMPTABLES', 'Experts-comptables'),
    ('FERROVIAIRE', 'Ferroviaire'),
    ('GARDIENS_IMMEUBLES', 'Gardiens, concierges et employés d\'immeubles'),
    ('HABILLEMENT_SUCCURSALES', 'Habillement : succursales'),
    ('HCR', 'Hôtels, Cafés, Restaurants (HCR)'),
    ('HOSPITALISATION_NON_LUCATIF', 'Hospitalisation privée non lucrative (FEHAP)'),
    ('HOSPITALISATION_PRIVEE', 'Hospitalisation privée (FHP)'),
    ('IMMOBILIER', 'Immobilier'),
    ('INDUSTRIE_PHARMACEUTIQUE', 'Industrie pharmaceutique'),
    ('INDUSTRIES_ALIMENTAIRES_DIVERSES', 'Industries alimentaires diverses'),
    ('INDUSTRIES_CHIMIQUES', 'Industries chimiques'),
    ('MAINTENANCE_MATERIELS_AGRICOLES', 'Maintenance des matériels agricoles'),
    ('METALLURGIE_CADRES', 'Métallurgie : Cadres'),
    ('METALLURGIE_REGION_PARISIENNE', 'Métallurgie (région parisienne)'),
    ('NEGOCE_AMEUBLEMENT', 'Négoce de l\'ameublement'),
    ('NEGOCE_MATERIAUX_CONSTRUCTION', 'Négoce des matériaux de construction'),
    ('NOTARIAT', 'Notariat'),
    ('ORGANISMES_FORMATION', 'Organismes de formation'),
    ('PARTICULIERS_EMPLOYEURS', 'Particuliers employeurs'),
    ('PERSONNES_INADAPTEES', 'Personnes inadaptées et handicapées (CCN 66)'),
    ('PHARMACIE_OFFICINE', 'Pharmacie d\'officine'),
    ('PLASTURGIE', 'Plasturgie'),
    ('PRESTATAIRES_TERTIAIRE', 'Prestataires de services du secteur tertiaire'),
    ('PREVENTION_SECURITE', 'Prévention et sécurité'),
    ('PUBLICITE', 'Publicité'),
    ('RESTAURATION_COLLECTIVITES', 'Restauration de collectivités'),
    ('RESTAURATION_RAPIDE', 'Restauration rapide'),
    ('SECURITE_SOCIALE', 'Sécurité sociale'),
    ('SERVICES_A_LA_PERSONNE', 'Services à la personne'),
    ('SERVICES_AUTOMOBILE', 'Services de l\'automobile'),
    ('SPORT', 'Sport'),
    ('SYNTEC', 'Syntec (Bureaux d\'études techniques)'),
    ('TELECOMMUNICATIONS', 'Télécommunications'),
    ('TRANSPORT_AERIEN_PERSONNEL_SOL', 'Transport aérien - Personnel au sol'),
    ('TRANSPORTS_PUBLICS_URBAINS', 'Transports publics urbains'),
    ('TRANSPORTS_ROUTIERS', 'Transports routiers'),
    ('TRAVAUX_PUBLICS_ETAM', 'Travaux publics : ETAM'),
    ('TRAVAUX_PUBLICS_OUVRIERS', 'Travaux publics : Ouvriers'),
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
    
    # Nouveaux champs pour la conformité RGPD
    pii_report = models.JSONField(null=True, blank=True, verbose_name=_('Rapport PII (sans valeurs)'))
    minimal_extract = models.JSONField(null=True, blank=True, verbose_name=_('Extraction minimale'))
    redacted_pdf_path = models.CharField(max_length=512, null=True, blank=True, verbose_name=_('Chemin PDF masqué'))

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