from django.urls import path
from .views import PayslipAnalysisView, FullAnalysisResultView, BulkAnalysisUploadView, BulkAnalysisResultView

urlpatterns = [
    path('payslip/<int:payslip_id>/analyze/', PayslipAnalysisView.as_view(), name='payslip-analyze'),
    path('payslip/<int:payslip_id>/results/', FullAnalysisResultView.as_view(), name='payslip-analysis-results'),
    path('bulk/upload/', BulkAnalysisUploadView.as_view(), name='bulk-analysis-upload'),
    path('bulk/<int:analysis_id>/results/', BulkAnalysisResultView.as_view(), name='bulk-analysis-results'),

]