from django.urls import path
from .views import PaySlipUploadView, PaySlipListView, PaySlipDetailView, PaySlipFileView, PaySlipDeleteView, ConventionCollectiveListView

urlpatterns = [
    path('upload/', PaySlipUploadView.as_view(), name='payslip-upload'),
    path('', PaySlipListView.as_view(), name='payslip-list'),
    path('<int:pk>/', PaySlipDetailView.as_view(), name='payslip-detail'),
    path('<int:pk>/file/', PaySlipFileView.as_view(), name='payslip-file'),
    path('<int:pk>/delete/', PaySlipDeleteView.as_view(), name='payslip-delete'),
    path('conventions/', ConventionCollectiveListView.as_view(), name='convention-list')

]