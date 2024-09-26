from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from backend.views import login, logout, dashboard, birthday_celebrants, dtr_logs, save_information, \
    savehealth_checklist, health_checklist_data, export_healthchecklist, update_dtr_logs, delete_dtr_logs, \
    portal_updater, view_help_desk, assigned_employee, main_dashboard, statistics_dashboard, \
    issuances_dashboard, issuances_dashboard_view, add_additional_info, delete_additional_info, load_ticket_message, \
    get_help_desk_total, birthday_celebrants_view, leaderboards_dashboard, export_qr, print_drf, \
    delete_ticket_request, vacancies, reset_portal_account, test_user_login, update_request
from frontend.lds.views import email_confirmation_participants
from frontend.views import wfh_attendance, wfh_dtr, load_employees, \
    getemployeebyempid, profiles, get_attendance_status_for_today, forgot_password, forgot_password_code, \
    forgot_password_expire_code, set_new_password, resend_code, developer_update, load_employee_by_section, \
    load_employee_dtr, print_employee_dtr, get_employee_time_async, print_timerecordprinter, manage_dtr, \
    manage_dtr_layout, delete_dtr_assignee, load_employee_by_payroll_incharge

from portal.active_directory import get_user_attribute, get_password_countdown

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sms/notification/', include('frontend.birthday_greetings.urls')),
    path('convocation/', include('backend.convocation.urls')),
    path('id-generator/', include('backend.pas.employee.id_generator.urls')),
    path('email-confirmation/<str:rso_pk>/<str:emp_pk>', email_confirmation_participants, name='email_confirmation_participants'),
    path('developer-update/', developer_update, name='developer_update'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('forgot-password/code/reset/<str:token>', resend_code, name='resend_code'),
    path('forgot-password/code/<str:token>', forgot_password_code, name='forgot_password_code'),
    path('forgot-password/code/expired/<str:token>', forgot_password_expire_code, name='forgot_password_expire_code'),
    path('set-new-password/<str:token>', set_new_password, name='set_new_password'),
    path('backend/', include('backend.urls')),
    path('', include('frontend.urls')),
    path('', include('landing.urls')),
    path('profiles/<str:id_number>', profiles, name='profiles'),
    path('login/', login, name="backend-login"),
    path('logout', logout, name='backend-logout'),
    path('vacancies/', vacancies, name='vacancies'),
    path('birthday-celebrants/', birthday_celebrants, name='birthday_celebrants'),
    path('birthday-celebrants/view/<int:pk>', birthday_celebrants_view, name='birthday_celebrants_view'),
    path('dashboard/', dashboard, name="backend-dashboard"),
    path('dashboard/main/', main_dashboard, name='main_dashboard'),
    path('dashboard/statistics', statistics_dashboard, name='statistics_dashboard'),
    path('dashboard/issuances/', issuances_dashboard, name='issuances_dashboard'),
    path('dashboard/issuances/view/<int:type_id>', issuances_dashboard_view, name='issuances_dashboard_view'),
    path('dashboard/leaderboards/', leaderboards_dashboard, name='leaderboards_dashboard'),
    path('work-from-home/attendance/', wfh_attendance, name='wfh_attendance'),
    path('work-from-home/attendance/check/', get_attendance_status_for_today, name='get_attendance_status_for_today'),
    path('generate-dtr/', wfh_dtr, name='wfh_dtr'),
    path('load-employees/payroll-incharge/<int:pk>/<str:start_date>/<str:end_date>', load_employee_by_payroll_incharge, name='load_employee_by_payroll_incharge'),
    path('load-employees/section/<int:section_id>/<int:aoa_id>/<str:start_date>/<str:end_date>', load_employee_by_section, name='load_employee_by_section'),
    path('load-employees/dtr/<str:employee_name>/<str:start_date>/<str:end_date>', load_employee_dtr, name='load_employee_dtr'),
    path('load-employee/dtr/async/', get_employee_time_async, name='get_employee_time_async'),
    path('employee/dtr/print/<str:pk>/<str:start_date>/<str:end_date>', print_employee_dtr, name='print_employee_dtr'),
    path('employee/dtr/print/authorized/', print_timerecordprinter, name='print_timerecordprinter'),
    path('load-employees/', load_employees, name='load_employees'),
    path('get-employee-by-emp-id/<str:empid>', getemployeebyempid, name='get_employee_by_emp_id'),
    path('dtr-logs/', dtr_logs, name='dtr_logs'),
    path('dtr/manage/', manage_dtr, name='manage_dtr'),
    path('dtr/manage/layout/', manage_dtr_layout, name='manage_dtr_layout'),
    path('dtr/manage/delete/', delete_dtr_assignee, name='delete_dtr_assignee'),
    path('dtr-logs/update/', update_dtr_logs, name='update_dtr_logs'),
    path('dtr-logs/delete/', delete_dtr_logs, name='delete_dtr_logs'),
    path('save-information/', save_information, name='save_information'),
    path('save-checklist/', savehealth_checklist, name='save_checklist'),
    path('health-checklist/', health_checklist_data, name='health_checklist'),
    path('export-checklist/', export_healthchecklist, name='export-checklist'),
    path('welfare/', include('backend.welfare_intervention.intervention.urls')),
    path('active-directory/users/<str:username>', get_user_attribute, name='get_user_attribute'),
    path('active-directory/password/countdown/<str:username>', get_password_countdown, name='get_password_countdown'),
    path('system/', include('backend.settings.urls')),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('export-qr/', export_qr, name='export_qr'),
    path('portal/updates/', portal_updater, name='portal_updater'),
    path('help-desk/delete/', delete_ticket_request, name='delete_ticket_request'),
    path('help-desk/view/<int:pk>', view_help_desk, name='view_help_desk'),
    path('help-desk/update/<int:pk>', update_request, name='update_request'),
    path('help-desk/drf/print/<int:pk>', print_drf, name='print_drf'),
    path('help-desk/assigned-to/', assigned_employee, name='assigned_employee'),
    path('help-desk/message/<int:pk>', load_ticket_message, name='load_ticket_message'),
    path('help-desk/total/', get_help_desk_total, name='get_help_desk_total'),
    path('help-desk/services-info/add/<int:services_id>', add_additional_info, name='add_additional_info'),
    path('help-desk/services-info/delete', delete_additional_info, name='delete_additional_info'),
    path('certification/', include('backend.certificates.urls')),
    path('track/tev/', include('frontend.pas.tev.urls')),
    path('endorsement/', include('backend.pas.endorsement.urls')),
    path('rso/', include('frontend.rso.urls')),
    path('infimos/beta/', include('backend.infimos.urls')),
    path('support/', reset_portal_account, name='password_reset_multiple'),
    path('support/test/login/', test_user_login, name='test_user_login'),
    path('approve-rito/', include('approve_rito.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'backend.views.page_not_found'

