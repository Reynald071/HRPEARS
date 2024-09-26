from django.urls import path

from api.rsp.views import RSPIntroLetterView

urlpatterns = [
    path('intro-letter/', RSPIntroLetterView.as_view(), name='api_rsp_intro_letter')
]