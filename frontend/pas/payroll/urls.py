from django.urls import path

from frontend.pas.payroll.views import f_payroll_list, get_employee_payroll_list, \
    generate_user_payslip, payroll_details_content

urlpatterns = [
    path('payroll/list/', f_payroll_list, name='f_payroll_list'),
    path('payroll/list/employee/<int:year>', get_employee_payroll_list, name='get_employee_payroll_list'),
    path('payroll/details/content/<str:pk>', payroll_details_content, name='payroll_details_content'),
    path('payroll/payslip/', generate_user_payslip, name='generate_user_payslip')
]