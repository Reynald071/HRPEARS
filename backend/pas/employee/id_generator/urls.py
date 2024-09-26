from django.urls import path

from backend.pas.employee.id_generator.views import id_generator, print_id, id_generate_employee_list, print_id_custom

urlpatterns = [
    path('', id_generator, name='id_generator'),
    path('print/<str:section_id>/<str:aoa_id>', print_id, name='print_id'),
    path('print/custom/', print_id_custom, name='print_id_custom'),
    path('generate/employee/', id_generate_employee_list, name='id_generate_employee_list')
]
