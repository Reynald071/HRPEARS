from django.urls import path

from .views import PayslipViews


urlpatterns = [
    path('payslip/', PayslipViews.as_view(), name='api_payslip'),
]
