from django.urls import path

from backend.pas.document_tracking.views import document_tracking, document_details

urlpatterns = [
    path('tracking/', document_tracking, name='document_tracking'),
    path('details/<int:pk>', document_details, name='document_details'),
]