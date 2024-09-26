from django.urls import path

from backend.lds.views import ld_admin, generate_drn_for_rso, bypass_lds_rso_approval, \
    bypass_lds_rrso_approval

urlpatterns = [
    path('', ld_admin, name='ld_admin'),
    path('rrso/bypass-approval/<int:pk>', bypass_lds_rrso_approval, name='bypass_lds_rrso_approval'),
    path('rso/bypass-approval/<int:pk>', bypass_lds_rso_approval, name='bypass_lds_rso_approval'),
    path('generate/rso/', generate_drn_for_rso, name='generate_drn_for_rso'),
]