from django.urls import path

from api.hrws.views import item_views,vest_view, intervention,covid_view,sweap_view,emp_assistance_view,health_profile_view, \
    sweap_gratuity_view, incident_report_view, sweap_membership_view, EmployeeInterventionDatabaseViews

urlpatterns = [
    path('sweap_membership_views/', sweap_membership_view.as_view(), name='sweap_membership_view'),
    path('stock_views/', item_views.as_view(), name='item_views'),
    path('vest_view/', vest_view.as_view(), name='vest_view'),
    path('intervention/', intervention.as_view(), name='intervention'),
    path('covid_view/',covid_view.as_view(), name='covid_view'),
    path('sweap_view/',sweap_view.as_view(),name='sweap_view'),
    path('emp_assistance_view/',emp_assistance_view.as_view(),name='emp_assistance_view'),
    path('health_profile_view/',health_profile_view.as_view(), name='health_profile_view'),
    path('sweap_gratuity_view/',sweap_gratuity_view.as_view(), name='sweap_gratuity_view'),
    path('incident_report_view/',incident_report_view.as_view(), name='incident_report_view'),
    path('intervention_database/',EmployeeInterventionDatabaseViews.as_view(), name='intervention_database'),

]