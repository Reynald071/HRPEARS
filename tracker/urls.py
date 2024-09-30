from django.urls import path

from tracker.views import tracker, leave_tracker, ship_documents, track_package, \
    track_package_details, track_package_received, track_package_forwarded, track_package_for_file, track_inbox, \
    track_for_return, return_document_package, dtr_tracker, print_transmittal, ctdo_tracker, \
    tracker_item, add_leave_employee, add_leave_employee_within_month, add_ctdo_employee_within_month, \
    add_ctdo_employee, track_package_cc, track_carbon_copy, remove_draft, tracker_announcements, \
    edit_tracker_announcements

urlpatterns = [
    path('', tracker, name='tracker'),
    path('announcements/', tracker_announcements, name='tracker_announcements'),
    path('announcements/update/<int:pk>', edit_tracker_announcements, name='edit_tracker_announcements'),
    path('remove/draft/', remove_draft, name='remove_draft'),
    path('documents/ship/', ship_documents, name='ship_documents'),
    path('ctdo/', ctdo_tracker, name='ctdo_tracker'),
    path('dtr/', dtr_tracker, name='dtr_tracker'),
    path('leave/', leave_tracker, name='leave_tracker'),
    path('leave/add/employee/', add_leave_employee, name='add_leave_employee'),
    path('leave/add/employee/within/month', add_leave_employee_within_month, name='add_leave_employee_within_month'),
    path('ctdo/add/employee/', add_ctdo_employee, name='add_ctdo_employee'),
    path('ctdo/add/employee/within/month', add_ctdo_employee_within_month, name='add_ctdo_employee_within_month'),
    path('print/transmittal/<str:pk>', print_transmittal, name='print_transmittal'),
    path('inbox/', track_inbox, name='track_inbox'),
    path('item/', tracker_item, name='tracker_item'),
    path('carbon-copy/', track_carbon_copy, name='track_carbon_copy'),
    path('package/', track_package, name='track_package'),
    path('package/cc/<str:pk>', track_package_cc, name='track_package_cc'),
    path('package/details/<str:pk>', track_package_details, name='track_package_details'),
    path('package/transaction/received/', track_package_received, name='track_package_received'),
    path('package/transaction/forwarded/<str:pk>', track_package_forwarded, name='track_package_forwarded'),
    path('package/transaction/for-file/', track_package_for_file, name='track_package_for_file'),
    path('package/transaction/for-return/<str:pk>', track_for_return, name='track_for_return'),
    path('package/transaction/return-documents', return_document_package, name='return_document_package')
]