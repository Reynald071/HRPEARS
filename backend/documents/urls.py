from django.urls import path

from backend.documents.views import documents_201_files, upload_201_documents, delete_201_file_upload, issuances, \
    upload_issuances, delete_issuances_file_upload, update_201_files, documents_201_content, \
    upload_multiple_201_documents, delete_all_201_documents, delete_multiple_201_documents

urlpatterns = [
    path('201-files/', documents_201_files, name='documents_201_files'),
    path('201-files/content/<str:employee_id_number>', documents_201_content, name='documents_201_content'),
    path('upload-201-files/', upload_201_documents, name='upload_201_documents'),
    path('upload-201-files/multiple/', upload_multiple_201_documents, name='upload_multiple_201_documents'),
    path('delete-all/files/', delete_all_201_documents, name='delete_all_201_documents'),
    path('201-files/edit/', update_201_files, name='update_201_files'),
    path('delete-201-file-upload/', delete_201_file_upload, name='delete_201_file_upload'),
    path('delete-201-files/multiple/', delete_multiple_201_documents, name='delete_multiple_201_documents'),
    path('issuances/', issuances, name='issuances'),
    path('upload-issuances-files/<int:type_id>', upload_issuances, name='upload_issuances'),
    path('delete-issuances-file-upload/', delete_issuances_file_upload, name='delete_issuances_file_upload'),
]