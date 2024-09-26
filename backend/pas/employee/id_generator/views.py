import math
import json
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.models import Division, Section, Aoa, Empprofile
from backend.templatetags.tags import force_token_decryption
from frontend.models import Deductionnumbers


@login_required
def id_generator(request):
    context = {
        'tab_title': 'ID Generator',
        'title': 'employee',
        'sub_sub_title': 'id_generator',
        'divisions': Division.objects.order_by('div_name'),
        'sections': Section.objects.order_by('sec_name'),
        'aoa': Aoa.objects.order_by('name')
    }
    return render(request, 'backend/pas/employee/id_generator/layout.html', context)


@login_required
def print_id_custom(request):
    list_variable = request.GET.get('list_variable')
    employee_list = json.loads(list_variable)

    employee = Empprofile.objects.filter(Q(id__in=employee_list)).order_by('pi__user__last_name')

    pagination = employee.count()

    context = {
        'employee': employee,
        'pagination': math.ceil(float(pagination) / 9),
        'today': date.today()
    }
    return render(request, 'backend/pas/employee/id_generator/print_id.html', context)


@login_required
def print_id(request, section_id, aoa_id):
    employee = Empprofile.objects.filter(Q(section_id=force_token_decryption(section_id)) &
                                                Q(aoa_id=force_token_decryption(aoa_id)) &
                                                Q(pi__user__is_active=1) &
                                                ~Q(position__name__icontains='OJT')).order_by('pi__user__last_name')

    pagination = employee.count()

    context = {
        'employee': employee,
        'pagination': math.ceil(float(pagination) / 9),
        'today': date.today()
    }
    return render(request, 'backend/pas/employee/id_generator/print_id.html', context)


@login_required
@csrf_exempt
def id_generate_employee_list(request):
    if request.method == "POST":
        employee = Empprofile.objects.filter(Q(section_id=force_token_decryption(request.POST.get('section_id'))) &
                                                Q(aoa_id=force_token_decryption(request.POST.get('aoa_id'))) &
                                             Q(pi__user__is_active=1) &
                                             ~Q(position__name__icontains='OJT'))

        data = [dict(full_name=row.pi.user.get_fullname,
                     position=row.position.name,
                     area_of_assignment=row.aoa.name if row.aoa_id else None,
                     ) for row in employee]

        return JsonResponse({'data': data})