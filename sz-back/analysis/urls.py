from django.urls import path
from .views import PayslipAnalysisView, FullAnalysisResultView, BulkAnalysisUploadView, BulkAnalysisResultView

from .views import (
    PayslipAnalysisView, FullAnalysisResultView, BulkAnalysisUploadView, BulkAnalysisResultView,
    payslip_pii_report, payslip_minimal_extract, payslip_redacted_pdf
)

urlpatterns = [
    path('payslip/<int:payslip_id>/analyze/', PayslipAnalysisView.as_view(), name='payslip-analyze'),
    path('payslip/<int:payslip_id>/results/', FullAnalysisResultView.as_view(), name='payslip-analysis-results'),
    path('bulk/upload/', BulkAnalysisUploadView.as_view(), name='bulk-analysis-upload'),
    path('bulk/<int:analysis_id>/results/', BulkAnalysisResultView.as_view(), name='bulk-analysis-results'),
    
    # Nouveaux endpoints RGPD-compliant
    path('payslip/<int:payslip_id>/pii-report/', payslip_pii_report, name='payslip_pii_report'),
    path('payslip/<int:payslip_id>/extract.json', payslip_minimal_extract, name='payslip_minimal_extract'),
    path('payslip/<int:payslip_id>/redacted.pdf', payslip_redacted_pdf, name='payslip_redacted_pdf'),

]