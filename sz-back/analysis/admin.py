from django.contrib import admin
from .models import PayslipAnalysis

@admin.register(PayslipAnalysis)
class PayslipAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'payslip', 'analysis_date', 'analysis_status')
    list_filter = ('analysis_status', 'analysis_date')
    search_fields = ('payslip__user__username',) # Modifié ici
    readonly_fields = ('analysis_date',)