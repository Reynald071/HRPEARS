from django.urls import path

from api.personnel.endorsement.views import EndorsementView, EndorsementPeopleView

urlpatterns = [
    path('', EndorsementView.as_view(), name='api_endorsement'),
    path('employee/', EndorsementPeopleView.as_view(), name='api_endorsement_people'),
]