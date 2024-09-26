from django.urls import path, include

from api.announcement.views import AnnouncementView
from api.birthday.views import BirthdayView
from api.directory_list.views import DirectoryListView
from api.grievance.views import GrievanceView
from api.personnel.tev.views import TevTrackerView
from api.personnel.views import RitoDetailsView, EmployeeDetailsView, \
    MOTView, RitoPeopleView, UpdateTravelMOTView, PositionView, SearchEmployeeView, LeaveDetailsView, \
    EmployeeDetailsLoadView
from api.views import PortalConfigViews, PermissionViews, RestFrameworkTrackingApirequestlogViews, UserPermissionViews, \
    SMSViews, FeedbackViews, api_send_sms, SMSUserView, PatchesViews, ConvocationEventViews, PortalSuccessLogsViews

urlpatterns = [
    path('dtr/', include('api.personnel.dtr.urls')),
    path('portal/success/logs/', PortalSuccessLogsViews.as_view(), name='api_portal_success_logs'),
    path('recruitment-selection-and-placement/', include('api.rsp.urls')),
    path('employees/', include('api.personnel.employees.urls')),
    path('documents/', include('api.documents.urls')),
    path('leave/', include('api.personnel.leave.urls')),
    path('certificates/', include('api.certificates.urls')),
    path('infimos/', include('api.infimos.urls')),
    path('help-desk/', include('api.help_desk.urls')),
    path('overtime/', include('api.personnel.overtime.urls')),
    path('document/tracking/', include('api.tracking.urls')),
    path('payroll/', include('api.personnel.payroll.urls')),
    path('sms/', SMSViews.as_view(), name='api_sms'),
    path('sms/user/', SMSUserView.as_view(), name='api_sms_user'),
    path('feedback/', FeedbackViews.as_view(), name='api_feedback'),
    path('announcements/', AnnouncementView.as_view(), name='api_announcement'),
    path('grievances/', GrievanceView.as_view(), name='api_grievances'),
    path('directory/list/', DirectoryListView.as_view(), name='api_directory_list'),
    path('configuration/', PortalConfigViews.as_view(), name='api_configuration'),
    path('permissions/', PermissionViews.as_view(), name='api_permissions'),
    path('permissions/user/', UserPermissionViews.as_view(), name='api_user_permissions'),
    path('requests/logs/', RestFrameworkTrackingApirequestlogViews.as_view(), name='api_logs'),
    path('patch-notes/', PatchesViews.as_view(), name='api_patch_notes'),
    path('leave/details/', LeaveDetailsView.as_view(), name='api_leave_details'),
    path('means-of-transportation/', MOTView.as_view(), name='api_hr_mot'),
    path('tev/tracker/', TevTrackerView.as_view(), name='api_tev_tracker'),
    path('travel/', include('api.personnel.travel.urls')),
    path('travel/details/', RitoDetailsView.as_view(), name='api_rito_details'),
    path('travel/details/people/', RitoPeopleView.as_view(), name='api_rito_people'),
    path('travel/details/update/', UpdateTravelMOTView.as_view(), name='api_update_travel_mot'),
    path('position/list/', PositionView.as_view(), name='api_position'),
    path('employee/list/', EmployeeDetailsView.as_view(), name='api_employee_list'),
    path('employee/list/load/', EmployeeDetailsLoadView.as_view(), name='api_employee_list_load'),
    path('employee/list/search/', SearchEmployeeView.as_view(), name='api_search_employee'),
    path('send-message/', api_send_sms, name='api_send_sms'),
    path('convocation/event/', ConvocationEventViews.as_view(), name='api_convocation_event'),
    path('hrws/', include('api.hrws.urls')),
    path('transmittal/', include('api.personnel.transmittal.urls')),
    path('learning-and-development/', include('api.lds.urls')),
    path('awards/', include('api.awards.urls')),
    path('endorsement/', include('api.personnel.endorsement.urls')),
    path('tr-hazard/', include('api.personnel.tr_hazard.urls')),
    path('birthday/', BirthdayView.as_view(), name='api_birthday'),
    path('payroll-new/', include('api.payroll_new.urls')),
]