from django.urls import path

from backend.pas.employee.file_uploading.views import file_uploading, file_uploading_content, file_uploading_delete, \
    file_uploading_update, file_uploading_multiple, file_uploading_delete_all, file_uploading_delete_marked

urlpatterns = [
    path('', file_uploading, name='file_uploading'),
    path('<str:employee_id_number>', file_uploading_content, name='file_uploading_content'),
    path('delete/', file_uploading_delete, name='file_uploading_delete'),
    path('update/', file_uploading_update, name='file_uploading_update'),
    path('multiple/', file_uploading_multiple, name='file_uploading_multiple'),
    path('delete/all/', file_uploading_delete_all, name='file_uploading_delete_all'),
    path('delete/marked/', file_uploading_delete_marked, name='file_uploading_delete_marked')
]