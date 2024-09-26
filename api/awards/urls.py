from django.urls import path

from api.awards.views import AwGuidelinesViews

urlpatterns = [
    path('guidelines/', AwGuidelinesViews.as_view(), name='api_aw_guidelines')
]