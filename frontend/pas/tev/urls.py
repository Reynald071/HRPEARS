from django.urls import path

from frontend.pas.tev.views import track_tev

urlpatterns = [
    path('', track_tev, name='track_tev')
]