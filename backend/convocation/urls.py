from django.urls import path

from backend.convocation.views import convocation, convocation_generate_employee_list, convocation_print_qrcode, \
    convocation_attendance, received_qrcode_attendance, generate_convocation_report, shareable_convocation_link, \
    get_convocation_qr_link

urlpatterns = [
    path('', convocation, name='convocation'),
    path('generate/report/', generate_convocation_report, name='generate_convocation_report'),
    path('generate/employee-list/', convocation_generate_employee_list, name='convocation_generate_employee_list'),
    path('print/qr-code/<str:section_id>/<str:aoa_id>', convocation_print_qrcode, name='convocation_print_qrcode'),
    path('attendance/board/', convocation_attendance, name='convocation_attendance'),
    path('attendance/board/receiver/<str:pk>/<int:type>', received_qrcode_attendance, name='received_qrcode_attendance'),
    path('attendance/link/<str:pk>', shareable_convocation_link, name='shareable_convocation_link'),
    path('attendance/qr-code/<str:pk>', get_convocation_qr_link, name='get_convocation_qr_link')
]