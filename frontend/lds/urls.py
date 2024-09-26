from django.urls import path

from backend.lds.views import print_rso
from frontend.lds.views import lds_rrso, training_details, print_rrso, add_training_participant, \
    add_training_facilitator, generate_certificate_participants, generate_certificate_facilitators, \
    tag_as_resource_person, remove_tag_as_resource_person, upload_ld_attachment, print_ld_attendance, \
    certificate_authenticity, delete_participants, delete_facilitator, generate_certificate_of_appearance, tag_as_group, \
    remove_tag_as_group, idp, update_idp_contents, remove_idp, view_idp_contents, duplicate_idp_contents, print_idp, \
    update_idp_details

urlpatterns = [
    path('requests/', lds_rrso, name='lds_rrso'),
    path('details/<int:pk>', training_details, name='training_details'),
    path('attachment/uploading/<int:pk>', upload_ld_attachment, name='upload_ld_attachment'),
    path('rso/print/<int:pk>', print_rso, name='print_rso'),
    path('rrso/print/<int:pk>', print_rrso, name='print_rrso'),
    path('participant/add/<int:pk>/<int:type>', add_training_participant, name='add_training_participant'),
    path('facilitator/add/<int:pk>/<int:type>', add_training_facilitator, name='add_training_facilitator'),
    path('attendance/print/<int:pk>', print_ld_attendance, name='print_ld_attendance'),
    path('resource-person/tagging/', tag_as_resource_person, name='tag_as_resource_person'),
    path('resource-person/tagging/remove/', remove_tag_as_resource_person, name='remove_tag_as_resource_person'),
    path('facilitator/group/tagging/', tag_as_group, name='tag_as_group'),
    path('facilitator/group/tagging/remove/', remove_tag_as_group, name='remove_tag_as_group'),
    path('participants/delete/', delete_participants, name='delete_participants'),
    path('facilitator/delete/', delete_facilitator, name='delete_facilitator'),
    path('certificate-authenticity/<str:pk_training>/<str:pk_id>', certificate_authenticity, name='certificate_authenticity'),
    path('individual-development-plan/', idp, name='idp'),
    path('individual-development-plan/edit/<int:pk>', update_idp_details, name='update_idp_details'),
    path('individual-development-plan/duplicate/', duplicate_idp_contents, name='duplicate_idp_contents'),
    path('individual-development-plan/print/<int:pk>', print_idp, name='print_idp'),
    path('individual-development-plan/view/<int:pk>', view_idp_contents, name='view_idp_contents'),
    path('individual-development-plan/update/<int:pk>', update_idp_contents, name='update_idp_contents'),
    path('individual-development-plan/delete/', remove_idp, name='remove_idp'),

    path('certificates/appearance/print/<int:pk>', generate_certificate_of_appearance,
         name='generate_certificate_of_appearance'),
    path('certificates/participants/print/<int:pk>', generate_certificate_participants,
         name='generate_certificate_participants'),
    path('certificates/facilitators/print/<int:pk>', generate_certificate_facilitators,
         name='generate_certificate_facilitators'),
]