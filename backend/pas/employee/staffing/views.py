from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from datetime import date

from backend.models import Empprofile


@login_required
@permission_required("auth.staffing")
def employee_staffing(request):
    context = {
        'sub_title': 'staffing'
    }
    return render(request, 'backend/pas/employee/staffing/layout.html', context)


@login_required()
@permission_required("auth.staffing")
def os_template_d(request):
    if request.method == "GET":
        as_of = request.GET.get('as_of', date.today())
    context = {
        'as_of': as_of,
        'requested_by': Empprofile.objects.filter(id=request.session['emp_id']).first()
    }
    return render(request, 'backend/pas/employee/staffing/os_template_d.html', context)


@login_required()
@permission_required("auth.staffing")
def os_template_c(request):
    if request.method == "GET":
        as_of = request.GET.get('as_of', date.today())
    context = {
        'as_of': as_of,
        'requested_by': Empprofile.objects.filter(id=request.session['emp_id']).first()
    }
    return render(request, 'backend/pas/employee/staffing/os_template_c.html', context)