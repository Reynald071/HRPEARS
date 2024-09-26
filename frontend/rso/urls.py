from django.urls import path

from frontend.rso.views import rso_attachment, rso_attachment_view

urlpatterns = [
    path('attachment/', rso_attachment, name='rso_attachment'),
    path('attachment/view/<str:pk>', rso_attachment_view, name='rso_attachment_view')
]