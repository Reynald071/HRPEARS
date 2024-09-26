from django.urls import path

from api.lds.views import LdsRsoViews, LdsRsoViewsAdmin, LdsParticipantsViews, LdsFacilitatorsViews, LdsIDPViews

urlpatterns = [
    path('', LdsRsoViews.as_view(), name='api_lds_rso'),
    path('participants/', LdsParticipantsViews.as_view(), name='api_lds_participants'),
    path('facilitators/', LdsFacilitatorsViews.as_view(), name='api_lds_facilitators'),
    path('admin/', LdsRsoViewsAdmin.as_view(), name='api_lds_rso_admin'),
    path('idp/', LdsIDPViews.as_view(), name='api_lds_idp')
]