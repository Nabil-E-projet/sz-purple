from django.contrib import admin
from .models import PaySlip

@admin.register(PaySlip)
class PaySlipAdmin(admin.ModelAdmin):
    list_display = ('user', 'processing_status', 'upload_date', 'period', 'employee_name', 'net_salary')
    list_filter = ('processing_status', 'upload_date')
    search_fields = ('user__username', 'user__email', 'convention_collective', 'period', 'employee_name')
    readonly_fields = ('upload_date',)