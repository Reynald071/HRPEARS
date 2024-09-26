from django.urls import path

from backend.pas.endorsement.views import endorsement, endorsement_details, edit_endorsement_details, \
    print_endorsement_details, get_employee_details_on_endorsement, view_shortlisted, page_shortlisted

urlpatterns = [
    path('', endorsement, name='endorsement'),
    path('shortlisted/view/', view_shortlisted, name='view_shortlisted'),
    path('shorlisted/', page_shortlisted, name='page_shortlisted'),
    path('details/<int:pk>', endorsement_details, name='endorsement_details'),
    path('details/edit/<int:pk>', edit_endorsement_details, name='edit_endorsement_details'),
    path('details/print/<int:pk>', print_endorsement_details, name='print_endorsement_details'),
    path('employee/details/', get_employee_details_on_endorsement, name='get_employee_details_on_endorsement')
]