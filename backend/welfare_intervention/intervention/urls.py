from django.urls import path
from .views import hrwelfare_intervention
from backend.welfare_intervention.intervention.views import covidassistance, insertassistance,printreport,vest_borrower,insertvest, \
    updatevest, hrwactivity, showitem, insertactivity, sweapassistance, printsweapreport, printinterventionreport, \
    update_sweap, gratuity_pay, printgratuity, updatecovid, welfare_dashboard,show_inventory, modalforintervention, updateintervention, \
    remind_vest, delete_gratuity, filter_employee_inactive, delete_sweap

from backend.welfare_intervention.intervention.stocks.views import stock_in, insert_stocks
from backend.welfare_intervention.intervention.emp_assistance.views import employee_assistance, show_category, attached_file, modalforemp_assistance, \
    get_form, assistance_submit, delete_info,printempassistance, employee_ir, emp_ir_modal, insert_ir_attachment, print_irdb, print_form

from backend.welfare_intervention.intervention.health_profiling.views import health_profiling, modal_emp_profile,individual_print
from backend.welfare_intervention.intervention.sweap_membership.views import sweap_membership_form, upload_attachment, update_sweap_form, delete_sweap_benes

urlpatterns = [
    #Membership Form
    path('sweap/form', sweap_membership_form, name='sweap_membership_form'),
    path('upload/sweap/attachment/<int:pk>', upload_attachment, name='upload_attachment'),
    path('update/sweap/form/<int:pk>', update_sweap_form, name='update_sweap_form'),
    path('delete/sweap/bene', delete_sweap_benes, name='delete_sweap_benes'),

    path('welfare/dashboard', welfare_dashboard, name='welfare_dashboard'),
    # THIS IS HR WELFARE COVID ASSISTANCE
    path('covid/financial/assistance', covidassistance, name='covidassistance'),
    path('covid/insert/assistance/', insertassistance, name='insertassistance'),
    path('covid/print/report/', printreport, name='printreport'),
    path('updatecovid', updatecovid, name='updatecovid'),

    # THIS IS FOR VEST MODULE
    path('intervention/vest/borrower/', vest_borrower, name='vest_borrower'),
    path('intervention/vest/insert/vest_borrower', insertvest, name='insertvest'),
    path('updatevest', updatevest, name='updatevest'),
    path('remind_vest', remind_vest, name="remind_vest"),

    # THIS IS FOR WELFARE INTERVENTION
    path('intervention/activity/hrwactivity/', hrwactivity, name='hrwactivity'),
    path('intervention/activity/item/showitem/', showitem, name='showitem'),
    path('intervention/insert/activity/', insertactivity, name='insertactivity'),
    path('intervention/modalforintervention/<int:pk>', modalforintervention, name='modalforintervention'),
    path('intervention/print/report/', printinterventionreport, name='printinterventionreport'),
    path('updateintervention', updateintervention, name='updateintervention'),
    path('show_inventory',show_inventory, name='show_inventory'),

    path('update/stock_in', insert_stocks, name='insert_stocks'),
    path('stock/stock_in', stock_in, name="stock_in"),

    # THIS IS FOR SWEAP ASSISTANCE
    path('sweap/assistance/', sweapassistance, name='sweapassistance'),
    path('sweap/print/report/', printsweapreport, name='printsweapreport'),
    path('sweap/update/', update_sweap, name="update_sweap"),
    path('delete/sweap', delete_sweap, name="delete_sweap"),

    # THIS IS FOR GRATUITY PAY
    path('sweap/gratuity_pay/', gratuity_pay, name="gratuity_pay"),
    path('sweap/print/report/gratuity', printgratuity, name='printgratuity'),
    path('sweap/delete_gratuity',delete_gratuity,name="delete_gratuity"),
    path('filter/filter_employee_inactive/', filter_employee_inactive, name='filter_employee_inactive'),

    # EMPLOYEE ASSISTANCE
    path('employee/assistace/', employee_assistance, name="employee_assistance"),
    path('category/', show_category, name="show_category"),
    path('attached_file/',attached_file,name="attached_file"),
    path('assistance/modalforemp_assistance/<int:pk>', modalforemp_assistance, name='modalforemp_assistance'),
    path('get_form/',get_form,name='get_form'),
    path('print_form/<str:pk>',print_form,name='print_form'),
    path('assistance_submit/',assistance_submit,name='assistance_submit'),
    path('printempassistance',printempassistance,name='printempassistance'),
    path('delete_info', delete_info, name='delete_info'),

    # EMPLOYEE IR
    path('Employee/Incident_report/', employee_ir, name="employee_ir"),
    path('IncidentReport/modal/<int:pk>', emp_ir_modal, name="emp_ir_modal"),
    path('Employee/Incident_report/Attachment/',insert_ir_attachment,name="insert_ir_attachment"),
    path('Employee/Print_ir/',print_irdb,name="print_irdb"),

    # HEALTH PROFILE
    path('health_profiling/',health_profiling,name="health_profiling"),
    path('health_profile/modal_emp_profile/<int:pk>',modal_emp_profile,name="modal_emp_profile"),
    path('individual_print/',individual_print,name="individual_print"),

    # INTERVENTION DATABASE
    path('intervention/database/',hrwelfare_intervention,name="hrwelfare_intervention"),

]