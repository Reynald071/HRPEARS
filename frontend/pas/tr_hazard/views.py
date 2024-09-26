from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.models import Empprofile
from frontend.models import HazardReport, HazardCategory


@login_required
def tr_hazard(request):
    if request.method == "POST":
        HazardReport.objects.create(
            date=request.POST.get('date'),
            category_id=request.POST.get('category'),
            area=request.POST.get('area'),
            accomplishment=request.POST.get('accomplishment'),
            status=0,
            emp_id=request.session['emp_id'],
            date_filed=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully added travel hazard report.'})

    context = {
        'title': 'personnel_transactions',
        'sub_title': 'tr_hazard',
        'sub_sub_title': 'annex_a',
        'category': HazardCategory.objects.order_by('id')
    }
    return render(request, 'frontend/pas/tr_hazard/tr_hazard.html', context)


@login_required
def edit_tr_hazard(request, pk):
    if request.method == "POST":
        HazardReport.objects.filter(id=pk).update(
            date=request.POST.get('date'),
            category_id=request.POST.get('category'),
            area=request.POST.get('area'),
            accomplishment=request.POST.get('accomplishment'),
            status=0,
            emp_id=request.session['emp_id'],
            date_filed=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated your travel hazard report.'})
    context = {
        'travel_report': HazardReport.objects.filter(id=pk).first(),
        'category': HazardCategory.objects.order_by('id')
    }
    return render(request, 'frontend/pas/tr_hazard/edit_tr_hazard.html', context)


@login_required
def print_tr_hazard(request, start_date, end_date):
    context = {
        'report': HazardReport.objects.filter(date__range=[start_date, end_date], emp_id=request.session['emp_id']).prefetch_related(),
        'start_date': start_date,
        'end_date': end_date,
        'today': datetime.today(),
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first()
    }
    return render(request, 'frontend/pas/tr_hazard/print_tr_hazard.html', context)


@login_required
@csrf_exempt
def locked_travel_annex_a(request):
    HazardReport.objects.filter(id=request.POST.get('id')).update(
        status=1
    )
    return JsonResponse({'data': 'success', 'msg': 'You have successfully locked the travel report.'})


@login_required
def tr_hazard_annex_b(request):
    context = {
        'title': 'personnel_transactions',
        'sub_title': 'tr_hazard',
        'sub_sub_title': 'annex_b',
    }
    return render(request, 'frontend/pas/tr_hazard/annex_b.html', context)


@login_required
def print_tr_hazard_annex_b(request, start_date, end_date):
    employee = Empprofile.objects.filter(id=request.session['emp_id']).first()

    print("DIVISION CHIEF ", employee.section.div.div_chief_id)
    division_chief = Empprofile.objects.filter(id=employee.section.div.div_chief_id).first()
    context = {
        'report': HazardReport.objects.filter(date__range=[start_date, end_date],
                                              emp__section__div_id=employee.section.div_id,
                                              status=1).prefetch_related(),
        'start_date': start_date,
        'end_date': end_date,
        'today': datetime.today(),
        'employee': employee,
        'division_chief': division_chief
    }
    return render(request, 'frontend/pas/tr_hazard/print_annex_b.html', context)