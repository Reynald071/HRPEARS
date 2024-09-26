from django.urls import path

from api.personnel.payroll.views import PayrollMovView

urlpatterns = [
    path('movs/', PayrollMovView.as_view(), name='api_payroll_mov')
]