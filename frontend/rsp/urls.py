from django.urls import path

from frontend.rsp.views import rso_for_assignment, rso_for_assignment_layout, intro_letter, intro_letter_layout, \
    intro_letter_data, generate_drn_for_intro_letter, intro_letter_print

urlpatterns = [
    path('special-order/assignment/', rso_for_assignment, name='rso_for_assignment'),
    path('special-order/assignment/layout/<str:employee_id>', rso_for_assignment_layout, name='rso_for_assignment_layout'),
    path('intro-letter/', intro_letter, name='intro_letter'),
    path('intro-letter/data/<str:employee_id>', intro_letter_data, name='intro_letter_data'),
    path('intro-letter/layout/<str:employee_id>', intro_letter_layout, name='intro_letter_layout'),
    path('intro-letter/generate/drn/<int:io_id>', generate_drn_for_intro_letter, name='generate_drn_for_intro_letter'),
    path('intro-letter/print/<int:io_id>', intro_letter_print, name='intro_letter_print')
]