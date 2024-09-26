from django.urls import path

from backend.certificates.views import certification_management, certification_transaction, certification_template, \
    print_certification, edit_certificate

urlpatterns = [
    path('', certification_management, name='certification_management'),
    path('transaction/<str:id_number>', certification_transaction, name='certification_transaction'),
    path('template/<int:pk>/<str:id_number>', certification_template, name='certification_template'),
    path('template/edit/<int:pk>', edit_certificate, name='edit_certificate'),
    path('print/<int:pk>', print_certification, name='print_certification'),
]