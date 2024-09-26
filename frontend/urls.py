from django.urls import path, include

from backend.directory.views import directory_list, delete_detail, contacts_search, directory_list_requests, \
    edit_directory_list
from backend.iso.views import delete_form
from backend.pas.clearance.views import view_clearance_layout_current
from backend.pas.employee.views import reset_password
from backend.views import ticket_request
from .announcements.views import announcements, delete_announcement
from .awards.views import awards, view_nominees, add_nominee, nominee_count, delete_nominee, edit_nominee, deliberation, \
    save_deliberation, view_awards, get_guidelines
from .documents.views import files_201
from .events.views import events, view_event, add_event, update_event, get_approval_id, get_has_permission_for_calendar, \
    save_event_approval, add_private_calendar, delete_event, revert_event_approval, calendar_sharing, share_calendar, \
    unshare_calendar, update_private_calendar, events_v2, get_all_events
from .ipcr.views import f_ipcr, emp_ipcr, emp_ipcr_details
from .leave.views import leave_application, get_leavespent, print_leaveapp, cancel_leave, ctdo_requests, print_ctdo, \
    cancel_ctdo, edit_leave_application, set_signature_leave, leave_after_print, ctdo_after_print, utilize_coc_earned, \
    coc_earned_content, delete_coc_utilization, auto_utilize_coc_earned, request_for_ctdo_cancellation, ctdo_add_remarks
from .grievance.views import grievances, view_grievance, update_grievance, get_grievance_overview, get_province_name, \
    get_grievance_latest_status
from .pas.outpass.views import outpass, outpass_update, print_outpass, filter_employee_except_me, \
    count_outpass_for_date, get_employee
from .pas.profile.views import my_profile, pds_pageone, pds_pagetwo, pds_pagethree, pds_pagefour, \
    about, activities, pds_pagefive, settings, change_password, travel_history, upload_cover_photo, social_media, \
    incase_of_emergency, view_transmittal, transmittal
from .pis.views import personal_info, show_brgy, family_background, show_children, remove_children, \
    educational_background, add_school, delete_education, add_degree, add_honor, show_city, civil_service, \
    delete_civil_service, \
    add_eligibility, work_experience, delete_workexperience, add_position, voluntary, delete_voluntary, add_org, \
    training, delete_training, others, delete_skills, delete_acad, delete_membership, add_hobbies, add_trainingtitle, \
    add_recog, additional_information, attachment, delete_reference, work_experience_sheet, write_wes, print_wes, \
    add_pds_course
from .pas.rito.views import rito, submit_rito, print_rito, delete_rito, draft_rito, delete_drafts, \
    cancel_travel_request, get_travel_totals, travel_undraft, get_vehicle_request_token, edit_rito, attachment_update,\
    view_tracking_details
from .tracking.views import document_tracking, view_document, sentbox, carboncopy, section_docs, get_section, \
    get_doctype, my_drn, view_document_blank, get_total_dt, delete_drn, get_division_and_section, my_drn_summary
from .views import downloadable_forms, submit_feedback, faqs, wfh_accomplishment, iso_forms, iso_forms_downloaded
from .pas.accomplishment.views import print_accomplishment, generateform, fetchaccomplishment, \
    print_dtr, accomplishment_report, get_accomplishment_report, set_signature_accomplishment, \
    clear_accomplishment_report, async_get_accomplishment_outputs

urlpatterns = [
    path('transmittal/', transmittal, name='my_transmittal'),
    path('view/transmittal/<int:pk>', view_transmittal, name='view_transmittal'),
    path('social-media/', social_media, name='social_media'),
    path('incase-of-emergency/', incase_of_emergency, name='incase_of_emergency'),
    path('upload-cover-photo/', upload_cover_photo, name='upload_cover_photo'),
    path('reset-password/<int:pk>', reset_password, name='reset_password'),
    path("show-city/", show_city, name="show-city"),
    path("show-brgy/", show_brgy, name="show-brgy"),
    path('show-children/', show_children, name='show-children'),
    path('remove-children/', remove_children, name='remove-children'),
    path('delete-education/', delete_education, name='delete-education'),
    path('add-school/', add_school, name="add-school"),
    path('add-degree/', add_degree, name='add-degree'),
    path('add-honor/', add_honor, name='add-honor'),
    path('delete-civil-service/', delete_civil_service, name='delete-civil-service'),
    path('add-eligibility/', add_eligibility, name='add-eligibility'),
    path('delete-workexperience/', delete_workexperience, name='delete-workexperience'),
    path('add-position/', add_position, name='add-position'),
    path('delete-voluntary/', delete_voluntary, name='delete-voluntary'),
    path('add-org/', add_org, name='add-org'),
    path('delete-training/', delete_training, name='delete-training'),
    path('add-trainingtitle/', add_trainingtitle, name='add-trainingtitle'),
    path('delete-skills/', delete_skills, name='delete-skills'),
    path('delete-nonacad/', delete_acad, name='delete-acad'),
    path('delete-membership/', delete_membership, name='delete-membership'),
    path('add-hobbies/', add_hobbies, name='add-hobbies'),
    path('add-recog/', add_recog, name='add-recog'),
    path('delete-reference/', delete_reference, name='delete-reference'),
    path('delete-rito/', delete_rito, name='delete-rito'),
    path('delete-drafts/<int:id>', delete_drafts, name='delete-drafts'),
    path('submit-rito/', submit_rito, name='submit-rito'),
    path('draft-rito/', draft_rito, name='draft-rito'),
    path('personnel/requests/travel/print/<int:pk>', print_rito, name='print-rito'),
    path('personnel/requests/travel/vehicle/request/print/', get_vehicle_request_token, name='get_vehicle_request_token'),
    path('get/travel/requests/totals/', get_travel_totals, name='get_travel_totals'),
    path('personnel/travel/requests/undraft/', travel_undraft, name='travel_undraft'),
    path('cancel-travel-request/', cancel_travel_request, name='cancel_travel_request'),
    path('attachment/travel/<str:tracking_no>', attachment_update, name='attachment_update'),
    path('tracking/travel-request/<str:pk>', view_tracking_details, name='view_tracking_details'),
    path('documents/downloadables/files/', downloadable_forms, name="downloadable-forms"),
    path('downloads/iso/', iso_forms, name="iso-forms-frontend"),
    path('downloads/iso/downloaded/', iso_forms_downloaded, name="iso-forms-downloaded"),
    path('request-outpass/', outpass, name='outpass'),
    path('update-outpass/<int:pk>', outpass_update, name='update-outpass'),
    path('print-outpass/<int:pk>', print_outpass, name='print-outpass'),
    path('filter-employee-except-me/', filter_employee_except_me, name='filter_employee_except_me'),
    path('documents/', include('frontend.documents.urls')),
    path('activities/', activities, name='activities'),
    path('settings/', settings, name='settings'),
    path('count-outpass/<str:mydate>/<str:id>', count_outpass_for_date, name='count-outpass'),
    path('get-employee/<str:id>', get_employee, name='get-employee'),
    path('submit-feedback/', submit_feedback, name='submit_feedback'),
    path('awards/deliberation/', deliberation, name='deliberation'),
    path('save-deliberation/', save_deliberation, name='save_deliberation'),
    path('awards/guidelines/get/<int:year>', get_guidelines, name='get_guidelines'),
    path('awards/nominations/', awards, name='nomination'),
    path('awards/view/<int:year>/<str:category>', view_awards, name='view_awards'),
    path('view-nominees/<int:pk>', view_nominees, name='view-nominees'),
    path('add-nominee/<int:pk>', add_nominee, name='add-nominee'),
    path('nominee-count/<int:pk>', nominee_count, name='nominee-count'),
    path('delete-nominee/<int:pk>', delete_nominee, name='delete-nominee'),
    path('edit-nominee/<int:pk>', edit_nominee, name='edit-nominee'),
    path('personnel/requests/ctdo/', ctdo_requests, name='ctdo_requests'),
    path('personnel/ctdo/cancellation/request/', request_for_ctdo_cancellation, name='request_for_ctdo_cancellation'),
    path('personnel/utilize/coc/auto/', auto_utilize_coc_earned, name='auto_utilize_coc_earned'),
    path('personnel/utilize/coc/<str:pk>', utilize_coc_earned, name='utilize_coc_earned'),
    path('personnel/utilize/coc/remove/', delete_coc_utilization, name='delete_coc_utilization'),
    path('personnel/coc/earned/', coc_earned_content, name='coc_earned_content'),
    path('personnel/requests/ctdo/cancel', cancel_ctdo, name='cancel_ctdo'),
    path('personnel/requests/ctdo/print/<int:pk>', print_ctdo, name='print_ctdo'),
    path('personnel/requests/ctdo/add/remarks', ctdo_add_remarks, name='ctdo_add_remarks'),
    path('personnel/requests/ctdo/after-print/', ctdo_after_print, name='ctdo_after_print'),
    path('personnel/requests/leave/edit/<int:pk>', edit_leave_application, name='edit_leave_application'),
    path('personnel/requests/leave/cancel', cancel_leave, name='cancel_leave'),
    path('personnel/travel-hazard/', include('frontend.pas.tr_hazard.urls')),
    path('get-leavespent/', get_leavespent, name='get_leavespent'),
    path('personnel/signature/set/', set_signature_leave, name='set_signature_leave'),
    path('personnel/after-print/', leave_after_print, name='leave_after_print'),
    path('work-experience/sheet/', work_experience_sheet, name='work_experience_sheet'),
    path('work-experience/sheet/write/<int:pk>', write_wes, name='write_wes'),
    path('work-experience/sheet/print', print_wes, name='print_wes'),
    path('accomplishment-report/', accomplishment_report, name='accomplishment_report'),
    path('get-accomplishment-report/async/', async_get_accomplishment_outputs, name='async_get_accomplishment_outputs'),
    path('accomplishment-report/get/<str:start_date>/<str:end_date>', get_accomplishment_report, name='get_accomplishment_report'),
    path('accomplishment-report/clear/', clear_accomplishment_report, name='clear_accomplishment_report'),
    path('print-accomplishment/<str:sd>/<str:ed>', print_accomplishment, name='print_accomplishment'),
    path('accomplishment/signatories/set/', set_signature_accomplishment, name='set_signature_accomplishment'),
    path('dtr/print/', print_dtr, name='print_dtr'),
    path('generate-form/', generateform, name='generateform'),
    path('fetch-accomplishment/<str:date>', fetchaccomplishment, name='fetchaccomplishment'),
    path('dtr-accomplishment/', wfh_accomplishment, name='wfh_accomplishment'),
    path('faqs/', faqs, name='faqs'),
    path('delete-form/<int:pk>', delete_form, name='delete-form'),
    path('announcements/', announcements, name='announcements'),
    path('announcements/delete/', delete_announcement, name='delete-announcement'),
    path('personnel/', include('frontend.pas.payroll.urls')),
    path('grievances/', grievances, name='grievance_module'),
    path('grievances/update/', update_grievance, name='update_grievance'),
    path('grievances/view/<int:pk>', view_grievance, name='view_grievance'),
    path('grievance-overview/get/', get_grievance_overview, name='get-grievance-overview'),
    path('grievance-latest-status/<int:pk>', get_grievance_latest_status, name='get-grievance-latest-status'),
    path('grievance-get-province-name/<str:id>', get_province_name, name='grievance-get-province-name'),
    path('directory/list/', directory_list, name='directory-list'),
    path('directory/list/edit/<int:pk>', edit_directory_list, name='edit_directory_list'),
    path('directory/list/requests', directory_list_requests, name='directory-list-requests'),
    path('directory/detail/delete/', delete_detail, name='delete-detail'),
    path('directory/search/', contacts_search, name='contacts-search'),
    path('tracking/drn/', my_drn, name='my-drn'),
    path('tracking/drn/delete/', delete_drn, name='delete-drn'),
    path('tracking/drn/summary/', my_drn_summary, name='my-drn-summary'),
    path('tracking/', document_tracking, name='tracking-inbox'),
    path('tracking/total/', get_total_dt, name='get_total_dt'),
    path('tracking/document/view/<int:pk>', view_document, name='view_document'),
    path('tracking/document/view/<int:pk>/<int:mark_as_received>', view_document, name='view_document'),
    path('tracking/document/view/<int:pk>/<int:mark_as_received>/<int:received_in_behalf>',
         view_document, name='view_document'),
    path('tracking/document/view/blank/<int:pk>', view_document_blank, name='view_document_blank'),
    path('tracking/sentbox/', sentbox, name='tracking-sentbox'),
    path('tracking/carboncopy/', carboncopy, name='tracking-carboncopy'),
    path('tracking/document/section/', section_docs, name='tracking-section-docs'),
    path('tracking/get/section/<int:pk>', get_section, name='get-section'),
    path('tracking/get/doctype/<int:pk>', get_doctype, name='get-doctype'),
    path('tracking/get/doctype/', get_doctype, name='get-doctype'),
    path('tracking/get/division/section/<str:id_number>', get_division_and_section, name='get-division-and-section'),
    path('events/v2/', events_v2, name='events_v2'),
    path('events/v2/get/all/<int:status>', get_all_events, name='get_all_events'),
    path('events/', events, name='events'),
    path('events/<int:status>', events, name='events'),
    path('events/view/<int:id>', view_event, name='view-events'),
    path('events/add/', add_event, name='add-events'),
    path('events/update/', update_event, name='update-events'),
    path('events/delete/', delete_event, name='delete-events'),
    path('events/approval/save/', save_event_approval, name='save-event-approval'),
    path('events/approval/revert/', revert_event_approval, name='revert-event-approval'),
    path('events/approval/<int:event_id>', get_approval_id, name='get-approval-id'),
    path('events/permission/<int:type_id>', get_has_permission_for_calendar, name='get-has-permission-for-calendar'),
    path('events/calendar/add/', add_private_calendar, name='add-private-calendar'),
    path('events/calendar/update/', update_private_calendar, name='update-private-calendar'),
    path('events/calendar/sharing/<int:type_id>', calendar_sharing, name='calendar-sharing'),
    path('events/calendar/sharing/add/', share_calendar, name='share-calendar'),
    path('events/calendar/sharing/remove/<int:id>', unshare_calendar, name='unshare-calendar'),
    path('overtime/', include('frontend.pas.overtime.urls')),
    path('recruitment-selection-and-placement/', include('frontend.rsp.urls')),


    path('employee/profile/', my_profile, name='my-profile'),
    path('about/', about, name='about'),
    path('pds-pageone/<int:pk>', pds_pageone, name="pds_pageone"),
    path('pds-pagetwo/<int:pk>', pds_pagetwo, name="pds_pagetwo"),
    path('pds-pagethree/<int:pk>', pds_pagethree, name="pds_pagethree"),
    path('pds-pagefour/<int:pk>', pds_pagefour, name="pds_pagefour"),
    path('pds-pagefive/<int:pk>', pds_pagefive, name="pds_pagefive"),
    path('change-password/', change_password, name='change-password'),
    path('employee/files/201/', files_201, name='files_201'),
    path('employee/files/clearance/', view_clearance_layout_current, name='view_clearance_layout_current'),
    path('employee/requests/', ticket_request, name='ticket_request'),
    path("employee/pds/personal-information/", personal_info, name="personal-info"),
    path("employee/pds/family-background/", family_background, name="family-background"),
    path('employee/pds/educational-baackground/', educational_background, name="educational-background"),
    path('employee/pds/civil-service/', civil_service, name='civil-service'),
    path('employee/pds/course/add/', add_pds_course, name='add_pds_course'),
    path('employee/pds/work-experience/', work_experience, name='work-experience'),
    path('employee/pds/voluntary-work/', voluntary, name='voluntary'),
    path('employee/pds/trainings-attended/', training, name='training'),
    path('employee/pds/other-information/', others, name='other-information'),
    path('employee/pds/additional-information/', additional_information, name='additional'),
    path('employee/pds/references/', attachment, name='attachment'),
    path('employee/pds/', include('frontend.pas.profile.urls')),
    path('employee/travels/', travel_history, name='travel_history'),
    path('employee/ipcr/', emp_ipcr, name='emp_ipcr'),
    path('employee/ipcr/details/<int:pk>', emp_ipcr_details, name='emp_ipcr_details'),

    path('leave/requests/', leave_application, name='leave_application'),
    path('leave/requests/print/<int:pk>', print_leaveapp, name='print_leaveapp'),
    path('travel/requests/', rito, name='rito'),
    path('travel/requests/edit/<int:pk>', edit_rito, name='edit_rito'),
    path('travel/requests/print/<int:pk>', print_rito, name='print-rito'),
    path('learning-and-development/', include('frontend.lds.urls')),
    path('rewards-and-recognition/nominations/', awards, name='nominations'),
    path('payroll/', include('frontend.payroll_new.urls')),
]
