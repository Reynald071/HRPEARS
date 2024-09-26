from django.urls import path

from backend.pas.employee.staffing.views import employee_staffing, os_template_d, os_template_c

urlpatterns = [
    path('', employee_staffing, name='employee_staffing'),
    path('os-template-c/', os_template_c, name='os_template_c'),
    path('os-template-d/', os_template_d, name='os_template_d')
]