from django.urls import path

from api.personnel.dtr.views import DTRTimeViews

urlpatterns = [
    path('time/logs/', DTRTimeViews.as_view(), name='time_logs')
]