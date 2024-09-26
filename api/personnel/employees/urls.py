from django.urls import path

from api.personnel.employees.views import WorkExperienceViews, EmployeeAdminViews, SectionViews, IPCRViews, \
    IPCRDivisionViews, ServiceRecordViews, IPCREmpViews, PositionVacancyViews, JobApplicationViews

urlpatterns = [
    path('work-experience-sheet/', WorkExperienceViews.as_view(), name='api_wes'),
    path('view/all/', EmployeeAdminViews.as_view(), name='api_view_employeee'),
    path('section/list/', SectionViews.as_view(), name='api_section_list'),
    path('ipcr/', IPCRViews.as_view(), name='api_ipcr'),
    path('ipcr/division/', IPCRDivisionViews.as_view(), name='api_ipcr_division'),
    path('ipcr/emp/', IPCREmpViews.as_view(), name='api_ipcr_emp'),
    path('service-record/', ServiceRecordViews.as_view(), name='api_service_record'),
    path('positions/view/', PositionVacancyViews.as_view(), name='api_position_vacancy'),
    path('job-app/', JobApplicationViews.as_view(), name='api_job_app'),
]