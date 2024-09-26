from django.urls import path

from .payslip.views import payslip, payslip_detail


urlpatterns = [
    path('payslip/', payslip, name="payslip"),
    path('payslip/detail/<str:pk>', payslip_detail, name="payslip_detail"),
]
