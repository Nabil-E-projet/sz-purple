from django.urls import path
from .views import PayslipAnalysisView, FullAnalysisResultView, BulkAnalysisUploadView, BulkAnalysisResultView, RecalculateScoresView

urlpatterns = [
    path('payslip/<int:payslip_id>/analyze/', PayslipAnalysisView.as_view(), name='payslip-analyze'),
    path('payslip/<int:payslip_id>/results/', FullAnalysisResultView.as_view(), name='payslip-analysis-results'),
    path('payslip/<int:payslip_id>/recalculate-scores/', RecalculateScoresView.as_view(), name='recalculate-scores'),
    path('bulk/upload/', BulkAnalysisUploadView.as_view(), name='bulk-analysis-upload'),
    path('bulk/<int:analysis_id>/results/', BulkAnalysisResultView.as_view(), name='bulk-analysis-results'),

]