from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, datetime
from django.db.models import Value, Sum, Count
from django.core.paginator import Paginator
from backend.models import Empprofile
from backend.welfare_intervention.intervention.models import Committee, Sweap_membership, Sweap_mem_committee, Sweap_mem_benes
from backend.models import Empprofile
from django.db.models.functions import Concat, Upper
from django.utils import timezone

from api.wiserv import send_notification
from django.contrib import messages

today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")
import json
import re

@csrf_exempt
@login_required
def sweap_membership_form(request):
	if request.method == "POST":
		id_number = re.split('\[|\]', request.POST.get('idnumber'))
		b_name = request.POST.getlist('b_name[]')
		b_relationship = request.POST.getlist('b_relationship[]')
		age = request.POST.getlist('age[]')
		data = [{'b_name': b_name, 'b_relationship': b_relationship, 'age': age}
					for b_name, b_relationship, age in zip(b_name, b_relationship, age)]
		emp = Empprofile.objects.filter(id_number=id_number[1]).first()
		today = timezone.now()
		year = today.strftime("%Y")
		print('this is year', year)
		check = Sweap_membership.objects.filter(Q(emp_id = emp.id) & Q(dateadded__year=year))
		if not check:
			sweap_mem = Sweap_membership.objects.create(
				emp_id = emp.id,
				encodedby_id = request.user.id)
			if request.POST.get('committee'):
				for row in request.POST.getlist('committee'):
					sweap_com = Sweap_mem_committee(mem_id=sweap_mem.id, committee_id=row)
					sweap_com.save()
			if data:
				for row in data:
					Sweap_mem_benes.objects.create(
						mem_id=sweap_mem.id,
						full_name=row['b_name'].upper(),
						relationship=row['b_relationship'].upper(),
						age=row['age'].upper())
			return JsonResponse({'data': 'success', 'msg': 'Successfully register client for the membership of sweap.'})
		else:
			return JsonResponse({'error': "Client information duplicate entry."})

	context = {
		'management': True,
		'title': 'HRWelfare',
		'sub_title': 'sweap_form',
		'committee': Committee.objects.all()
	}
	return render(request,"backend/Welfare_Intervention/sweap_membership_form/sweap_membership_form.html", context)


@csrf_exempt
@login_required
def update_sweap_form(request, pk):
	if request.method == "POST":
		#Update Sweap Benes
		upb_name = request.POST.getlist('upb_name[]')
		upb_relationship = request.POST.getlist('upb_relationship[]')
		upage = request.POST.getlist('upage[]')
		data = [{'upb_name': upb_name, 'upb_relationship': upb_relationship, 'upage': upage}
			for upb_name, upb_relationship, upage in zip(upb_name, upb_relationship, upage)]

		check = Sweap_mem_benes.objects.filter(mem_id=pk)
		store = [row.id for row in check]
		if check:
			y = 1
			x = 0
			for row in data:
				if y > len(check):
					Sweap_mem_benes.objects.create(
						mem_id=pk,
						full_name=row['upb_name'].upper(),
						relationship=row['upb_relationship'].upper(),
						age=row['upage'].upper())
				else:
					Sweap_mem_benes.objects.filter(id=store[x]).update(
						full_name=row['upb_name'].upper(),
						relationship=row['upb_relationship'].upper(),
						age=row['upage'].upper())
					y += 1
					x += 1
		else:
			for row in data:
				Sweap_mem_benes.objects.create(
					mem_id=pk,
					full_name=row['upb_name'].upper(),
					relationship=row['upb_relationship'].upper(),
					age=row['upage'].upper())
		return JsonResponse({'data': 'success', 'msg': 'Sweap attachment successfully updated!'})

	sweap = Sweap_membership.objects.get(id=pk)
	sweap_com = Sweap_mem_committee.objects.filter(mem_id=pk)
	sweap_bene = Sweap_mem_benes.objects.filter(mem_id=pk)
	context = {
		'sweap': sweap,
		'sweap_com': sweap_com,
		'sweap_bene': sweap_bene,
		'pk': pk,
		'committee': Committee.objects.all()
	}
	return render(request,"backend/Welfare_Intervention/sweap_membership_form/sweap_membership_form_update.html", context)


@csrf_exempt
@login_required
def delete_sweap_benes(request):
    Sweap_mem_benes.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
def upload_attachment(request, pk):
	if request.method == "POST":
		file = request.FILES.get('update_attachment')
		attach = Sweap_membership.objects.filter(id=pk).first()
		if file:
			attach.attachment = file
		attach.save()
		return JsonResponse({'data': 'success', 'msg': 'Sweap attachment successfully updated!'})

	sweap = Sweap_membership.objects.filter(id=pk).first()
	context = {
		'sweap': sweap,
		'pk': pk,
	}
	return render(request,"backend/Welfare_Intervention/sweap_membership_form/sweap_upload_attachments.html", context)