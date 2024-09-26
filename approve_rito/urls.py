from django.urls import path, include
from approve_rito.views import approve_rito_home, TravelSupervisorView

urlpatterns = [
    path('', approve_rito_home, name='approve_rito_home'),
    path('supervisor/', TravelSupervisorView.as_view(), name='travel_supervisor'),
]
