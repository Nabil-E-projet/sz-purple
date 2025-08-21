from rest_framework import serializers
from .models import PayslipAnalysis, BulkAnalysisGroup, BulkAnalysisItem


class PayslipAnalysisSerializer(serializers.ModelSerializer):
    """Sérialiseur pour afficher les résultats de l'analyse."""

    # Afficher l'ID de la fiche de paie associée
    payslip_id = serializers.ReadOnlyField(source='payslip.id')

    # Optionnel: Si tu veux afficher plus de détails sur la fiche de paie associée
    # Décommenter la ligne d'import ci-dessus et la ligne suivante
    # payslip = PaySlipSerializer(read_only=True)

    class Meta:
        model = PayslipAnalysis
        fields = [
            'id',
            'payslip_id', # ID de la fiche de paie liée
            # 'payslip', # Décommenter si tu utilises le serializer imbriqué
            'analysis_date',
            'analysis_status',
            'analysis_details', # Le JSON complet retourné par GPT Vision
        ]
        # Ces champs sont définis par le système, pas par l'utilisateur via l'API
        read_only_fields = ('analysis_date', 'analysis_status', 'analysis_details', 'payslip_id')


class BulkAnalysisItemSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les items d'une analyse groupée."""
    payslip_id = serializers.ReadOnlyField(source='payslip.id')
    period = serializers.ReadOnlyField(source='payslip.period')
    status = serializers.ReadOnlyField(source='payslip.processing_status')
    
    class Meta:
        model = BulkAnalysisItem
        fields = ['id', 'payslip_id', 'order', 'period', 'status']

class BulkAnalysisGroupSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les groupes d'analyse."""
    items = BulkAnalysisItemSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkAnalysisGroup
        fields = [
            'id', 'name', 'convention_collective', 'status', 
            'created_at', 'total_files', 'processed_files',
            'total_amount_due', 'missing_benefits', 'summary',
            'items', 'progress_percentage'
        ]
    
    def get_progress_percentage(self, obj):
        if obj.total_files == 0:
            return 0
        return int((obj.processed_files / obj.total_files) * 100)