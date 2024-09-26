import json
import re

import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.models import Position, Empstatus, Fundsource, Empprofile
from backend.pas.endorsement.models import PasEndorsement, PasEndorsementPeople


@login_required
def endorsement(request):
    if request.method == "POST":
        PasEndorsement.objects.create(
            date=request.POST.get('date'),
            preparedby_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully created a new endorsement.'})

    context = {
        'tab_title': 'Endorsement',
        'title': 'employee',
        'sub_title': 'monitoring',
        'sub_sub_title': 'endorsement'
    }
    return render(request, 'backend/pas/endorsement/endorsement.html', context)


@login_required
def view_shortlisted(request):
    try:
        shortlisted = requests.get('https://caraga-iris.dswd.gov.ph/api/applicants_on_process/',
                                   headers={'Content-Type': 'application/json',
                                       'Authorization': 'Token {}'.format('243f229926212da6b5170d5e604a038d28fec9f4')})
    except Exception as e:
        shortlisted = None

    items = json.loads(shortlisted.text)
    shortlisted_items = [item for item in items if item["workflow_status"] == "Shortlisted"]

    context = {
        'shortlisted': shortlisted_items[:10]
    }
    return render(request, 'backend/pas/endorsement/view_shortlisted.html', context)


@login_required
def page_shortlisted(request):
    try:
        shortlisted = requests.get('https://caraga-iris.dswd.gov.ph/api/applicants_on_process/',
                                   headers={'Content-Type': 'application/json',
                                       'Authorization': 'Token {}'.format('243f229926212da6b5170d5e604a038d28fec9f4')})
    except Exception as e:
        shortlisted = None

    items = json.loads(shortlisted.text)
    shortlisted_items = [item for item in items if item["workflow_status"] == "Shortlisted"]

    vacancies = [item['vacancies'] for item in shortlisted_items]
    unique_vacancies = list(set(vacancies))

    context = {
        'shortlisted': shortlisted_items,
        'unique_vacancies': unique_vacancies
    }
    return render(request, 'backend/pas/endorsement/page_shortlisted.html', context)


@login_required
def endorsement_details(request, pk):
    try:
        if request.method == "POST":
            employee_name = re.split('\[|\]', request.POST.get('employee_name'))
            vice_str = request.POST.get('vice')
            if vice_str:
                vice = re.split('\[|\]', vice_str)
                vice = vice[2].strip()
                vice_idnumber = vice[1].strip()
            else:
                vice = None
                vice_idnumber = None

            employee = Empprofile.objects.filter(id_number=employee_name[1]).first()
            check = PasEndorsementPeople.objects.filter(endorsement_id=pk, emp_id=employee.id)

            if not check:
                PasEndorsementPeople.objects.create(
                    emp_id=employee.id,
                    position_id=request.POST.get('position'),
                    basic_salary=request.POST.get('basic_salary'),
                    premium_rate=request.POST.get('premium_rate'),
                    effectivity_contract=request.POST.get('effectivity_contract'),
                    end_of_contract=request.POST.get('end_of_contract') if request.POST.get('end_of_contract') else None,
                    empstatus_id=request.POST.get('empstatus'),
                    remarks=request.POST.get('remarks'),
                    fundcharge_id=request.POST.get('fundcharge'),
                    vice=vice,
                    vice_id_number=vice_idnumber,
                    endorsement_id=pk
                )

                Empprofile.objects.filter(id_number=employee_name[1]).update(
                    account_number=request.POST.get('account_number')
                )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully added an employee on the endorsement.'})
            else:
                return JsonResponse({'error': True, 'msg': 'Employee already added on the endorsement.'})

        context = {
            'pk': pk,
            'position': Position.objects.filter(status=1).order_by('name'),
            'empstatus': Empstatus.objects.filter(status=1).order_by('name'),
            'fundcharge': Fundsource.objects.filter(status=1).order_by('name')
        }
        return render(request, 'backend/pas/endorsement/endorsement_details.html', context)
    except Exception as e:
        return JsonResponse({'error': True, 'msg': e})


@login_required
@csrf_exempt
def get_employee_details_on_endorsement(request):
    if request.method == "POST":
        employee_name = re.split('\[|\]', request.POST.get('employee_name'))

        if employee_name[0] != '' or employee_name[1] != '':
            employee = Empprofile.objects.filter(id_number=employee_name[1]).first()

            return JsonResponse({'position': employee.position_id,
                                 'salary': employee.salary_rate,
                                 'empstatus': employee.empstatus_id,
                                 'fundcharge': employee.fundsource_id,
                                 'account_number': employee.account_number})


@login_required
def edit_endorsement_details(request, pk):
    if request.method == "POST":
        employee_name = re.split('\[|\]', request.POST.get('employee_name'))
        vice_str = request.POST.get('vice')
        if vice_str:
            vice = re.split('\[|\]', vice_str)
            vice = vice[2].strip()
            vice_idnumber = vice[1].strip()
        else:
            vice = None
            vice_idnumber = None

        employee = Empprofile.objects.filter(id_number=employee_name[1]).first()

        PasEndorsementPeople.objects.filter(id=pk).update(
            emp_id=employee.id,
            position_id=request.POST.get('position'),
            basic_salary=request.POST.get('basic_salary'),
            premium_rate=request.POST.get('premium_rate'),
            effectivity_contract=request.POST.get('effectivity_contract'),
            end_of_contract=request.POST.get('end_of_contract') if request.POST.get('end_of_contract') else None,
            empstatus_id=request.POST.get('empstatus'),
            remarks=request.POST.get('remarks'),
            fundcharge_id=request.POST.get('fundcharge'),
            vice=vice,
            vice_id_number=vice_idnumber,
        )

        Empprofile.objects.filter(id_number=employee_name[1]).update(
            account_number=request.POST.get('account_number')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated an employee on the endorsement.'})
    context = {
        'pk': pk,
        'employee': PasEndorsementPeople.objects.filter(id=pk).first(),
        'position': Position.objects.filter(status=1).order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1).order_by('name'),
        'fundcharge': Fundsource.objects.filter(status=1).order_by('name')
    }
    return render(request, 'backend/pas/endorsement/edit_endorsement_details.html', context)


@login_required
def print_endorsement_details(request, pk):
    context = {
        'data': PasEndorsement.objects.filter(id=pk).first(),
        'people': PasEndorsementPeople.objects.filter(endorsement_id=pk).order_by('emp__pi__user__last_name')
    }
    return render(request, 'backend/pas/endorsement/print_endorsement_details.html', context)