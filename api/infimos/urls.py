from django.urls import path

from api.infimos.views import Infimos20Views, Infimos21Views, Infimos22Views, Infimos23Views, InfimosHistoryViews, \
    InfimosViews

urlpatterns = [
    path('2020/', Infimos20Views.as_view(), name='api_infimos_2020'),
    path('2021/', Infimos21Views.as_view(), name='api_infimos_2021'),
    path('2022/', Infimos22Views.as_view(), name='api_infimos_2022'),
    path('2023/', Infimos23Views.as_view(), name='api_infimos_2023'),
    path('', InfimosViews.as_view(), name='api_infimos'),
    path('tracking/history/', InfimosHistoryViews.as_view(), name='api_infimos_tracking')
]