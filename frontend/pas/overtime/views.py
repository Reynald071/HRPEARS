import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1

from backend.models import Empprofile
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration
from frontend.pas.overtime.models import OvertimeClaims, OvertimeDetails, Overtime, OvertimeEmployee


@login_required
def overtime_requests(request):
    if request.method == "POST":
        employee = request.POST.getlist('employee[]')
        check = Overtime.objects.filter(status=0, prepared_by_id=request.session['emp_id'])
        if check:
            detail = OvertimeDetails(
                overtime_id=check.id,
                place=request.POST.get('place'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                nature_of_ot=request.POST.get('nature_of_ot'),
                claims_id=request.POST.get('claims')
            )
            detail.save()

            for row in employee:
                id_number = re.split('\[|\]', row)
                employee = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
                OvertimeEmployee.objects.create(
                    emp_id=employee['id'],
                    detail_id=detail.id
                )
        else:
            overtime = Overtime(
                prepared_by_id=request.session['emp_id'],
                status=0
            )
            overtime.save()

            detail = OvertimeDetails(
                overtime_id=overtime.id,
                place=request.POST.get('place'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                nature_of_ot=request.POST.get('nature_of_ot'),
                claims_id=request.POST.get('claims')
            )
            detail.save()

            for row in employee:
                id_number = re.split('\[|\]', row)
                employee = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
                OvertimeEmployee.objects.create(
                    emp_id=employee['id'],
                    detail_id=detail.id
                )

            return JsonResponse({'data': 'success'})
    context = {
        'title': 'personnel_transactions',
        'sub_title': 'overtime_requests',
        'overtime_claims': OvertimeClaims.objects.filter(status=1)
    }
    return render(request, 'frontend/pas/overtime/overtime_request.html', context)


@login_required
def overtime_request_submit(request):
    if request.method == "POST":
        lasttrack = Overtime.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'OT')

        Overtime.objects.filter(status=0, prepared_by_id=request.session['emp_id']).update(
            tracking_no=track_num,
            status=1
        )

        return JsonResponse({'data': 'success',
                             'msg': 'This will serve as your tracking no. {}. Please wait for the reviewal of your '
                                    'overtime request. Thank you :)'.format(track_num)})


@login_required
@csrf_exempt
def overtime_save_as_draft(request):
    if request.method == "POST":
        Overtime.objects.filter(status=0, prepared_by_id=request.session['emp_id']).update(
            status=4
        )
        return JsonResponse({'data': 'success', 'msg': 'Overtime request was saved as draft.'})


@login_required
@csrf_exempt
def move_overtime_draft(request, pk):
    if request.method == "POST":
        Overtime.objects.annotate(hash=SHA1('id')).filter(hash=pk, prepared_by_id=request.session['emp_id']).update(
            status=0
        )
        return JsonResponse({'data': 'success'})


@login_required
def print_ot_request(request, pk):
    context = {
        'overtime': Overtime.objects.annotate(hash=SHA1('id')).filter(hash=pk).first(),
        'details': OvertimeDetails.objects.annotate(hash=SHA1('overtime_id')).filter(hash=pk),
        'oic': PortalConfiguration.objects.filter(key_name='OT INCHARGE').first().key_acronym.split(', ')
    }
    return render(request, 'frontend/pas/overtime/print_ot_request.html', context)
