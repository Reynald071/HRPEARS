from django.urls import path, include

from backend.calendar.views import calendar_type, calendar_type_permissions, add_calendar_permissions, \
    remove_calendar_permissions, CalendarTypeUpdate
from backend.libraries.directory.views import detailtype, DirectoryDetailTypeUpdate
from backend.libraries.documents.views import sop_class, SopClassUpdate, docs_201_type, Docs201TypeUpdate, \
    issuances_type, IssuancesTypeUpdate, dl_class, DlClassUpdate
from backend.libraries.tracking.views import doctype, DtsDoctypeUpdate
from frontend.pis.api import api_schools, api_degrees, api_honors, api_eligibilities, api_positions, api_organizations, \
    api_trainings, api_hobbies, api_nonacads
from backend.awards.views import badges, BadgesUpdate, awclassification, ClassificationUpdate, awlevels, AwlevelsUpdate, \
    update_awards, validate_nominees, add_nominee, verified_nominee, delete_nominee, edit_nominee, reset_results, \
    mark_as_winner, check_password, toggle_awards, awcategories, AwcategoriesUpdate, check_awards, deliberation_results, \
    nominees_report, print_nominees_report, print_deliberation_results, awards, upload_guidelines, delete_guidelines, \
    awards_eligibility_criteria, eligibility_criteria_checklist, update_checklist_eligibility
from backend.designation.views import designation, DesignationUpdate
from backend.iso.views import iso_forms
from backend.leave.views import leave_credits, leave_request, view_leave_request, \
    update_leave_credits, bulk_import_leave_credits, cancel_leave_request, admin_ctdo_requests, admin_ctdo_approve, \
    remove_credits_history, uncancel_leave_request, get_leave_spent, leave_attachment, leave_certification, \
    leave_certification_layout, leave_certificate_transaction, generate_drn_lc, print_leave_certificate, \
    admin_ctdo_update, edit_leave_certificate, coc_credits, view_coc_credits, delete_coc, print_coc, update_coc_drn, \
    view_coc_utilization, admin_utilize_coc_earned, print_coc_previous, add_coc_balance_on_certificate, \
    view_custom_coc_balance, remove_custom_coc_balance, auto_utilize_coc_earned_admin, generate_ctdo_report, \
    move_leave_application_to_ctdo, ctdo_attachment, update_custom_coc_balance
from backend.libraries.grievance.views import classification, GrievanceClassificationUpdate, GrievanceMediaUpdate, \
    media, GrievanceStatusUpdate, status
from backend.libraries.leave.views import leave_type, LeavetypeUpdate, leave_subtype, LeavesubtypeUpdate, leave_spent, \
    LeavespentUpdate
from backend.libraries.pis.views import bloodtype, BloodtypeUpdate, civilstatus, CivilstatusUpdate, hobbies, \
    HobbiesUpdate, \
    degree, DegreeUpdate, educationlevel, EducationlevelUpdate, eligibility, EligibilityUpdate, honors, HonorsUpdate, \
    school, SchoolUpdate, brgy, BrgyUpdate, city, CityUpdate, province, ProvinceUpdate, countries, CountryUpdate, \
    organization, OrganizationUpdate, nonacad, NonacadUpdate, trainingtitle, TrainingtitleUpdate, trainingtype, \
    TrainingtypeUpdate, find_merges, merge_degree, merge_organization, merge_honors, merge_schools, \
    merge_trainingtitles, merge_eligibilities, merge_positions, merge_hobbies, merge_nonacads
from backend.libraries.hrppms.views import fundsource, FundsourceUpdate, aoa, AoaUpdate, project, ProjectUpdate, \
    empstatus, EmpstatusUpdate, position, PositionUpdate, mode_accession, mode_accessionUpdate, mode_separation, \
    mode_separationUpdate
from backend.pas.accomplishment.views import view_accomplishment_report
from backend.pas.employee.views import employees, show_children, remove_children, view_pds_pageone, view_pds_pagetwo, \
    view_pds_pagethree, view_pds_pagefour, view_profile, divisions, DiviUpdate, sections, SecUpdate, \
    view_pds_pagefive, update_user, activities, about, settings, edit_workhistory, permission, backend_travel_history, \
    export_employees, bulk_import_employees, work_history, register_employee, generate_itemnumber, export_data, \
    view_ad_account, validate_pds, edit_employee, add_payroll_incharge
from backend.pas.resignation.views import deactivation_request, view_resignation_request, deactivate_user, \
    delete_compliance, \
    activate_user, rfd
from backend.infimos.views import repeat_last_infimos_transaction, filter_payee
from backend.pas.travel_order.views import rito_request, view_rito, approved_rito, update_rito, generate_to, \
    approved_to, to_claims, TOClaimsUpdate, to_mot, TOMotUpdate, view_rito_details, \
    edit_rito_details, delete_ritopeople, add_rito_details, delete_travel_request, delete_backend_rito, \
    cancel_travel_order, travel_remark, travel_order_report, generate_travel_order, unapproved_to, \
    attachment_to_update, merge_travel, filter_tracking_no, undo_merge_travel_all, undo_merge_travel,\
    update_travel_remarks, admin_travel_total, uncancel_travel_order, view_tr_tracking, mark_as_received_tr,\
    travel_order_summary
from backend.pas.outpass.views import outpass_request, AttachmentOutpassUpdate, approve_outpass, get_outpass_total, \
    outpass_report, outpass_returned, trigger_returned
from backend.views import (logout, filter_employee, upload_picture, feedback, delete_feedback,
                           text_blast, filter_incumbent, upload_picture_admin, filter_employee_by_permission,
                           filter_employee_all, filter_employee_by_division, filter_leave_employee,
                           filter_ctdo_employee, filter_shortcut_links, monthly_birthdays, print_birthdays)

urlpatterns = [
    path('libraries/utils/merges/find/<str:model>/<str:q>/<str:id>', find_merges, name='find-merges'),
    path('libraries/descriptive/bloodtypes/', bloodtype, name='bloodtype'),
    path('libraries/descriptive/bloodtypes/update/<int:pk>', BloodtypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'descriptive', 'sub_sub_title': 'bloodtype'}),
         name='bt-update'),
    path('libraries/descriptive/civilstatuses/', civilstatus, name='civil-status'),
    path('libraries/descriptive/civilstatuses/update/<int:pk>', CivilstatusUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'descriptive', 'sub_sub_title': 'civilstatus'}),
         name='cs-update'),
    path('libraries/descriptive/hobbies/', hobbies, name="hobbies"),
    path('libraries/descriptive/hobbies/update/<int:pk>', HobbiesUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'descriptive', 'sub_sub_title': 'hobbies'}),
         name='hobbies-update'),

    path('libraries/education/academichonors/', honors, name='honors'),
    path('libraries/education/academichonors/update/<int:pk>', HonorsUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'education', 'sub_sub_title': 'honors'}),
         name='honors-update'),
    path('libraries/education/degrees/', degree, name='degree'),
    path('libraries/education/degrees/update/<int:pk>', DegreeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'education', 'sub_sub_title': 'degree'}),
         name='degree-update'),
    path('libraries/education/levels/', educationlevel, name='educationlevel'),
    path('libraries/education/levels/update/<int:pk>', EducationlevelUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'education', 'sub_sub_title': 'level'}),
         name='education-level-update'),
    path('libraries/education/eligibilities/', eligibility, name='eligibility'),
    path('libraries/education/eligibilities/update/<int:pk>/', EligibilityUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'education', 'sub_sub_title': 'eligibility'}),
         name='el-update'),
    path('libraries/education/schools/', school, name='school'),
    path('libraries/education/schools/update/<int:pk>', SchoolUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'education', 'sub_sub_title': 'school'}),
         name='school-update'),

    path('libraries/grievance/classifications/', classification, name='grievance-classification'),
    path('libraries/grievance/classifications/update/<int:pk>', GrievanceClassificationUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'grievance', 'sub_sub_title': 'classification'}),
         name='grievance-classification-update'),
    path('libraries/grievance/media/', media, name='grievance-media'),
    path('libraries/grievance/media/update/<int:pk>', GrievanceMediaUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'grievance', 'sub_sub_title': 'media'}),
         name='grievance-media-update'),
    path('libraries/grievance/statuses/', status, name='grievance-status'),
    path('libraries/grievance/statuses/update/<int:pk>', GrievanceStatusUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'grievance', 'sub_sub_title': 'status'}),
         name='grievance-status-update'),

    path('libraries/directory/detail-types/', detailtype, name='detail-type'),
    path('libraries/directory/detail-types/update/<int:pk>', DirectoryDetailTypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'directory', 'sub_sub_title': 'detailtype'}),
         name='detail-type-update'),

    path('libraries/tracking/doc-types/', doctype, name='doc-type'),
    path('libraries/tracking/doc-types/update/<int:pk>', DtsDoctypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'tracking', 'sub_sub_title': 'doctype'}),
         name='doc-type-update'),

    path('libraries/documents/downloadables-class/', dl_class, name='dl-class'),
    path('libraries/documents/downloadables-class/update/<int:pk>', DlClassUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'documents', 'sub_sub_title': 'dl_class'}),
         name='dl-class-update'),

    path('libraries/documents/sop-classification/', sop_class, name='sop-class'),
    path('libraries/documents/sop-classification/update/<int:pk>', SopClassUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'documents', 'sub_sub_title': 'sop_class'}),
         name='sop-class-update'),

    path('libraries/documents/docs-201-type/', docs_201_type, name='docs-201-type'),
    path('libraries/documents/docs-201-type/update/<int:pk>', Docs201TypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'documents', 'sub_sub_title': 'docs_201_type'}),
         name='docs-201-type-update'),

    path('libraries/documents/issuances-type/', issuances_type, name='issuances-type'),
    path('libraries/documents/issuances-type/update/<int:pk>', IssuancesTypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'documents', 'sub_sub_title': 'issuances_type'}),
         name='issuances-type-update'),

    path('libraries/calendar/type/', calendar_type, name='calendar-type'),
    path('libraries/calendar/type/permissions/add/', add_calendar_permissions, name='add-calendar-permissions'),
    path('libraries/calendar/type/permissions/delete/<int:id>', remove_calendar_permissions, name='remove-calendar'
                                                                                                  '-permissions'),
    path('libraries/calendar/type/permissions/<int:id>', calendar_type_permissions, name='calendar-type-permissions'),
    path('libraries/calendar/type/update/<int:pk>', CalendarTypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'calendar', 'sub_sub_title': 'type'}),
         name='calendar-type-update'),

    path('libraries/awards/badges/', badges, name="badges"),
    path('libraries/awards/badges/update/<int:pk>',
         BadgesUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'awards', 'sub_sub_title': 'badges'}),
         name="badges-update"),
    path('libraries/awards/classifications/', awclassification, name="classification"),
    path('libraries/awards/classifications/update/<int:pk>', ClassificationUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'awards', 'sub_sub_title': 'classification'}),
         name="classification-update"),
    path('libraries/awards/levels/', awlevels, name="award-level"),
    path('libraries/awards/levels/update/<int:pk>',
         AwlevelsUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'awards', 'sub_sub_title': 'level'}),
         name="award-level-update"),
    path('libraries/awards/categories/', awcategories, name="award-category"),
    path('libraries/awards/categories/update/<int:pk>',
         AwcategoriesUpdate.as_view(
             extra_context={'title': 'libraries', 'sub_title': 'awards', 'sub_sub_title': 'category'}),
         name="award-category-update"),
    path('awards/', awards, name="awards"),
    path('designation/', designation, name='designation'),
    path('designation-update/<int:pk>',
         DesignationUpdate.as_view(
             extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'designation'}),
         name='designation-update'),
    path('logout/', logout, name="backend-logout"),
    path('employees/', employees, name='backend-employees'),
    path('employees/staffing/', include('backend.pas.employee.staffing.urls')),
    path('employees/register/', register_employee, name='register_employee'),
    path('employees/edit/<int:id>', edit_employee, name='edit_employee'),
    path('documents/', include('backend.documents.urls')),
    path('update-pds/', include('backend.pas.employee.urls')),
    path('export/employees/', export_employees, name='backend-export-employees'),
    path('export/data/', export_data, name='export_data'),
    path('activities/<int:pk>', activities, name='backend-activities'),
    path('validate-pds/', validate_pds, name='validate_pds'),
    path('about/<int:pk>/<int:pi_id>', about, name='backend-about'),
    path('settings/<int:pk>', settings, name='backend-settings'),
    path('workhistory/<int:pi_id>', work_history, name='backend-workhistory'),
    path('edit-workhistory/<int:pk>', edit_workhistory, name='edit_workhistory'),
    path('permission/', permission, name='permission'),
    path('update-user/<int:pk>', update_user, name='update_user'),
    path('request-for-deactivation/', rfd, name="rfd"),
    path('resignation-request/', deactivation_request, name='resignation_request'),
    path('delete-compliance/', delete_compliance, name="delete_compliance"),
    path('deactivate-user/', deactivate_user, name="deactivate_user"),
    path('divisions/', divisions, name='divisions'),
    path('division-update/<int:pk>', DiviUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'division'}),
         name='divi-update'),
    path('sections/', sections, name='sections'),
    path('section-update/<int:pk>',
         SecUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'section'}),
         name='sec-update'),
    path('payroll/', include('backend.pas.payroll.urls')),
    path('view-resignation-detail/<int:pk>', view_resignation_request, name='view_resignation_request'),
    path('show-children/<int:pk>', show_children, name='show-children'),
    path('remove-children/<int:pk>', remove_children, name='admin-remove-children'),
    path('fund-source/', fundsource, name='fundsource'),
    path('fund-source/update/<int:pk>', FundsourceUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'fundsource'}),
         name='fundsource-update'),
    path('area-of-assignment/', aoa, name='aoa'),
    path('area-of-assignment/update/<int:pk>',
         AoaUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'aoa'}),
         name='aoa-update'),
    path('project/', project, name='project'),
    path('project-update/<int:pk>',
         ProjectUpdate.as_view(
             extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'project'}),
         name='project-update'),
    path('empstatus/', empstatus, name='empstatus'),
    path('empstatus-update/<int:pk>', EmpstatusUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'empstatus'}),
         name='empstatus-update'),
    path('position/', position, name='position'),
    path('position-update/<int:pk>', PositionUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'position'}),
         name='position-update'),
    path('countries/', countries, name='countries'),
    path('countries-update/<int:pk>', CountryUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'location', 'sub_sub_title': 'countries'}),
         name='country-update'),
    path('nonacad/', nonacad, name='nonacad'),
    path('nonacad-update/<int:pk>',
         NonacadUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'others', 'sub_sub_title': 'na'}),
         name='nonacad-update'),
    path('organization/', organization, name='organization'),
    path('organization-update/<int:pk>', OrganizationUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'others', 'sub_sub_title': 'org'}), name='org-update'),
    path('province/', province, name="province"),
    path('province-update/<int:pk>', ProvinceUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'location', 'sub_sub_title': 'province'}),
         name='prov-update'),
    path('training-title/', trainingtitle, name='trainingtitle'),
    path('trainingtitle-update/<int:pk>', TrainingtitleUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'training', 'sub_sub_title': 'title'}), name='tt-update'),
    path('training-type/', trainingtype, name='trainingtype'),
    path('trainingtype-update/<int:pk>', TrainingtypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'training', 'sub_sub_title': 'type'}), name='ttype-update'),
    path('city/', city, name="city"),
    path('city-update/<int:pk>',
         CityUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'location', 'sub_sub_title': 'city'}),
         name='city-update'),
    path('brgy/', brgy, name='brgy'),
    path('brgy-update/<int:pk>',
         BrgyUpdate.as_view(extra_context={'title': 'libraries', 'sub_title': 'location', 'sub_sub_title': 'brgy'}),
         name='brgy-update'),
    path('travel-total/<str:year>', admin_travel_total, name='admin_travel_total'),
    path('travel-request/', rito_request, name='rito-request'),
    path('filter/tracking_number/', filter_tracking_no, name='filter_tracking_no'),
    path('merge/travel/', merge_travel, name='merge_travel'),
    path('undo/merge/travel/all/', undo_merge_travel_all, name='undo_merge_travel_all'),
    path('undo/merge/travel/<str:tracking_no>', undo_merge_travel, name='undo_merge_travel'),
    path('view-travel/<str:tracking_no>', view_rito, name='view-rito'),
    path('view-travel-details/<str:tracking_no>', view_rito_details, name='view_rito_details'),
    path('add-travel-details/<str:tracking_no>', add_rito_details, name='add_rito_details'),
    path('edit-travel-details/<int:pk>', edit_rito_details, name='edit_rito_details'),
    path('delete-ritopeople', delete_ritopeople, name='delete_ritopeople'),
    path('delete-rito/<str:tracking_no>', delete_backend_rito, name='delete_backend_rito'),
    path('delete-travel-request/', delete_travel_request, name='delete_travel_request'),
    path('approved-rito/', approved_rito, name='approved-rito'),
    path('cancel-travel-order/', cancel_travel_order, name='cancel_travel_order'),
    path('travel-order/uncancel/', uncancel_travel_order, name='uncancel_travel_order'),
    path('update-rito/', update_rito, name="update-rito"),
    path('generate-to/<str:tracking_no>', generate_to, name='generate-to'),
    path('get-total-outpass/', get_outpass_total, name='pas-get-outpass-total'),
    path('approved-to/', approved_to, name='approved-to'),
    path('unapproved-to/', unapproved_to, name='unapproved-to'),
    path('attachment/travel/<str:tracking_no>', attachment_to_update, name='attachment_to_update'),
    path('travel-remark/update/<str:tracking_no>', update_travel_remarks, name='update_travel_remarks'),
    path('travel-remark/<str:tracking_no>', travel_remark, name='travel_remark'),
    path('travel-history/<int:pk>', backend_travel_history, name='backend_travel_history'),
    path('travel-report/', travel_order_report, name='travel_order_report'),
    path('travel-report/summary/', travel_order_summary, name='travel_order_summary'),
    path('generate-travel-report/', generate_travel_order, name='generate_travel_report'),
    path('tracking/travel-request/<str:pk>', view_tr_tracking, name='view_tr_tracking'),
    path('tracking/travel-request/mark-as-received/', mark_as_received_tr, name='mark_as_received_tr'),
    path('view-profile/<int:pk>', view_profile, name="view-profile"),
    path('view-ad-account/<int:pk>', view_ad_account, name='view_ad_account'),
    path('upload-profile/<int:pk>', upload_picture, name='upload_picture'),
    path('view/profile/upload/<int:pk>', upload_picture_admin, name='upload_picture_admin'),
    path('activate-user/<int:pk>', activate_user, name='activate_user'),
    path('repeat-last-infimos-transaction', repeat_last_infimos_transaction, name='repeat_last_infimos_transaction'),
    path('filter-payee/', filter_payee, name='filter_payee'),
    path('filter-shortcut-links/', filter_shortcut_links, name='filter_shortcut_links'),
    path('filter-employee/', filter_employee, name='filter_employee'),
    path('filter-employee/division/', filter_employee_by_division, name='filter_employee_by_division'),
    path('filter-employee/all/', filter_employee_all, name='filter_employee_all'),
    path('filter-employee/leave/', filter_leave_employee, name='filter_leave_employee'),
    path('filter-employee/ctdo/', filter_ctdo_employee, name='filter_ctdo_employee'),
    path('filter-employee/<str:permission>', filter_employee_by_permission, name='filter_employee_by_permission'),
    path('filter-employee/<str:permission>/<str:except_me>', filter_employee_by_permission, name='filter_employee_by_permission'),
    path('travel-claims/', to_claims, name='to_claims'),
    path('travel-claims-update/<int:pk>', TOClaimsUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'travel_order', 'sub_sub_title': 'to_claims'}),
         name="to_claim_update"),
    path('travel-means-of-transportation/', to_mot, name='to_mot'),
    path('travel-means-of-transportation-update/<int:pk>', TOMotUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'travel_order', 'sub_sub_title': 'to_mot'}),
         name="to_mot_update"),
    path('view-pds-pageone/<int:pk>/', view_pds_pageone, name="view_pds_pageone"),
    path('view-pds-pagetwo/<int:pk>/', view_pds_pagetwo, name="view_pds_pagetwo"),
    path('view-pds-pagethree/<int:pk>/', view_pds_pagethree, name="view_pds_pagethree"),
    path('view-pds-pagefour/<int:pk>/', view_pds_pagefour, name="view_pds_pagefour"),
    path('view-pds-pagefive/<int:pk>/', view_pds_pagefive, name="view_pds_pagefive"),
    path('outpass-request/', outpass_request, name='outpass-request'),
    path('outpass-returned/', outpass_returned, name='outpass-returned'),
    path('trigger-returned/<int:pk>/', trigger_returned, name='trigger-returned'),
    path('outpass-generate-report/', outpass_report, name='outpass-generate-report'),
    path('get-total-outpass-returning/', get_outpass_total, name='get-total-outpass-returning'),
    path('approve-outpass/<int:pk>/<int:status>', approve_outpass, name='approve-outpass'),
    path('attachment-outpass-update/<int:pk>', AttachmentOutpassUpdate.as_view(extra_context={'title': 'outpass'}),
         name='attachment-outpass-update'),
    path('deliberation-results/', deliberation_results, name="deliberation-results"),
    path('print-deliberation-results/', print_deliberation_results, name="print_deliberation_results"),
    path('awards/guidelines/upload/', upload_guidelines, name='upload_guidelines'),
    path('awards/guidelines/delete/<int:pk>', delete_guidelines, name='delete_guidelines'),
    path('nominees-report/', nominees_report, name='nominees_report'),
    path('print-nominees-report/', print_nominees_report, name="print_nominees_report"),
    path('check-awards/', check_awards, name="check_awards"),
    path('toggle-awards/', toggle_awards, name="toggle-awards"),
    path('update-awards/<int:pk>', update_awards, name='update_awards'),
    path('eligibility-awards/<int:pk>', awards_eligibility_criteria, name='awards_eligibility_criteria'),
    path('validate-nominees/<int:pk>', validate_nominees, name='validate-nominees'),
    path('eligibility-awards/checklist/<int:pk>', eligibility_criteria_checklist, name='eligibility_criteria_checklist'),
    path('eligibility-awards/checklist/update/<int:pk>', update_checklist_eligibility, name='update_checklist_eligibility'),
    path('add-nominee/<int:pk>', add_nominee, name='add-nominee'),
    path('verified-nominee/<int:pk>', verified_nominee, name='verified-nominee'),
    path('delete-nominee/<int:pk>', delete_nominee, name='delete-nominee'),
    path('edit-nominee/<int:pk>', edit_nominee, name='edit-nominee'),
    path('reset-results/<int:pk>', reset_results, name='reset-results'),
    path('mark-as-winner/<int:pk>', mark_as_winner, name='mark-as-winner'),
    path('check-password/', check_password, name='check-password'),
    path('ctdo/coc/', coc_credits, name='coc_credits'),
    path('ctdo/coc/view/utilization/<str:pk>', view_coc_utilization, name='view_coc_utilization'),
    path('ctdo/coc/view/<str:pk>', view_coc_credits, name='view_coc_credits'),
    path('ctdo/coc/delete/', delete_coc, name='delete_coc'),
    path('ctdo/coc/print/<str:pk>', print_coc, name='print_coc'),
    path('ctdo/coc/print/previous/<str:pk>', print_coc_previous, name='print_coc_previous'),
    path('ctdo/coc/update/drn/', update_coc_drn, name='update_coc_drn'),
    path('ctdo/coc/balance/add/', add_coc_balance_on_certificate, name='add_coc_balance_on_certificate'),
    path('ctdo/coc/view/custom/<int:pk>', view_custom_coc_balance, name='view_custom_coc_balance'),
    path('ctdo/coc/remove/custom/', remove_custom_coc_balance, name='remove_custom_coc_balance'),
    path('ctdo/coc/update/custom/', update_custom_coc_balance, name='update_custom_coc_balance'),
    path('move/leave-application/to/ctdo/', move_leave_application_to_ctdo, name='move_leave_application_to_ctdo'),
    path('ctdo/requests/', admin_ctdo_requests, name='admin_ctdo_requests'),
    path('ctdo/attachment/<int:pk>', ctdo_attachment, name='ctdo_attachment'),
    path('ctdo/update/<int:pk>', admin_ctdo_update, name='admin_ctdo_update'),
    path('ctdo/report/generate/<str:month>', generate_ctdo_report, name='generate_ctdo_report'),
    path('ctdo/utilization/auto/', auto_utilize_coc_earned_admin, name='auto_utilize_coc_earned_admin'),
    path('ctdo/requests/approve', admin_ctdo_approve, name='admin_ctdo_approve'),
    path('ctdo/utilize/coc/<str:pk>/<int:ctdo_id>', admin_utilize_coc_earned, name='admin_utilize_coc_earned'),
    path('leave-type/', leave_type, name='leave_type'),
    path('leave-spent/get/<int:pk>', get_leave_spent, name='get_leave_spent'),
    path('leave/credits/history/delete/', remove_credits_history, name='remove_credits_history'),
    path('leave-type/update/<int:pk>', LeavetypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'leave', 'sub_sub_title': 'leave_type'}),
         name='leavetype-update'),
    path('leave-subtype/', leave_subtype, name='leave_subtype'),
    path('leave-sub-type/update/<int:pk>', LeavesubtypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'leave', 'sub_sub_title': 'leave_subtype'}),
         name='leavesubtype-update'),
    path('leave-spent/', leave_spent, name='leave_spent'),
    path('leave-spent/update/<int:pk>', LeavespentUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'leave', 'sub_sub_title': 'leave_spent'}),
         name='leavespent-update'),
    path('leave-credits/', leave_credits, name='leave-credits'),
    path('bulk-import-leave-credits/', bulk_import_leave_credits, name='bulk_import_leave_credits'),
    path('update-leave-credits/<int:pk>', update_leave_credits, name='update_leave_credits'),
    path('leave/certification/', leave_certification, name='leave_certification'),
    path('leave/certification/transaction/<str:emp_id>', leave_certificate_transaction, name='leave_certificate_transaction'),
    path('leave/certification/generate/drn/<int:pk>', generate_drn_lc, name='generate_drn_lc'),
    path('leave/certification/print/<int:pk>', print_leave_certificate, name='print_leave_certificate'),
    path('leave/certification/template/<int:pk>/<str:emp_id>', leave_certification_layout, name='leave_certification_layout'),
    path('leave/certification/template/edit/<int:pk>', edit_leave_certificate, name='edit_leave_certificate'),
    path('leave_request/', leave_request, name='leave_request'),
    path('leave-request/attachment/<int:pk>', leave_attachment, name='leave_attachment'),
    path('view-leave-request/<int:pk>', view_leave_request, name='view_leave_request'),
    path('cancel/leave/request/', cancel_leave_request, name='cancel_leave_request'),
    path('uncancel/leave/request/', uncancel_leave_request, name='uncancel_leave_request'),
    path('feedback/', feedback, name='feedback'),
    path('delete-feedback/<int:pk>', delete_feedback, name='delete_feedback'),
    path('text-blast/', text_blast, name='text_blast'),
    path('api/schools/<int:pi_id>', api_schools, name='api-schools'),
    path('api/degrees/<int:pi_id>', api_degrees, name='api-degrees'),
    path('api/honors/<int:pi_id>', api_honors, name='api-honors'),
    path('api/eligibilities/<int:pi_id>', api_eligibilities, name='api-eligibilities'),
    path('api/positions/<int:user_id>', api_positions, name='api-positions'),
    path('api/organizations/<int:pi_id>', api_organizations, name='api-organizations'),
    path('api/trainings/<int:pi_id>', api_trainings, name='api-trainings'),
    path('api/hobbies/<int:pi_id>', api_hobbies, name='api-hobbies'),
    path('api/nonacads/<int:pi_id>', api_nonacads, name='api-nonacads'),
    path('view-accomplishment-report/', view_accomplishment_report, name='view_accomplishment_report'),
    path('bulk-import-employees/', bulk_import_employees, name='bulk-import-employees'),
    path('merge/degree/', merge_degree, name='merge-degree'),
    path('merge/organization/', merge_organization, name='merge-organization'),
    path('merge/honors/', merge_honors, name='merge-honors'),
    path('merge/schools/', merge_schools, name='merge-schools'),
    path('merge/trainingtitles/', merge_trainingtitles, name='merge-trainingtitles'),
    path('merge/eligibilities/', merge_eligibilities, name='merge-eligibilities'),
    path('merge/positions/', merge_positions, name='merge-positions'),
    path('merge/hobbies/', merge_hobbies, name='merge-hobbies'),
    path('merge/nonacads/', merge_nonacads, name='merge-nonacads'),
    path('iso-forms/', iso_forms, name='iso-forms'),
    path('mode-accession/', mode_accession, name='mode-accession'),
    path('mode-accession/update/<int:pk>', mode_accessionUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'modeaccess'}),
         name='mode-accession-update'),
    path('mode-separation/', mode_separation, name='mode-separation'),
    path('mode-separation/update/<int:pk>', mode_separationUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'employees', 'sub_sub_title': 'separation'}),
         name='mode-separation-update'),
    path('generate-itemnumber/<int:pk>', generate_itemnumber, name='generate-itemnumber'),
    path('filter-incumbent/', filter_incumbent, name='filter-incumbent'),
    path('add/payroll-incharge/', add_payroll_incharge, name='add_payroll_incharge'),
    path('clearance/', include('backend.pas.clearance.urls')),
    path('document/', include('backend.pas.document_tracking.urls')),
    path('libraries/gamification/', include('backend.libraries.gamification.urls')),
    path('transmittal/', include('backend.pas.transmittal.urls')),
    path('performance/ipcr/', include('backend.ipcr.urls')),
    path('learning-and-development/', include('backend.lds.urls')),
    path('service-record/', include('backend.pas.service_record.urls')),
    path('monthly-birthdays/', monthly_birthdays, name="monthly_birthdays"),
    path('monthly-birthdays/print/<int:month>', print_birthdays, name="print_birthdays"),
    path('position/', include('backend.pas.employee.position.urls')),
    path('job-application/', include('backend.pas.employee.job_app.urls')),
    path('file-uploading/', include('backend.pas.employee.file_uploading.urls'))
]
