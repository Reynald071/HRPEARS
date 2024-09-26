from django.urls import path

from api.personnel.transmittal.views import TransmittalView, TransmittalOldView, TransmittalEmployeeOldView, \
    TransmittalEmployeeView

urlpatterns = [
    path('', TransmittalView.as_view(), name='api_transmittal'),
    path('old/', TransmittalOldView.as_view(), name='api_transmittal_old'),
    path('employee/', TransmittalEmployeeView.as_view(), name='api_employee_transmittal'),
    path('employee/old/', TransmittalEmployeeOldView.as_view(), name='api_employee_transmittal_old')
]