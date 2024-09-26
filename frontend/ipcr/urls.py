from django.urls import path

from frontend.ipcr.views import f_ipcr

urlpatterns = [
    path('', f_ipcr, name='f_ipcr')
]