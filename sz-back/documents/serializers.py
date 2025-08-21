from rest_framework import serializers
from .models import PaySlip
import os
from django.core.exceptions import ValidationError

# --- Validateurs ---
def validate_file_extension(value):
    """Vérifie que l'extension du fichier est .pdf."""
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Format de fichier non supporté. Seuls les PDF sont acceptés.')

def validate_file(value):
    """Vérifie la taille du fichier et confirme l'extension (redondant mais sûr)."""
    # Vérification de la taille (ex: 5MB)
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Le fichier est trop volumineux (max 5MB).")
    # Double vérification de l'extension
    if not value.name.lower().endswith('.pdf'):
        raise ValidationError("Seuls les fichiers PDF sont acceptés.")

# --- Sérialiseur pour PaySlip ---
class PaySlipSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle PaySlip (upload et affichage liste)."""
    # Appliquer les validateurs au champ du fichier uploadé
    uploaded_file = serializers.FileField(
        validators=[validate_file_extension, validate_file],
        # write_only=True # Optionnel: si tu ne veux pas renvoyer le champ fichier dans les réponses GET
    )
    # Optionnel: Rendre le nom d'utilisateur lisible
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PaySlip
        # Inclure TOUS les champs, y compris les nouveaux
        fields = (
            'id',
            'user',                 # ID de l'utilisateur
            'user_username',        # Nom d'utilisateur (lecture seule)
            'uploaded_file',        # Pour l'upload
            'upload_date',
            'processing_status',
            'contractual_salary',
            'additional_details',
            'convention_collective',
            # Nouveaux champs
            'period',
            'net_salary',
            'employee_name',
        )
        # Champs qui ne peuvent pas être définis lors de la création/mise à jour via l'API
        read_only_fields = (
            'upload_date', 
            'processing_status', 
            'user',
            # Les nouveaux champs sont en lecture seule car ils sont remplis par l'analyse
            'period',
            'net_salary',
            'employee_name',
        )

    # La méthode create est correcte pour appeler full_clean
    def create(self, validated_data):
        # L'utilisateur est ajouté dans la vue (request.user), pas via le serializer directement
        # user = validated_data.pop('user') # Normalement géré dans la vue
        payslip = PaySlip(**validated_data)
        # Assigner l'utilisateur avant full_clean si nécessaire (dépend de la logique de la vue)
        # payslip.user = self.context['request'].user
        try:
            payslip.full_clean()  # Appelle les validateurs du modèle
        except ValidationError as e:
            # Remonter les erreurs de validation du modèle au serializer
            raise serializers.ValidationError(serializers.as_serializer_error(e))
        payslip.save()
        return payslip


# --- Sérialiseur étendu pour le Dashboard avec scores ---
class PaySlipDashboardSerializer(serializers.ModelSerializer):
    """Sérialiseur pour afficher les payslips avec les scores dans le dashboard."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    analysis_score = serializers.SerializerMethodField()
    conformity_score = serializers.SerializerMethodField()
    anomalies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PaySlip
        fields = (
            'id',
            'user_username',
            'uploaded_file',
            'upload_date',
            'processing_status',
            'period',
            'net_salary',
            'employee_name',
            'analysis_score',
            'conformity_score',
            'anomalies_count',
        )
    
    def get_analysis_score(self, obj):
        """Récupère le score global de l'analyse."""
        try:
            if hasattr(obj, 'analysis'):
                analysis_details = obj.analysis.analysis_details
                gpt_data = analysis_details.get('gpt_analysis', {})
                return gpt_data.get('note_globale', 0)
        except:
            pass
        return 0
    
    def get_conformity_score(self, obj):
        """Récupère le score de conformité de l'analyse."""
        try:
            if hasattr(obj, 'analysis'):
                analysis_details = obj.analysis.analysis_details
                gpt_data = analysis_details.get('gpt_analysis', {})
                return gpt_data.get('note_conformite_legale', 0)
        except:
            pass
        return 0
    
    def get_anomalies_count(self, obj):
        """Compte le nombre d'anomalies détectées."""
        try:
            if hasattr(obj, 'analysis'):
                analysis_details = obj.analysis.analysis_details
                gpt_data = analysis_details.get('gpt_analysis', {})
                anomalies = gpt_data.get('anomalies_potentielles_observees', [])
                return len(anomalies)
        except:
            pass
        return 0

    # Optionnel: Ajouter une méthode update si tu permets la modification
    # def update(self, instance, validated_data):
    #     # ... logique de mise à jour ...
    #     return super().update(instance, validated_data)