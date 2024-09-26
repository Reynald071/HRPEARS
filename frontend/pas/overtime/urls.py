from django.urls import path

from frontend.pas.overtime.views import overtime_requests, overtime_save_as_draft, move_overtime_draft, \
    overtime_request_submit, print_ot_request

urlpatterns = [
    path('request/', overtime_requests, name='overtime_requests'),
    path('save-as-draft/', overtime_save_as_draft, name='overtime_save_as_draft'),
    path('move-to-requests/<str:pk>', move_overtime_draft, name='move_overtime_draft'),
    path('submit/', overtime_request_submit, name='overtime_request_submit'),
    path('request/print/<str:pk>', print_ot_request, name='print_ot_request')
]