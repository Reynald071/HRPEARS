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
	sweap_gratuity, type_of_assistance
from backend.models import Empprofile
from django.db.models.functions import Concat, Upper

from api.wiserv import send_notification
from django.contrib import messages

today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")
import json
import re

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg', 'docx', 'xls', 'pdf','xlsx']


def welfare_dashboard(request):
	countmale = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__pi_id__gender__icontains="1").count()
	countfemale = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__pi_id__gender__icontains="2").count()

	countcovidmale = CovidAssistance.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__pi_id__gender__icontains="1").count()
	countcovidfemale = CovidAssistance.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__pi_id__gender__icontains="2").count()

	counthw = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=1).count()
	countPPE = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=2).count()
	counted = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=5).count()
	countrr = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=6).count()
	countss = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=7).count()
	counttii = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=8).count()
	countrfa = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=9).count()


	counthrmdd = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="HRMDD")
	countpromotive = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="Promotive Services Division")
	countprotective = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="Protective Services Division")
	countppd = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="PPD")
	countdrmd = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="DRMD")
	countfmd = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="FMD")
	countadmindiv = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="Administrative Division")
	countord = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="ORD")
	countpppp = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(emp_id__section_id__div_id__div_acronym__icontains="PPPP")

	countjanuary = sweap_assistance.objects.filter(period_applied__month="01",period_applied__year=year).count()
	countfebruary = sweap_assistance.objects.filter(period_applied__month="02",period_applied__year=year).count()
	countmarch = sweap_assistance.objects.filter(period_applied__month="03",period_applied__year=year).count()
	countapril = sweap_assistance.objects.filter(period_applied__month="04",period_applied__year=year).count()
	countmay = sweap_assistance.objects.filter(period_applied__month="05",period_applied__year=year).count()
	countjune = sweap_assistance.objects.filter(period_applied__month="06",period_applied__year=year).count()
	countjuly = sweap_assistance.objects.filter(period_applied__month="07",period_applied__year=year).count()
	countaugust = sweap_assistance.objects.filter(period_applied__month="08",period_applied__year=year).count()
	countseptember = sweap_assistance.objects.filter(period_applied__month="09",period_applied__year=year).count()
	countoctober = sweap_assistance.objects.filter(period_applied__month="10",period_applied__year=year).count()
	countnovember = sweap_assistance.objects.filter(period_applied__month="11",period_applied__year=year).count()
	countdecember = sweap_assistance.objects.filter(period_applied__month="12",period_applied__year=year).count()

	countcovid2020 = CovidAssistance.objects.filter(start__year="2020").count()
	countcovid2021 = CovidAssistance.objects.filter(start__year="2021").count()
	countcovid2022 = CovidAssistance.objects.filter(start__year="2022").count()


	calculatefaceshield = intervention.objects.filter(activity_id='2',item_id='28',date__year=year).aggregate(total=Sum('total')) 
	calculatefacemask = intervention.objects.filter(activity_id='2',item_id='29',date__year=year).aggregate(total=Sum('total')) 
	calculatealcohol = intervention.objects.filter(activity_id='2',item_id='30',date__year=year).aggregate(total=Sum('total')) 
	calculatebunnysuit = intervention.objects.filter(activity_id='2',item_id='31',date__year=year).aggregate(total=Sum('total')) 
	calculategloves = intervention.objects.filter(activity_id='2',item_id='32',date__year=year).aggregate(total=Sum('total')) 
	calculatemultivitamins = intervention.objects.filter(activity_id='2',item_id='33',date__year=year).aggregate(total=Sum('total')) 
	calculatesanitationkit = intervention.objects.filter(activity_id='2',item_id='34',date__year=year).aggregate(total=Sum('total')) 
	calculateheadcover = intervention.objects.filter(activity_id='2',item_id='35',date__year=year).aggregate(total=Sum('total')) 
	calculatefootcover = intervention.objects.filter(activity_id='2',item_id='36',date__year=year).aggregate(total=Sum('total'))
	calculateantigen = intervention.objects.filter(activity_id='2',item_id='39',date__year=year).aggregate(total=Sum('total'))
	calculaterapidtest = intervention.objects.filter(activity_id='2',item_id='38',date__year=year).aggregate(total=Sum('total'))
	calculateswab = intervention.objects.filter(activity_id='2',item_id='40',date__year=year).aggregate(total=Sum('total'))

	counthealthwellness = intervention.objects.all().values('emp_id').annotate(total=Count('emp_id')).filter(activity_id=1)
	
	calculatehw = intervention.objects.filter(activity_id='1',date__year=year).aggregate(total=Sum('total'))
	calculaterpa = intervention.objects.filter(activity_id='10',item_id='39',date__year=year).aggregate(total=Sum('total'))

	interventions = "HRWelfare"
	subtitle = "Dashboard"
	context = {
		'management': True,
		'title': interventions,
		'sub_title': subtitle,

		'male': countmale,
		'female': countfemale,

		'covidmale':countcovidmale,
		'covidfemale':countcovidfemale,

		'counthealthwellness': counthw,
		'countppes':countPPE,
		'countempd':counted,
		'countrrs':countrr,
		'countsss':countss,
		'counttiis':counttii,
		'countfaas':countrfa,

		'hrmdd': counthrmdd.count(),
		'promotive': countpromotive.count(),
		'protective': countprotective.count(),
		'cppd': countppd.count(),
		'drmd': countdrmd.count(),
		'fmd': countfmd.count(),
		'admindiv': countadmindiv.count(),
		'ord': countord.count(),
		'pppp': countpppp.count(),

		'countjan': countjanuary,
		'countfeb': countfebruary,
		'countmar': countmarch,
		'countapr': countapril,
		'countmy': countmay,
		'countjn': countjune,
		'countjl': countjuly,
		'countaug': countaugust,
		'countsept': countseptember,
		'countoct': countoctober,
		'countnov': countnovember,
		'countdec': countdecember,

		'covid2020': countcovid2020,
		'covid2021': countcovid2021,

		'calfs': calculatefaceshield,
		'countfm':calculatefacemask,
		'countalc':calculatealcohol,
		'calbunny': calculatebunnysuit,
		'calgloves': calculategloves,
		'calmulti': calculatemultivitamins,
		'calsani': calculatesanitationkit,
		'calculatehead': calculateheadcover,
		'calculatefc': calculatefootcover,
		'calculateantgen':calculateantigen,
		'calculaterapid':calculaterapidtest,
		'calswab':calculateswab,

		'counthw': calculatehw,
		'calculaterpa': calculaterpa,
	}
	return render(request, 'backend/Welfare_Intervention/Dashboard/dashboard.html', context)

def covidassistance(request):
	intervention = "HRWelfare"
	subtitle = "intervention"
	sub_sub_title = "covidassistance"
	context = {
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
	}
	return render(request,"backend/Welfare_Intervention/covid_assistance/covid_assistance.html", context)

@csrf_exempt
def updatecovid(request):
	if request.method == "POST":
		data = CovidAssistance.objects.filter(id=request.POST.get('id')).first()
		if data.provision == "0":
			data = CovidAssistance.objects.filter(id=data.id).update(
				provision="1",
				)
			msg = "The Employee successfully given Sanitationkit"
			return JsonResponse({'data': 'success', 'Message':msg})
		elif data.provision == "1":
			data = CovidAssistance.objects.filter(id=data.id).update(
				provision="2",
				)
			msg = "The Employee successfully given all the intervention needed"
			return JsonResponse({'data': 'success', 'Message':msg})

@csrf_exempt
@login_required
def insertassistance(request):
	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('fname'))
		emp = Empprofile.objects.filter(id_number=id_number[1]).first()
		insert1 = CovidAssistance.objects.create(
			emp_id = emp.id,
			caseofemp = request.POST.get('case'),
			start = request.POST.get('start'),
			end = request.POST.get('end'),
			)
		return JsonResponse({'data': 'success'})


def printreport(request): #PRINT PR
	rows = request.GET.get('rows', 1000)
	page = request.GET.get('page', 1)
	datas = Paginator(CovidAssistance.objects.filter(provision="2").all(),rows).page(page)
	context = {
		'data' : datas,
		'month': today
	}
	return render(request, 'backend/Welfare_Intervention/covid_assistance/printreport.html',context)


@csrf_exempt
def updatevest(request):
	if request.method == "POST":
		data = vest_db.objects.filter(id=request.POST.get('id')).update(
			status= 1,
			date_returned= today,
			)
		return JsonResponse({'data': 'success'})


@csrf_exempt
def remind_vest(request):
	if request.method == "POST":
		data = vest_db.objects.filter(id=request.POST.get('id')).first()
		number = data.emp.pi.mobile_no
		message = "Good day, {}! This is from DSWD HR Welfare Section. I would like to inform you that the item you borrowed which is the Red Vest is already due based on your filled-up form. Kindly return the borrowed item Asap. Thank you and Godbless!".format(
			data.emp.pi.user.first_name)
		send_notification(message, number, request.session['emp_id'])
		return JsonResponse({'data': 'success'})


def vest_borrower(request):
	search = request.GET.get('search','')
	vestaction = request.GET.get('vestaction','')
	
	rows = request.GET.get('rows', 20)
	page = request.GET.get('page', 1)


	intervention = "HRWelfare"
	subtitle = "intervention"
	sub_sub_title = "vest_borrower"
	context = {
		# 'data': datas,
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
	}
	return render(request, 'backend/Welfare_Intervention/vest_borrower/vest_borrower.html', context)


@csrf_exempt
@login_required
def insertvest(request):
	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('fname'))
		data = vest_db.objects.filter(emp_id=id_number[1]).first()
		if data:
			data1 = vest_db.objects.filter(emp_id=id_number[1],status=0).first()
			if data1:
				return JsonResponse({'data':'Fail'})
			else:
				updatevest = vest_db.objects.filter(emp_id=id_number[1]).update(
					no_of_days = request.POST.get('case'),
					date_borrowed = request.POST.get('start'),
					status = 0,
					)
				return JsonResponse({'data': 'Success'})
		else: 
			insert1 = vest_db.objects.create(
				emp_id = id_number[1],
				no_of_days = request.POST.get('case'),
				date_borrowed = request.POST.get('start'),
				)
			return JsonResponse({'data': 'Success'})


def hrwactivity(request):
	# uid = request.session['emp_id']
	month = today.strftime("%m")
	year = today.strftime("%Y")
	rows = request.GET.get('rows', 20)
	page = request.GET.get('page', 1)

	activity = activity_db.objects.all()
	item = item_db.objects.all()

	# search = request.GET.get('search','')
	# actvty = request.GET.get('activity','')
	# itm = request.GET.get('itm','')

	# if request.GET.get('search'):
	# 	id_number = re.split('\[|\]', search)
	# 	emp = Empprofile.objects.filter(id_number=id_number[1]).first()
	# 	hrintervention = Paginator(intervention.objects.all().filter(emp_id=emp.id,date__year=year).order_by('-id'),rows).page(page)
	# elif request.GET.get('activity'):
	# 	hrintervention = Paginator(intervention.objects.all().filter(Q(activity_id__activity__icontains=actvty,date__year=year)).order_by('-id'),rows).page(page)
	# elif request.GET.get('itm'):
	# 	hrintervention = Paginator(intervention.objects.all().filter(Q(item_id__item__icontains=itm,date__year=year)).order_by('-id'),rows).page(page)
	# else:
	# 	hrintervention = Paginator(intervention.objects.all().filter(date__year=year).order_by('-id'),rows).page(page)

	title = "HRWelfare"
	subtitle = "intervention"
	sub_sub_title = "hrw_activity"
	context = {
		'management': True,
		'title': title,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,

		'act': activity,
		'itms': item,
	}
	return render(request,'backend/Welfare_Intervention/hrw_activity/hrw_activity.html', context)

def printinterventionreport(request):
	year = today.strftime("%Y")

	calculatefaceshield = intervention.objects.filter(activity_id='2',item_id='28',date__year=year).aggregate(total=Sum('total'))
	calculatefacemask = intervention.objects.filter(activity_id='2',item_id='29',date__year=year).aggregate(total=Sum('total'))
	calculatealcohol = intervention.objects.filter(activity_id='2',item_id='30',date__year=year).aggregate(total=Sum('total'))
	calculatebunnysuit = intervention.objects.filter(activity_id='2',item_id='31',date__year=year).aggregate(total=Sum('total'))
	calculategloves = intervention.objects.filter(activity_id='2',item_id='32',date__year=year).aggregate(total=Sum('total'))
	calculatemultivitamins = intervention.objects.filter(activity_id='2',item_id='33',date__year=year).aggregate(total=Sum('total'))
	calculatesanitationkit = intervention.objects.filter(activity_id='2',item_id='34',date__year=year).aggregate(total=Sum('total'))
	calculateheadcover = intervention.objects.filter(activity_id='2',item_id='35',date__year=year).aggregate(total=Sum('total'))
	calculatefootcover = intervention.objects.filter(activity_id='2',item_id='36',date__year=year).aggregate(total=Sum('total'))
	context ={
		'month': today,

		'calfs': calculatefaceshield,
		'countfm': calculatefacemask,
		'countalc': calculatealcohol,
		'calbunny': calculatebunnysuit,
		'calgloves': calculategloves,
		'calmulti': calculatemultivitamins,
		'calsani': calculatesanitationkit,
		'calculatehead': calculateheadcover,
		'calculatefc': calculatefootcover,
	}
	return render(request,'backend/Welfare_Intervention/hrw_activity/printactivityreport.html', context)

@csrf_exempt
@login_required
def insertactivity(request):
	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('idnumber'))
		emp = Empprofile.objects.filter(id_number=id_number[1]).first()
		itemid = request.POST.get('item_db')
		hrintervention = intervention.objects.filter(emp_id=emp.id, item_id=itemid)
		if hrintervention:
			return JsonResponse({'data': 'fail'})
		else:
			insert1 = intervention.objects.create(
				emp_id=emp.id,
				date=today,
				activity_id=request.POST.get('activity_db'),
				item_id=itemid,
				total=request.POST.get('total'),
				)
			update = item_db.objects.filter(id=itemid).update(
				inventory=request.POST.get('total_stocks') if request.POST.get('total_stocks') else None,
				)
			return JsonResponse({'data': 'success'})

def modalforintervention(request,pk):
	intervention_update = intervention.objects.filter(id=pk).first()
	item_inventory = item_db.objects.filter(id=intervention_update.item_id).first()
	context = {
		'intervention': intervention_update,
		'inventory': item_inventory,
	}
	return render(request,'backend/Welfare_Intervention/hrw_activity/modal_activity.html', context)

def updateintervention(request):
	update_intervention = intervention.objects.filter(id=request.POST.get('empid')).update(
		total = request.POST.get('activitytotal')
		)
	update = item_db.objects.filter(item=request.POST.get('item')).update(
		inventory=request.POST.get('total_stock') if request.POST.get('total_stock') else None,
		)
	return JsonResponse({'data': 'success'})

@csrf_exempt
def showitem(request): #DYNAMIC DISPLAY IN SELECT2
	itm = item_db.objects.all().filter(activity_id=request.POST.get('src'))
	data = [dict(id=row.id, item=row.item) for row in itm]
	return JsonResponse({'data': data})

@csrf_exempt
def show_inventory(request):
	if request.POST.get('activity_id') == "":
		Fail = "FAIL SAVE"
		return JsonResponse({'data': Fail})
	else:
		itm = item_db.objects.filter(id=request.POST.get('activity_id'))
		data = [dict(id=row.id, inventory=row.inventory) for row in itm]
		return JsonResponse({'data': data})


@csrf_exempt
def update_sweap(request):
	if request.method == "POST":
		share = request.POST.get('share_contrib')
		update = sweap_assistance.objects.filter(id=request.POST.get("empid")).update(
			share_contrib=request.POST.get('share_contrib'),
			)
		return JsonResponse({'data': 'success','test':share})

@csrf_exempt
def sweapassistance(request):
	month = today.strftime("%m")
	year = today.strftime("%Y")
	search = request.GET.get('search','')
	monthly = request.GET.get('month','')
	toa = request.GET.get('toa', '')
	rows = request.GET.get('rows', 20)
	page = request.GET.get('page', 1)

	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('idnumber'))
		display_first = sweap_assistance.objects.filter(emp_id=id_number[1],period_applied__year=year).first()
		if display_first:
			update = sweap_assistance.objects.filter(id=display_first.id).update(
				entry = 1,
				)	
			insert = sweap_assistance.objects.create(
				emp_id=id_number[1],
				typeofassistant=request.POST.get('typeofassistant'),
				particular=request.POST.get('particular'),
				amount_excess=request.POST.get('amountexcess'),
				amount_extended=request.POST.get('amountextended'),
				relationship=request.POST.get('relation'),
				share_contrib=request.POST.get('sharecontribution') if request.POST.get('sharecontribution') else None,
				period_applied=request.POST.get('date'),
				entry=1,
				 )
			return JsonResponse({'data': 'success'})
		else:
			insert = sweap_assistance.objects.create(
				emp_id=id_number[1],
				typeofassistant=request.POST.get('typeofassistant'),
				particular=request.POST.get('particular'),
				amount_excess=request.POST.get('amountexcess'),
				amount_extended=request.POST.get('amountextended'),
				relationship=request.POST.get('relation'),
				share_contrib=request.POST.get('sharecontribution') if request.POST.get('sharecontribution') else None,
				period_applied=request.POST.get('date'),
				entry=0,
				 )
			return JsonResponse({'data': 'success'})

	if request.GET.get('month'):
		datas = Paginator(sweap_assistance.objects.all().filter(Q(period_applied__month=monthly,period_applied__year=year)).order_by('-id'),rows).page(page)
	elif request.GET.get('search'):
		emp_id = re.split('\[|\]', search)
		datas = Paginator(sweap_assistance.objects.all().filter(Q(emp_id__icontains=emp_id[1],period_applied__year=year)).order_by('-id'),rows).page(page)
	elif request.GET.get('toa'):
		datas = Paginator(sweap_assistance.objects.all().filter(Q(typeofassistant__icontains=toa,period_applied__year=year)).order_by('-id'), rows).page(page)
	else:
		datas = Paginator(sweap_assistance.objects.all().filter(period_applied__year=year).order_by('-id'),rows).page(page)

	intervention = "HRWelfare"
	subtitle = "sweap_assistance"
	sub_sub_title = "sweapfinancial"
	context = {
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
		'data':datas,
	}
	return render(request,'backend/Welfare_Intervention/sweap_assistance/sweap_assistance.html', context)

@csrf_exempt
def delete_sweap(request):
	if request.method == "POST":
		print("sample")
		delete = sweap_assistance.objects.filter(id=request.POST.get('id')).delete()
		return JsonResponse({'data': 'success'})

@csrf_exempt
def printsweapreport(request): #PRINT PR
	year = today.strftime("%Y")
	rows = request.GET.get('rows', 1000)
	page = request.GET.get('page', 1)
	if request.method == "GET":
		month = request.GET.get('mth')
		if month == "ALL":
			datas = Paginator(sweap_assistance.objects.filter(period_applied__year=year).order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=year).aggregate(total_payment=Sum('share_contrib'))
		elif month == "Mortuary":
			datas = Paginator(sweap_assistance.objects.filter(typeofassistant=month,period_applied__year="2021").order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=year).aggregate(total_payment=Sum('share_contrib'))
		elif month == "Medical":
			datas = Paginator(sweap_assistance.objects.filter(typeofassistant=month,period_applied__year="2021").order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=year).aggregate(total_payment=Sum('share_contrib'))
		elif month == "2023":
			datas = Paginator(sweap_assistance.objects.filter(period_applied__year=month).order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=month).aggregate(total_payment=Sum('share_contrib'))
		elif month == "2022":
			datas = Paginator(sweap_assistance.objects.filter(period_applied__year=month).order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=month).aggregate(total_payment=Sum('share_contrib'))
		elif month == "2021":
			datas = Paginator(sweap_assistance.objects.filter(period_applied__year=month).order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__year=month).aggregate(total_payment=Sum('share_contrib'))			
		else:
			datas = Paginator(sweap_assistance.objects.filter(period_applied__month=month, period_applied__year=year).order_by('-id'),rows).page(page)
			calculate = sweap_assistance.objects.filter(period_applied__month=month, period_applied__year=year).aggregate(total_payment=Sum('share_contrib'))

	context = {
		'data':datas,
		'calculate': calculate,
		'year': year,
	}
	return render(request, 'backend/Welfare_Intervention/sweap_assistance/printreport.html', context)

@csrf_exempt
def gratuity_pay(request):
	search = request.GET.get('search', '')
	toa = request.GET.get('toa', '')
	rows = request.GET.get('rows', 20)
	page = request.GET.get('page', 1)

	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('idnumber'))
		emp = Empprofile.objects.filter(id_number=id_number[1]).first()
		insert1 = sweap_gratuity.objects.create(
			emp_id=emp.id,
			type_of_assistance=request.POST.get('typeofassistant'),
			date_emp_start=request.POST.get('dt_start'),
			date_emp_end=request.POST.get('dt_end'),
			emp_yearinservice=request.POST.get('yr_serve'),
			share_contrib=request.POST.get('share'),
			amount_recieved=request.POST.get('am_recieved'),
			)
		return JsonResponse({'data': 'success'})

	intervention = "HRWelfare"
	subtitle = "sweap_assistance"
	sub_sub_title = "gratuity_pay"
	context = {
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
		'sub_sub_title': sub_sub_title,
	}
	return render(request,'backend/Welfare_Intervention/sweap_gratuitypay/sweap_gratuity_pay.html', context)

@login_required
def filter_employee_inactive(request):
    if request.method == "GET":
        json = []
        employee = Empprofile.objects.filter(Q(pi__user__first_name__icontains=request.GET.get('query', '')) |
                                               Q(pi__user__last_name__icontains=request.GET.get('query', ''))).order_by('pi__user__first_name')[:10]
        if employee:
            for row in employee:
                json.append("[{}] {}".format(row.id_number, row.pi.user.get_fullname.upper()))

            return JsonResponse(json, safe=False)
        else:
            return JsonResponse(json, safe=False)

@csrf_exempt
def delete_gratuity(request):
	if request.method == "POST":
		delete = sweap_gratuity.objects.filter(id=request.POST.get('id')).delete()
		return JsonResponse({'data': 'success'})

def printgratuity(request): #PRINT PR
	rows = request.GET.get('rows', 1000)
	page = request.GET.get('page', 1)
	datas = Paginator(sweap_gratuity.objects.filter().order_by('-id'),rows).page(page)
	context = {
		'data':datas,
	}
	return render(request, 'backend/Welfare_Intervention/sweap_gratuitypay/printreport.html', context)
	


def hrwelfare_intervention(request):
	context = {
		'management': True,
		'title' : 'HRWelfare',
		'sub_title': 'intervention_database'
	}
	return render(request, 'backend/Welfare_Intervention/intervention.html',context)


#@csrf_exempt
#@login_required
#def insertassistance(request):
#	if request.method == "POST":
#		fname = request.POST.getlist('fname[]')
#		case = request.POST.getlist('case[]')
#		start = request.POST.getlist('start[]')
#		end = request.POST.getlist('end[]')
#		provision = request.POST.getlist('provision[]')
#
#
#		data = [{'fname': i, 'case': c, 'start': s, 'end': e, 'provision': p}
#			for i, c, s, e, p in zip(fname, case, start, end, provision)]
#
#		for row in data:
#			id_number[] = re.split('\[|\]', row['fname'])
#			print("THIS IS EXAMPLE", id_number[][1])
#
#			insert = CovidAssistance.objects.create(
#				empid = row['id_number'],
#				caseofemp = row['case'],
#				start = row['start'],
#				end = row['end'],
#				provision = row['provision'],
#				)
#		return JsonResponse({'data': 'success'})
#	return render(request,'PR/covidassistance/modalforassistance.html')

