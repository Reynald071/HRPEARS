from django.urls import path

from backend.pas.service_record.views import service_record, generate_service_record, generate_sr_template, \
    edit_sr_workhistory, add_sr_workhistory, generate_drn_for_service_record, print_service_record, \
    delete_service_record_data

urlpatterns = [
    path('', service_record, name='service_record'),
    path('data/<str:employee_name>', generate_service_record, name='generate_service_record'),
    path('template/<str:employee_name>', generate_sr_template, name='generate_sr_template'),
    path('add/<str:id_number>', add_sr_workhistory, name='add_sr_workhistory'),
    path('edit/<int:pk>', edit_sr_workhistory, name='edit_sr_workhistory'),
    path('delete/<int:pk>', delete_service_record_data, name='delete_service_record_data'),
    path('generate-drn/<int:sr_id>', generate_drn_for_service_record, name='generate_drn_for_service_record'),
    path('print/<int:pk>', print_service_record, name='print_service_record')
]