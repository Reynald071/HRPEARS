from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from backend.ipcr.models import IPC_Rating
from backend.models import Empprofile


@login_required
def f_ipcr(request):
    emp = Empprofile.objects.values('section__div_id').filter(id=request.session['emp_id']).first()
    context = {
        'tab_title': 'Individual Performance Contract Rating',
        'title': 'performance_monitoring',
        'sub_title': 'ipcr',
        'div_id': emp['section__div_id']
    }
    return render(request, 'frontend/ipcr/ipcr.html', context)


@login_required
def emp_ipcr(request):
    emp = Empprofile.objects.values('section__div_id').filter(id=request.session['emp_id']).first()
    context = {
        'tab_parent': 'Employee Data',
        'tab_title': 'IPCR Tracker',
        'title': 'profile',
        'sub_title': 'emp_ipcr',
        'div_id': emp['section__div_id']
    }
    return render(request, 'frontend/ipcr/emp_ipcr.html', context)


@login_required
def emp_ipcr_details(request, pk):
    context = {
        'data': IPC_Rating.objects.filter(id=pk).first(),
    }
    return render(request, 'frontend/ipcr/emp_ipcr_details.html', context)
