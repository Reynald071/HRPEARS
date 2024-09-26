from django.urls import path

from api.personnel.travel.views import TravelHistoryView, TravelDetailsView, TravelView, TravelAdminView

urlpatterns = [
    path('history/', TravelHistoryView.as_view(), name='api_travel_history'),
    path('details/requests/', TravelDetailsView.as_view(), name='api_travel_details'),
    path('', TravelView.as_view(), name='api_travel'),
    path('admin/', TravelAdminView.as_view(), name='api_travel_admin')
]