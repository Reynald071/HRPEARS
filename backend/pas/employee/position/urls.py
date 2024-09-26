from django.urls import path

from backend.pas.employee.position.views import position_status, get_position_totals, submit_position, delete_position,\
    edit_position, vacancy_attachment


urlpatterns = [
    path('status/', position_status, name="position_status"),
    path('status/total/', get_position_totals, name="get_position_totals"),
    path('submit/', submit_position, name="submit_position"),
    path('delete/', delete_position, name="delete_position"),
    path('edit/<int:pk>', edit_position, name="edit_position"),
    path('attachment/<int:pk>', vacancy_attachment, name="vacancy_attachment"),
]
