from django.urls import path

from api.personnel.tr_hazard.views import HazardReportView, HazardReportAnnexBView

urlpatterns = [
    path('annex-a/', HazardReportView.as_view(), name='api_hazard_annex_a'),
    path('annex-b/', HazardReportAnnexBView.as_view(), name='api_hazard_annex_b')
]
