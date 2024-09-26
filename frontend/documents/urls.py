from django.urls import path

from frontend.documents.views import files_201, display_201_files, files_sop, display_sop_files, upload_user_document, \
    delete_user_file_upload

urlpatterns = [
    path('display-201-files/<str:hash_type>', display_201_files, name='display_201_files'),
    path('201-files/upload/', upload_user_document, name='upload_user_document'),
    path('201-files/delete/', delete_user_file_upload, name='delete_user_file_upload'),
    path('sop-files/', files_sop, name='files-sop'),
    path('display-sop-files/<int:type_id>', display_sop_files, name='display_sop_files'),
]