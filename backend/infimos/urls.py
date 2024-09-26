from django.urls import path

from backend.infimos.views import infimos_beta, infimos_beta_view, view_payroll_tracker, view_payroll_workflow

urlpatterns = [
    path('', infimos_beta, name='infimos_beta'),
    path('edit/<str:year>/<str:dv_no>', infimos_beta_view, name='infimos_beta_view'),
    path('view/payroll/<str:dv_no>', view_payroll_tracker, name='view_payroll_tracker'),
    path('view/payroll/workflow/<int:timeline>/<str:dv_no>', view_payroll_workflow, name='view_payroll_workflow')
]