from django.urls import path

from api.personnel.overtime.views import OvertimeDetailsView, OvertimeView

urlpatterns = [
    path('', OvertimeView.as_view(), name='api_overtime'),
    path('details/', OvertimeDetailsView.as_view(), name='api_overtime_details'),
]