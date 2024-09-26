from django.urls import path
from backend.pas.employee.views import update_personal_information, update_family_background, show_children, \
    update_educational_background, add_school, add_degree, add_honor, update_civil_service, add_eligibility, \
    update_work_experience, add_position, update_voluntary_work, add_org, update_trainings, add_trainingtitle, \
    update_others, add_hobbies, add_recog, update_additional_information, update_reference, registered_dtr_pin, \
    ad_account_creation

urlpatterns = [
    path('personal-information/<int:pi_id>', update_personal_information, name='update_personal_information'),
    path('family-background/<int:pi_id>', update_family_background, name='update_family_background'),
    path('educational-background/<int:pi_id>', update_educational_background, name='update_educational_background'),
    path('add-school/<int:pi_id>', add_school, name='admin_add_school'),
    path('add-degree/<int:pi_id>', add_degree, name='admin_add_degree'),
    path('add-honor/<int:pi_id>', add_honor, name='admin_add_honor'),
    path('civil-service/<int:pi_id>', update_civil_service, name='update_civil_service'),
    path('add-eligibility/<int:pi_id>', add_eligibility, name='admin_add_eligibility'),
    path('work-experience/<int:pi_id>', update_work_experience, name='update_work_experience'),
    path('add-position/<int:user_id>', add_position, name='admin_add_position'),
    path('voluntary-work/<int:pi_id>', update_voluntary_work, name='update_voluntary_work'),
    path('add-organization/<int:pi_id>', add_org, name='admin_add_org'),
    path('trainings/<int:pi_id>', update_trainings, name='update_trainings'),
    path('add-trainingtitle/<int:pi_id>', add_trainingtitle, name='admin_add_trainingtitle'),
    path('others/<int:pi_id>', update_others, name='update_others'),
    path('add-hobbies/<int:pi_id>', add_hobbies, name='admin_add_hobbies'),
    path('add-recog/<int:pi_id>', add_recog, name='admin_add_recog'),
    path('additional-information/<int:pi_id>', update_additional_information, name='update_additional_information'),
    path('reference/<int:pi_id>', update_reference, name='update_reference'),
    path('register/dtr/pin/', registered_dtr_pin, name='registered_dtr_pin'),
    path('active-directory-account/create/', ad_account_creation, name='ad_account_creation'),
]