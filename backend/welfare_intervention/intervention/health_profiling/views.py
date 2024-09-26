from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from datetime import date
from django.db.models import Value, Sum, Count
from django.core.paginator import Paginator
from backend.models import Empprofile
from backend.welfare_intervention.intervention.models import CovidAssistance, vest_db, activity_db, item_db, intervention, sweap_assistance, \
	sweap_gratuity, type_of_request, category_request, doucument_attached, commorbid, health_profile, health_profile_data
from backend.models import Empprofile
from django.db.models.functions import Concat, Upper

from api.wiserv import send_notification
from django.contrib import messages

today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")
import json
import re

@csrf_exempt
def health_profiling(request):
	if request.method == "POST":
		if request.POST.get('emp_id') != None:
			id_number = re.split('\[|\]', request.POST.get('emp_id'))
			emp = Empprofile.objects.filter(id_number=id_number[1]).first()
			data1 = health_profile.objects.filter(emp_id=emp.id).first()

			if data1:
				return JsonResponse({'data': 'Fail'})
			else:
				insert1 = health_profile.objects.create(
					emp_id=emp.id,
					category=request.POST.get('category') if request.POST.get('category') else None,
					)
				return JsonResponse({'data': 'Success'})
		else:
			insert2 = health_profile_data.objects.create(
				health_profile_id=request.POST.get('health_profile_id'),
				emp_commorbid_id=request.POST.get('commorbid'),
				systolic_bs=request.POST.get('systolic') if request.POST.get('systolic') else None,
				diastolic_bs=request.POST.get('diastolic') if request.POST.get('diastolic') else None,
				bs=request.POST.get('bs') if request.POST.get('bs') else None,
				oxemeter=request.POST.get('oxemeter') if request.POST.get('oxemeter') else None,
				result=request.POST.get('result') if request.POST.get('result') else None,
				remarks= request.POST.get('remarks') if request.POST.get('remarks') else None,
				date = request.POST.get('date'),
			)
			
			data_profile = health_profile.objects.filter(id=request.POST.get('health_profile_id')).first()
			number = data_profile.emp.pi.mobile_no
			if request.POST.get('commorbid') == "1":
				message = "Good day, {}! This is DSWD Health Profiling Monitoring Database. Your systolic blood pressure is {} and diastolic blood pressure is {}, The result {}, Date as of {}. HR Cares".format(
					data_profile.emp.pi.user.first_name,
					request.POST.get('systolic'),
					request.POST.get('diastolic'),
					request.POST.get('result'),
					request.POST.get('date'))
				send_notification(message, number, request.session['emp_id'])	
			return JsonResponse({'data': 'Success'})


	interventions = "HRWelfare"
	subtitle = "intervention"
	sub_sub_title = "healthprofile"
	context = {
		'management': True,
		'title': interventions,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
	}
	return render(request,'backend/Welfare_Intervention/health_profiling/health_profiling.html', context)


def modal_emp_profile(request,pk):
	data = health_profile.objects.filter(id=pk).first()
	data1 = health_profile_data.objects.filter(health_profile_id=pk,emp_commorbid_id=1).all().order_by('-date')
	data2 = health_profile_data.objects.filter(health_profile_id=pk).exclude(emp_commorbid_id=1).all().order_by('-date')
	context = {
		'data': data,
		'pk':pk,
		'commorbid': commorbid.objects.all(),
		'data1':data1,
		'data2':data2,
	}
	return render(request,'backend/Welfare_Intervention/health_profiling/emp_profile_modal.html',context)


def individual_print(request):
	if request.method == "GET":
		datas = health_profile_data.objects.filter(emp_commorbid_id__Commorbidity__icontains=request.GET.get('specific'),health_profile_id=request.GET.get('individual_print_name')).all()
		data1 = health_profile.objects.filter(id=request.GET.get('individual_print_name')).first()
	context = {
		'datas': datas,
		'data1':data1,
	}


	return render(request,'backend/Welfare_Intervention/health_profiling/printindividual.html',context)