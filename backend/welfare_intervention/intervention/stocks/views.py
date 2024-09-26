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
	sweap_gratuity
from backend.models import Empprofile
from django.db.models.functions import Concat, Upper

today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")
import json
import re

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg', 'docx', 'xls', 'pdf','xlsx']

def stock_in(request):
	rows = request.GET.get('rows', 20)
	page = request.GET.get('page', 1)

	datas = Paginator(item_db.objects.all().filter(Q(activity_id=2)).order_by('-id'),rows).page(page)

	intervention = "HRWelfare"
	subtitle = "stock"
	sub_sub_title = "stock_in"
	context = {
		'data': datas,
		'management': True,
		'title': intervention,
		'sub_title': subtitle,
	}
	return render(request, 'backend/Welfare_Intervention/stock_in/stocks_in.html', context)


@csrf_exempt
@login_required
def insert_stocks(request):
	if request.method == "POST":
		insert1 = item_db.objects.filter(id=request.POST.get('id')).update(
			inventory = request.POST.get('total_stocks'),
			)
		return JsonResponse({'data': 'Success'})