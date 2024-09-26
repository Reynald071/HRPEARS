import math
from datetime import datetime, date
import socket

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import pusher

from backend.convocation.models import ConvocationQRCode, ConvocationAttendance, ConvocationEvent
from backend.models import Section, Division, Empprofile, Aoa
from backend.templatetags.tags import force_token_decryption, convert_string_to_crypto, convert_crypto_to_string


@login_required
@permission_required("auth.convocation")
def convocation(request):
    if request.method == "POST":
        check = ConvocationEvent.objects.filter(date=request.POST.get('date'),
                                                time=request.POST.get('time'),
                                                status=request.POST.get('status'))
        if not check:
            ConvocationEvent.objects.create(
                date=request.POST.get('date'),
                time=request.POST.get('time'),
                status=request.POST.get('status')
            )
            return JsonResponse({'data': 'success', 'msg': 'You have successfully created an event.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Convocation event already created. Please select another date.'})

    context = {
        'tab_title': 'Convocation',
        'divisions': Division.objects.order_by('div_name'),
        'sections': Section.objects.order_by('sec_name'),
        'aoa': Aoa.objects.order_by('name')
    }
    return render(request, 'backend/convocation/convocation.html', context)


@login_required
@permission_required("auth.convocation")
def get_convocation_qr_link(request, pk):
    context = {
        'event': ConvocationEvent.objects.filter(id=pk).first()
    }
    return render(request, 'backend/convocation/qr_link.html', context)


@login_required
@permission_required("auth.convocation")
def generate_convocation_report(request):
    if request.method == "POST":
        select_date = request.POST.get('date')

        data = ConvocationAttendance.objects.filter(date=select_date)

        division = Division.objects.order_by('-div_name')
        employees = Empprofile.objects.filter(Q(pi__user__is_active=1) &
                                              Q(aoa__name__icontains='Field Office Caraga') &
                                              ~Q(position__name__icontains='OJT'))

        context = {
            'division': division,
            'employees': employees,
            'select_date': select_date,
            'data': data
        }
        return render(request, 'backend/convocation/generate_report.html', context)


def get_qrcode(pk):
    data = ConvocationQRCode.objects.filter(emp_id=pk).first()

    return data.qrcode


@login_required
@csrf_exempt
@permission_required("auth.convocation")
def convocation_generate_employee_list(request):
    if request.method == "POST":
        employee = Empprofile.objects.filter(Q(section_id=force_token_decryption(request.POST.get('section_id'))) &
                                                Q(aoa_id=force_token_decryption(request.POST.get('aoa_id'))) &
                                             Q(pi__user__is_active=1) &
                                             ~Q(position__name__icontains='OJT'))

        for row in employee:
            check = ConvocationQRCode.objects.filter(emp_id=row.id)

            if not check:
                ConvocationQRCode.objects.create(
                    emp_id=row.id,
                    qrcode=str(convert_string_to_crypto(row.id_number))
                )

        data = [dict(full_name=row.pi.user.get_fullname,
                     position=row.position.name,
                     area_of_assignment=row.aoa.name if row.aoa_id else None,
                     crypto=str(get_qrcode(row.id))) for row in employee]

        return JsonResponse({'data': data})


@login_required
@permission_required("auth.convocation")
def convocation_print_qrcode(request, section_id, aoa_id):
    employee = ConvocationQRCode.objects.filter(Q(emp__section_id=force_token_decryption(section_id)) &
                                                Q(emp__aoa_id=force_token_decryption(aoa_id)) &
                                            Q(emp__pi__user__is_active=1) &
                                         ~Q(emp__position__name__icontains='OJT'))

    pagination = employee.count()

    context = {
        'employee': employee,
        'pagination': math.ceil(float(pagination) / 8),
    }
    return render(request, 'backend/convocation/print_qrcode.html', context)


def convocation_attendance(request):
    context = {
        'date': date.today()
    }
    return render(request, 'backend/convocation/attendance.html', context)


def save_attendance(pusher_client, pk, status):
    check = ConvocationQRCode.objects.filter(qrcode=pk)
    if check:
        today = date.today()
        if status == 0:
            check_time_in = ConvocationAttendance.objects.filter(emp_id=check.first().emp_id, date=today, status=0)
            if not check_time_in:
                ConvocationAttendance.objects.create(emp_id=check.first().emp_id, date=today, time=datetime.now(),
                                                     status=0)
        elif status == 1:
            check_time_out = ConvocationAttendance.objects.filter(emp_id=check.first().emp_id, date=today, status=1)
            if not check_time_out:
                ConvocationAttendance.objects.create(emp_id=check.first().emp_id, date=today, time=datetime.now(),
                                                     status=1)

        attendance = ConvocationAttendance.objects.order_by('-id')
        headcount_timein = ConvocationAttendance.objects.filter(date=today, status=0).count()
        headcount_timeout = ConvocationAttendance.objects.filter(date=today, status=1).count()

        data = [{'picture': row.emp.picture.url,
                 'fullname': row.emp.pi.user.get_fullname.upper(),
                 'time': row.time.strftime('%I:%M %p'),
                 'status': 'Time In' if row.status == 0 else 'Time Out'
                 } for row in attendance[:6]]

        headcount = {
            'timein_headcount': headcount_timein,
            'timeout_headcount': headcount_timeout
        }

        pusher_client.trigger('my-channel', 'my-event', data)
        pusher_client.trigger('my-channel', 'headcount', headcount)


def received_qrcode_attendance(request, pk, type):
    try:
        pusher_client = pusher.Pusher(
            app_id='1558037',
            key='46db3be3f3ba5178b147',
            secret='68189c8718215f68f74c',
            cluster='ap1',
            ssl=True
        )

        save_attendance(pusher_client, pk, type)
        return JsonResponse({'data': 'success'})
    except Exception as e:
        pusher_client = pusher.Pusher(
            app_id='1562485',
            key='d69c75fafc9656699c20',
            secret='2226e97c2339465c66b6',
            cluster='ap1',
            ssl=True
        )

        save_attendance(pusher_client, pk, type)
        return JsonResponse({'data': 'success'})


def shareable_convocation_link(request, pk):
    id = force_token_decryption(pk)
    event = ConvocationEvent.objects.filter(id=id).first()
    if request.method == "POST":
        employee = Empprofile.objects.filter(id_number=request.POST.get('id_number'))

        if employee:
            check = ConvocationAttendance.objects.filter(emp_id=employee.first().id, date=event.date, status=event.status)
            if not check:
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)

                ConvocationAttendance.objects.create(
                    emp_id=employee.first().id,
                    time=datetime.now(),
                    status=event.status,
                    date=event.date,
                    ip_address=ip_address
                )
                return JsonResponse({'data': 'success',
                                     'msg': 'You have successfully {}'.format("Time In" if event.status == 0 else "Time Out")})
            return JsonResponse({'error': True, 'msg': "Employee with the id number {} already {}.".format(
                employee.first().id_number,
                "Time In" if event.status == 0 else "Time Out"
            )})
        else:
            return JsonResponse({'error': True, 'msg': "ID Number doesn't exist."})

    context = {
        'event': event,
        'token': pk
    }
    return render(request, 'backend/convocation/shareable_link.html', context)

