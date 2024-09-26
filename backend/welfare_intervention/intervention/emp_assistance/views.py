from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, datetime
from django.db.models import Value, Sum, Count
from django.core.paginator import Paginator
from backend.models import Empprofile
from backend.welfare_intervention.intervention.models import CovidAssistance, vest_db, activity_db, item_db, intervention, sweap_assistance, \
	sweap_gratuity, type_of_request, category_request, doucument_attached, employee_assistance_sop, \
	emp_assistance_attachment, incidentreport_db, ir_attachment_db, incident_data_db
from backend.models import Empprofile
from django.db.models.functions import Concat, Upper
from django.contrib import messages
from django.utils import timezone

today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")
import json
import re

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg', 'docx', 'xls', 'pdf','xlsx']


@csrf_exempt
def employee_assistance(request): 
	if request.method == "POST":
		insert1 = employee_assistance_sop.objects.filter(id=request.POST.get('assistance_id')).update(
			brief_request = request.POST.get('Nor'),
			cr_financial_others = request.POST.get('other_finance'),
			result_of_interview = request.POST.get('result_interview'),
			action_provided = request.POST.get('action_provided'),
			other_docx = request.POST.get('document_specified'),
			remarks = request.POST.get('remarks'),
			officer_in_charge = request.POST.get('officer_in_charge'),
			unit_quantity = request.POST.get('unit'),
			date_received = request.POST.get('date_received'),
			date_endorse_cis = request.POST.get('date_endorse'),
			)
		emp_assistance_attachment.objects.filter(emp_assistance_id=request.POST.get('assistance_id')).delete()
		emp_assistance_attachment.objects.create(
			emp_assistance_id=request.POST.get('assistance_id'),
			attachment_data=request.FILES.get('file'),
		)

		return JsonResponse({'data': 'success'})

	display_tr = type_of_request.objects.all()

	intervention = "HRWelfare"
	subtitle = "sweap_assistance"
	sub_sub_title = "employee_assistance"
	context = {
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
		'display_type_request': display_tr,

	}
	return render(request,'backend/Welfare_Intervention/emp_assistance/emp_assistance.html', context)

@csrf_exempt
def show_category(request): #DYNAMIC DISPLAY IN SELECT2
	itm = category_request.objects.all().filter(toa_id=request.POST.get("src"))
	data = [dict(id=row.id, item=row.name) for row in itm]
	return JsonResponse({'data': data})


@csrf_exempt
def attached_file(request):
	if request.POST.get('attached_file') == "":
		Fail = "FAIL SAVE"
		return JsonResponse({'data': Fail})
	else:
		itm = category_request.objects.all().filter(id=request.POST.get('attached_file'))
		for row in itm:
			attached = doucument_attached.objects.all().filter(category_id=row.toa_id)
			data = [dict(id=row.id, name=row.name) for row in attached]
			return JsonResponse({'data': data})


def modalforemp_assistance(request,pk):
	data = employee_assistance_sop.objects.filter(id=pk).first()
	file = emp_assistance_attachment.objects.filter(emp_assistance_id=pk).first()
	context = {
		'data': data,
		'file': file,
		'pk': pk,
	}
	return render(request, 'backend/Welfare_Intervention/emp_assistance/modalforassistance.html',context)


@csrf_exempt
def assistance_submit(request):
	if request.method == "POST":
		print('here....')
		today = date.today()
		print('pk', request.POST.get('pk'))
		if request.POST.get('pk'):
			check = employee_assistance_sop.objects.filter(id = request.POST.get('pk'), dateadded__day=today.day, dateadded__month=today.month).first()
			if check:
				print('exist na...')
				employee_assistance_sop.objects.filter(id = request.POST.get('pk'), dateadded__day=today.day, dateadded__month=today.month).update(
					rq_date = request.POST.get('date_requested'),
					informant = request.POST.get('informant') if request.POST.get('informant') else None,
					informant_contact = request.POST.get('informant_contact') if request.POST.get('informant_contact') else None,
					brief_request = request.POST.get('brief_request') if request.POST.get('brief_request') else None,
					cr_financial_id = request.POST.get('financial') if request.POST.get('financial') else None,
					cr_fa_others = request.POST.get('cr_fa_others') if request.POST.get('cr_fa_others') else None,
					cr_financial_others = request.POST.get('others') if request.POST.get('others') else None,
					cr_mental_id = request.POST.get('mental') if request.POST.get('mental') else None,
					cr_other_id = request.POST.get('other_request') if request.POST.get('other_request') else None,
					docx_valid_id = request.POST.get('validid') if request.POST.get('validid') else None,
					docx_barangay_cert = request.POST.get('barangay_cert') if request.POST.get('barangay_cert') else None,
					docx_case_study = request.POST.get('case_study_report') if request.POST.get('case_study_report') else None,
					docx_clinical_abstract = request.POST.get('clinical_abstract') if request.POST.get('clinical_abstract') else None,
					docx_host_bill = request.POST.get('host_bill') if request.POST.get('host_bill') else None,
					docx_prescription = request.POST.get('prescription') if request.POST.get('prescription') else None,
					docx_lab_request = request.POST.get('lab_request') if request.POST.get('lab_request') else None,
					docx_showing = request.POST.get('document_showing') if request.POST.get('document_showing') else None,
					docx_police_blotter = request.POST.get('police_blotter_cert') if request.POST.get('police_blotter_cert') else None,
					docx_funeral_contract = request.POST.get('Funeral_Contract') if request.POST.get('Funeral_Contract') else None,
					docx_death_cert = request.POST.get('Death_Certificate') if request.POST.get('Death_Certificate') else None,
					docx_permit_to_transfer = request.POST.get('permit_to_transfer') if request.POST.get('permit_to_transfer') else None,
					other_docx = request.POST.get('other_docx') if request.POST.get('other_docx') else None,
					memo_voluntaryContrib = request.POST.get('for_memo') if request.POST.get('for_memo') else None,
					endorsement_letter = request.POST.get('for_financial') if request.POST.get('for_financial') else None,
					result_of_interview = request.POST.get('result_emp') if request.POST.get('result_emp') else None,
					action_provided = request.POST.get('action_provided') if request.POST.get('action_provided') else None,
					remarks = request.POST.get('remarks') if request.POST.get('remarks') else None,
					officer_in_charge = request.POST.get('office_in_charge') if request.POST.get('office_in_charge') else None,
					date_approved = request.POST.get('date_approved') if request.POST.get('date_approved') else None,
				)
			else:
				print('wapa nag exist!')
				employee_assistance_sop.objects.create(
					emp_id = request.POST.get('emp_id'),
					rq_date = request.POST.get('date_requested'),
					informant = request.POST.get('informant') if request.POST.get('informant') else None,
					informant_contact = request.POST.get('informant_contact') if request.POST.get('informant_contact') else None,
					brief_request = request.POST.get('brief_request') if request.POST.get('brief_request') else None,
					cr_financial_id = request.POST.get('financial') if request.POST.get('financial') else None,
					cr_fa_others = request.POST.get('cr_fa_others') if request.POST.get('cr_fa_others') else None,
					cr_financial_others = request.POST.get('others') if request.POST.get('others') else None,
					cr_mental_id = request.POST.get('mental') if request.POST.get('mental') else None,
					cr_other_id = request.POST.get('other_request') if request.POST.get('other_request') else None,
					docx_valid_id = request.POST.get('validid') if request.POST.get('validid') else None,
					docx_barangay_cert = request.POST.get('barangay_cert') if request.POST.get('barangay_cert') else None,
					docx_case_study = request.POST.get('case_study_report') if request.POST.get('case_study_report') else None,
					docx_clinical_abstract = request.POST.get('clinical_abstract') if request.POST.get('clinical_abstract') else None,
					docx_host_bill = request.POST.get('host_bill') if request.POST.get('host_bill') else None,
					docx_prescription = request.POST.get('prescription') if request.POST.get('prescription') else None,
					docx_lab_request = request.POST.get('lab_request') if request.POST.get('lab_request') else None,
					docx_showing = request.POST.get('document_showing') if request.POST.get('document_showing') else None,
					docx_police_blotter = request.POST.get('police_blotter_cert') if request.POST.get('police_blotter_cert') else None,
					docx_funeral_contract = request.POST.get('Funeral_Contract') if request.POST.get('Funeral_Contract') else None,
					docx_death_cert = request.POST.get('Death_Certificate') if request.POST.get('Death_Certificate') else None,
					docx_permit_to_transfer = request.POST.get('permit_to_transfer') if request.POST.get('permit_to_transfer') else None,
					other_docx = request.POST.get('other_docx') if request.POST.get('other_docx') else None,
					memo_voluntaryContrib = request.POST.get('for_memo') if request.POST.get('for_memo') else None,
					endorsement_letter = request.POST.get('for_financial') if request.POST.get('for_financial') else None,
					result_of_interview = request.POST.get('result_emp') if request.POST.get('result_emp') else None,
					action_provided = request.POST.get('action_provided') if request.POST.get('action_provided') else None,
					remarks = request.POST.get('remarks') if request.POST.get('remarks') else None,
					officer_in_charge = request.POST.get('office_in_charge') if request.POST.get('office_in_charge') else None,
					date_approved = request.POST.get('date_approved') if request.POST.get('date_approved') else None,
					)
		else:
			print('wapa nag exist!')
			employee_assistance_sop.objects.create(
				emp_id = request.POST.get('emp_id'),
				rq_date = request.POST.get('date_requested'),
				informant = request.POST.get('informant') if request.POST.get('informant') else None,
				informant_contact = request.POST.get('informant_contact') if request.POST.get('informant_contact') else None,
				brief_request = request.POST.get('brief_request') if request.POST.get('brief_request') else None,
				cr_financial_id = request.POST.get('financial') if request.POST.get('financial') else None,
				cr_fa_others = request.POST.get('cr_fa_others') if request.POST.get('cr_fa_others') else None,
				cr_financial_others = request.POST.get('others') if request.POST.get('others') else None,
				cr_mental_id = request.POST.get('mental') if request.POST.get('mental') else None,
				cr_other_id = request.POST.get('other_request') if request.POST.get('other_request') else None,
				docx_valid_id = request.POST.get('validid') if request.POST.get('validid') else None,
				docx_barangay_cert = request.POST.get('barangay_cert') if request.POST.get('barangay_cert') else None,
				docx_case_study = request.POST.get('case_study_report') if request.POST.get('case_study_report') else None,
				docx_clinical_abstract = request.POST.get('clinical_abstract') if request.POST.get('clinical_abstract') else None,
				docx_host_bill = request.POST.get('host_bill') if request.POST.get('host_bill') else None,
				docx_prescription = request.POST.get('prescription') if request.POST.get('prescription') else None,
				docx_lab_request = request.POST.get('lab_request') if request.POST.get('lab_request') else None,
				docx_showing = request.POST.get('document_showing') if request.POST.get('document_showing') else None,
				docx_police_blotter = request.POST.get('police_blotter_cert') if request.POST.get('police_blotter_cert') else None,
				docx_funeral_contract = request.POST.get('Funeral_Contract') if request.POST.get('Funeral_Contract') else None,
				docx_death_cert = request.POST.get('Death_Certificate') if request.POST.get('Death_Certificate') else None,
				docx_permit_to_transfer = request.POST.get('permit_to_transfer') if request.POST.get('permit_to_transfer') else None,
				other_docx = request.POST.get('other_docx') if request.POST.get('other_docx') else None,
				memo_voluntaryContrib = request.POST.get('for_memo') if request.POST.get('for_memo') else None,
				endorsement_letter = request.POST.get('for_financial') if request.POST.get('for_financial') else None,
				result_of_interview = request.POST.get('result_emp') if request.POST.get('result_emp') else None,
				action_provided = request.POST.get('action_provided') if request.POST.get('action_provided') else None,
				remarks = request.POST.get('remarks') if request.POST.get('remarks') else None,
				officer_in_charge = request.POST.get('office_in_charge') if request.POST.get('office_in_charge') else None,
				date_approved = request.POST.get('date_approved') if request.POST.get('date_approved') else None,
				)
		return JsonResponse({'data': 'Success'})

@csrf_exempt
def delete_info(request):
	if request.method == "POST":
		delete = employee_assistance_sop.objects.filter(id=request.POST.get('id')).delete()
		delete_attachment = emp_assistance_attachment.objects.filter(emp_assistance_id=request.POST.get('id')).delete()
		return JsonResponse({'data': 'success'})


@csrf_exempt
def get_form(request):
	today = date.today()
	id_number = re.split('\[|\]', request.GET.get('fname'))
	data1 = Empprofile.objects.filter(id_number=id_number[1]).first()
	emp_assistance = employee_assistance_sop.objects.filter(emp_id=data1.id, dateadded__day=today.day, dateadded__month=today.month).first()
	context = {
		'data1':data1,
		'date_today': today,
		'emp_assistance': emp_assistance if emp_assistance else '',
		'financial': category_request.objects.all().filter(toa_id=1),
		'mental': category_request.objects.all().filter(toa_id=2),
		'other': category_request.objects.all().filter(toa_id=3),
	}
	return render(request,'backend/Welfare_Intervention/emp_assistance/assistance_layout.html',context)


@csrf_exempt
def print_form(request, pk):
	emp_assistance = employee_assistance_sop.objects.filter(id=pk).first()
	data1 = Empprofile.objects.filter(id=emp_assistance.emp.id).first()
	context = {
		'data1':data1,
		'date_today': today,
		'emp_assistance': emp_assistance if emp_assistance else '',
		'financial': category_request.objects.all().filter(toa_id=1),
		'mental': category_request.objects.all().filter(toa_id=2),
		'other': category_request.objects.all().filter(toa_id=3),
	}
	return render(request,'backend/Welfare_Intervention/emp_assistance/print_assistance_layout.html',context)


@csrf_exempt
def printempassistance(request): #PRINT PR
	rows = request.GET.get('rows', 1000)
	page = request.GET.get('page', 1)
	if request.method == "GET":
		month = request.GET.get('mth')
		if month == "all":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "first_sem":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["01", "06"], rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "second_sem":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["07", "12"], rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "first_quarter":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["01", "03"], rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "second_quarter":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["04", "06"], rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "third_quarter":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["07", "09"], rq_date__year=year).order_by('-rq_date'),rows).page(page)
		elif month == "fourth_quarter":
			datas = Paginator(employee_assistance_sop.objects.all().filter(rq_date__month__range=["10", "12"], rq_date__year=year).order_by('-rq_date'),rows).page(page)						
		else:
			datas = Paginator(employee_assistance_sop.objects.filter(rq_date__month=month, rq_date__year=year).order_by('-rq_date'),rows).page(page)

	context = {
		'data': datas,
		'date': datetime.today()
	}
	return render(request, 'backend/Welfare_Intervention/emp_assistance/printempreport.html', context)


# ---------------------------------------------------------------Incident Report---------------------------------------------------------------------------#

def employee_ir(request):
	if request.method == "POST":
			id_number = re.split('\[|\]', request.POST.get('idnumber'))
			emp = Empprofile.objects.filter(id_number=id_number[1]).first()

			insert1 = incidentreport_db.objects.create(
				emp_id=emp.id,
				category_id = request.POST.get('category'),
				date=request.POST.get('date_of_ir'),
				remarks=request.POST.get('remarks'),
				)
			return JsonResponse({'data': 'success'})

	intervention = "HRWelfare"
	subtitle = "IRDB"
	sub_sub_title = "irdatabase"
	category = incident_data_db.objects.all()
	context = {
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
		'categories': category,
	}
	return render(request,'backend/Welfare_Intervention/Incident_report/incident_report.html', context)

def emp_ir_modal(request,pk):
	data = incidentreport_db.objects.filter(id=pk).first()
	file = ir_attachment_db.objects.filter(incident_report_id=pk).first()
	context = {
		'data': data,
		'files': file,
		'pk':pk,
	}
	return render(request,'backend/Welfare_Intervention/Incident_report/modal_ir.html', context)

def insert_ir_attachment(request):
	if request.method == "POST":
		insert2 = ir_attachment_db.objects.create(
			incident_report_id=request.POST.get('ir_id'),
			attachment_data=request.FILES.get('file'),
			)
		return JsonResponse({'data': 'success'})

@csrf_exempt
def print_irdb(request): #PRINT PR
	if request.method == "GET":
		ctg = request.GET.get('category')
		datas = incidentreport_db.objects.filter(category_id=ctg)

	context = {
		'data':datas,
	}
	return render(request, 'backend/Welfare_Intervention/Incident_report/printir.html', context)