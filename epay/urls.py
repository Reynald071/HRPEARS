from django.urls import path

from epay.views import epay_home, manage_payroll_employee, remove_payroll_employee, payroll_sent_notification, \
    view_payroll_sent_logs, bulk_send_payroll_notification, view_employee_payroll_details, view_employee_ctdo_requests, \
    view_employee_leave_application, payroll_monitoring, view_employee_travel_history, payroll_monitoring_view, \
    payroll_workflow, script_for_auto_add_employee_on_payroll_incharge, view_payroll_workflow_detail, \
    view_payroll_tracker, add_payroll_timeline_comments, payroll_mark_hold, payroll_unmark_hold

urlpatterns = [
    path('', epay_home, name='epay_home'),
    path('manage/employee/', manage_payroll_employee, name='manage_payroll_employee'),
    path('view/employee/details/<int:pk>', view_employee_payroll_details, name='view_employee_payroll_details'),
    path('view/employee/ctdo/all/<str:pk>', view_employee_ctdo_requests, name='view_employee_ctdo_requests'),
    path('view/employee/leave/all/<str:pk>', view_employee_leave_application, name='view_employee_leave_application'),
    path('view/employee/travel-history/all/<str:pk>', view_employee_travel_history, name='view_employee_travel_history'),
    path('manage/employee/remove/', remove_payroll_employee, name='remove_payroll_employee'),
    path('manage/employee/sent/notification/', payroll_sent_notification, name='payroll_sent_notification'),
    path('manage/employee/sent/notification/logs/', view_payroll_sent_logs, name='view_payroll_sent_logs'),
    path('manage/employee/sent/notification/bulk/', bulk_send_payroll_notification, name='bulk_send_payroll_notification'),
    path('manage/payroll/monitoring/', payroll_monitoring, name='payroll_monitoring'),
    path('manage/payroll/monitoring/view/<str:start_date>/<str:end_date>', payroll_monitoring_view, name='payroll_monitoring_view'),
    path('manage/payroll/workflow/', payroll_workflow, name='payroll_workflow'),
    path('manage/payroll/workflow/detail/<int:pk>', view_payroll_workflow_detail, name='view_payroll_workflow_detail'),
    path('manage/payroll/tracker/<str:dv_no>', view_payroll_tracker, name='epay_view_payroll_tracker'),
    path('manage/payroll/tracker/add-comments/<str:dv_no>', add_payroll_timeline_comments, name='add_payroll_timeline_comments'),
    path('manage/payroll/hold/<str:dv_no>', payroll_mark_hold, name='payroll_mark_hold'),
    path('manage/payroll/hold/unmark/<str:dv_no>', payroll_unmark_hold, name='payroll_unmark_hold')
#    path('script/run/auto/employee/add/', script_for_auto_add_employee_on_payroll_incharge, name='script_for_auto_add_employee_on_payroll_incharge')
]