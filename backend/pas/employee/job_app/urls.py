from django.urls import path

from .views import job_app, application_detail, app_totals, vacancy_detail, approve_application, reject_application,\
    remarks


urlpatterns = [
    path('', job_app, name="job_app_backend"),
    path('view/<str:pk>', application_detail, name="application_detail"),
    path('vacancy/view/<str:pk>', vacancy_detail, name="app_vacancy_detail"),
    path('totals/', app_totals, name="job_app_totals"),
    path('approve-app/', approve_application, name="approve_application"),
    path('reject-app/', reject_application, name="reject_application"),
    path('remarks/<str:pk>', remarks, name="app_remarks"),
]
