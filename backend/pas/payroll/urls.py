from django.urls import path

from backend.pas.payroll.views import payroll_employee, payroll_list, \
    payrolL_list_view, generate_payroll, import_template, payroll_detail_view, \
    lock_payroll, unlock_payroll, employee_edit, get_column, \
    draft_column_group, draft_column_group_start, employee_group, employee_group_delete, process_employee, \
    status_dtr, print_obs_dv_form, delete_draft_columns, recalculate, recalculate_url, \
    download_template
from backend.pas.payroll2.views import payroll_uploading, get_payroll_list, delete_payroll_one, delete_payroll_many, \
    new_generate_template, generate_employee_payslip, payroll_list_all, get_payroll_list_all, print_payroll, tax, \
    get_tax_data, send_tax_computation, payroll_movs, view_payroll_movs, delete_payroll_movs

urlpatterns = [
    path('employee/management/', payroll_employee, name='payroll_employee'),
    path('employee/edit/<int:emp_id>/', employee_edit, name='employee_edit'),
    path('employee/group/', employee_group, name='employee_group'),
    path('employee/group/delete/', employee_group_delete, name='employee_group_delete'),
    path('employee/process/', process_employee, name='process_employee'),
    path('list/', payroll_list, name='payroll_list'),
    path('get-column/<int:type_id>', get_column, name='get_column'),
    path('draft/column-group/', draft_column_group, name='draft_column_group'),
    path('draft/column-group/start/<int:cg_id>', draft_column_group_start, name='draft_column_group_start'),
    path('draft/column-group/delete', delete_draft_columns, name='delete_draft_columns'),
    path('recalculate/<int:payroll_id>', recalculate, name='recalculate'),
    path('recalculate/url/<int:pk>', recalculate_url, name='recalculate_url'),
    path('list/view/<int:id>/', payrolL_list_view, name='payrolL_list_view'),
    path('status/dtr/', status_dtr, name='status_dtr'),
    path('import/template/<int:id>/', import_template, name='import_template'),
    path('generate/template/<int:payroll_id>/', generate_payroll, name='generate_template'),
    path('download/template/<int:id>/', download_template, name='download_template'),
    path('detail/view/<int:payroll_id>/<int:emp_id>/<str:type>', payroll_detail_view, name='payroll_detail_view'),
    path('lock/<int:payroll_id>/', lock_payroll, name='lock_payroll'),
    path('unlock/<int:payroll_id>/', unlock_payroll, name='unlock_payroll'),
    path('generate/payslip/', generate_employee_payslip, name='generate_employee_payslip'),
    path('print/obs-dv/form/', print_obs_dv_form, name='print_obs_dv_form'),
    path('list/all/', payroll_list_all, name='payroll_list_all'),
    path('uploading/', payroll_uploading, name='payroll_uploading'),
    path('generate/template/', new_generate_template, name='new_generate_template'),
    path('list/uploading/<int:year>', get_payroll_list, name='get_payroll_list'),
    path('list/uploading/all/<int:year>', get_payroll_list_all, name='get_payroll_list_all'),
    path('list/delete/one', delete_payroll_one, name='delete_payroll_one'),
    path('list/delete/many', delete_payroll_many, name='delete_payroll_many'),
    path('print/payroll/', print_payroll, name='print_payroll'),
    path('tax/', tax, name='tax'),
    path('tax/get/data/', get_tax_data, name='get_tax_data'),
    path('tax/notification/send/', send_tax_computation, name='send_tax_computation'),
    path('movs/', payroll_movs, name='payroll_movs'),
    path('movs/view/<int:pk>', view_payroll_movs, name='view_payroll_movs'),
    path('movs/delete/', delete_payroll_movs, name='delete_payroll_movs')
]