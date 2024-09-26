from django.urls import path

from frontend.pas.tr_hazard.views import tr_hazard, print_tr_hazard, edit_tr_hazard, tr_hazard_annex_b, \
    print_tr_hazard_annex_b, locked_travel_annex_a

urlpatterns = [
    path('annex-a/', tr_hazard, name='tr_hazard'),
    path('annex-a/edit/<int:pk>', edit_tr_hazard, name='edit_tr_hazard'),
    path('annex-a/locked/', locked_travel_annex_a, name='locked_travel_annex_a'),
    path('annex-a/print/<str:start_date>/<str:end_date>', print_tr_hazard, name='print_tr_hazard'),
    path('annex-b/', tr_hazard_annex_b, name='tr_hazard_annex_b'),
    path('annex-b/print/<str:start_date>/<str:end_date>', print_tr_hazard_annex_b, name='print_tr_hazard_annex_b')
]