from django.urls import path

from landing.views import home, landing_issuances, landing_issuances_files, get_subcategories, add_request, \
    get_categories, get_impacts, get_urgencies, send_message, announcement_layout, job_application, show_city,\
    show_brgy, job_vacancies, vacancy_details, check_captcha, app_success, app_tracking

urlpatterns = [
    path('', home, name='home'),
    path('announcement/view/', announcement_layout, name='announcement_layout'),
    path('send-message/', send_message, name='send_message'),
    path('issuances/', landing_issuances, name='landing_issuances'),
    path('issuances/files/<str:pk>', landing_issuances_files, name='landing_issuances_files'),
    path('support/get/categories/', get_categories, name='get-categories'),
    path('support/get/impacts/', get_impacts, name='get-impacts'),
    path('support/get/urgencies/', get_urgencies, name='get-urgencies'),
    path('support/get/subcategories/<int:pk>', get_subcategories, name='get-subcategories'),
    path('support/request/add/', add_request, name='add-support-request'),
    path('job-vacancies/', job_vacancies, name='job_vacancies'),
    path('vacancy/details/<str:pk>', vacancy_details, name='vacancy_details'),
    path('application/<str:pk>', job_application, name='job_application'),
    path('application/show-city/<str:prov_code>', show_city, name='app_show_city'),
    path('application/show-brgy/<str:city_code>', show_brgy, name='app_show_brgy'),
    path('application/check-captcha/', check_captcha, name='check_captcha'),
    path('application/success/<str:tracking_no>', app_success, name='app_success'),
    path('application/tracking/', app_tracking, name='app_tracking'),
]