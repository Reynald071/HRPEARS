import re
import io
import csv
import threading
from datetime import datetime, date, timedelta

from dateutil.parser import parse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction

from django.db.models import F, Sum
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_notification, send_sms_notification
from backend.documents.models import DtsDocument, DtsDrn, DtsTransaction, DtsDivisionCc
from backend.leave.forms import LeaveAttachmentForm, CTDOAttachmentForm
from backend.leave.models import LeaveCertificationType, LeaveCertificationTransaction
from backend.libraries.leave.models import LeaveCredits, LeaveType, LeaveApplication, LeavespentApplication, \
    CTDORequests, CTDORandomDates, LeaveCreditHistory, LeaveSubtype, LeaveRandomDates, LeavePrintLogs, LeaveSpent, \
    CTDOPrintLogs, CTDOBalance, CTDOActualBalance, CTDOUtilization, CTDOHistoryBalance, CTDOCoc

from backend.models import Empprofile
from backend.templatetags.tags import force_token_decryption
from backend.views import generate_serial_string
from frontend.leave.views import Balance
from frontend.models import Workhistory
from frontend.templatetags.tags import gamify, generateDRN


@login_required
@permission_required('auth.leave')
def leave_credits(request):
    if request.method == "POST":
        check = LeaveCredits.objects.filter(leavetype_id=request.POST.get('leavetype'), emp_id=request.POST.get('pk'))
        if check:
            return JsonResponse({'error': 'error'})
        else:
            LeaveCredits.objects.create(
                leavetype_id=request.POST.get('leavetype'),
                leave_total=request.POST.get('total'),
                emp_id=request.POST.get('pk'),
                updated_on=datetime.now()
            )
            messages.success(request, 'Leave credits successfully added!')
            return JsonResponse({'data': 'success'})

    search = request.GET.get('search', '')
    id_number = re.split('\[|\]', search)
    if len(id_number) >= 2:
        id_number = id_number[1]
        emp = Empprofile.objects.filter(id_number=id_number).first()
        leave = LeaveCredits.objects.filter(emp_id=emp.id)
    else:
        id_number = id_number[0]
        leave = ''

    context = {
        'employee': Empprofile.objects.filter(Q(id_number=id_number)).first(),
        'leave_type': LeaveType.objects.filter(status=1),
        'leave_credits': leave,
        'management': True,
        'title': 'leave',
        'sub_title': 'leave_credits'
    }
    return render(request, 'backend/leave/leave_credits.html', context)


@login_required
@permission_required('auth.leave')
def update_leave_credits(request, pk):
    if request.method == "POST":
        LeaveCredits.objects.filter(id=pk).update(
            leave_total=request.POST.get('update_total'),
            updated_on=datetime.now()
        )
        messages.success(request, "Leave credits successfully updated!")
        return JsonResponse({'data': 'success'})
    context = {
        'leave_credits': LeaveCredits.objects.filter(id=pk).first(),
        'leave_type': LeaveType.objects.filter(status=1),
    }
    return render(request, 'backend/leave/update_leave_credits.html', context)


@login_required
@permission_required('auth.leave')
def leave_request(request):
    if request.method == "POST":
        leavespent_check = request.POST.get('leavespent_check')

        if leavespent_check:
            leavespent_specify = request.POST.get('leavespent_specify' + leavespent_check)
        else:
            leavespent_specify = request.POST.get('leavespent_specify')

        lasttrack = LeaveApplication.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'LV')

        user_id = re.split('\[|\]', request.POST.get('in_behalf_of'))
        emp = Empprofile.objects.filter(id_number=user_id[1]).first()

        l_application = LeaveApplication(
            tracking_no=track_num,
            leavesubtype_id=request.POST.get('leavesubtype'),
            start_date=None if not request.POST.get('start_date') else request.POST.get('start_date'),
            end_date=None if not request.POST.get('end_date') else request.POST.get('end_date'),
            reasons=request.POST.get('reasons'),
            remarks=None if not request.POST.get('remarks') else request.POST.get('remarks'),
            date_of_filing=request.POST.get('date_of_filing'),
            status=0,
            emp_id=emp.id
        )

        # Save points for booking of event in calendar
        gamify(13, request.session['emp_id'])

        l_application.save()

        LeavespentApplication.objects.create(
            leaveapp_id=l_application.id,
            leavespent_id=leavespent_check,
            status=1 if leavespent_check != "" else None,
            specify=leavespent_specify
        )

        random_dates = request.POST.getlist('dates[]')

        if random_dates[0] != '':
            for row in random_dates:
                LeaveRandomDates.objects.create(
                    leaveapp_id=l_application.id,
                    date=row
                )

        return JsonResponse({'data': 'success', 'tracking_no': track_num})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    current_year = request.GET.get('current_year', datetime.now().year)
    total_leave_pending = LeaveApplication.objects.filter(Q(date_of_filing__year__icontains=current_year),
                                                           status=0).count()
    total_leave_approved = LeaveApplication.objects.filter(Q(date_of_filing__year__icontains=current_year), status=1).count()
    total_leave_canceled = LeaveApplication.objects.filter(Q(date_of_filing__year__icontains=current_year),
                                                           status=2).count()

    context = {
        'leave': Paginator(
            LeaveApplication.objects.filter(Q(date_of_filing__year__icontains=current_year), Q(tracking_no__icontains=search) |
                                            Q(emp__pi__user__last_name__icontains=search) |
                                            Q(emp__pi__user__first_name__icontains=search) |
                                            Q(leavesubtype__name__icontains=search),
                                            Q(status__icontains=status)).order_by('-date_of_filing'), rows).page(page),
        'management': True,
        'current_year': current_year,
        'total_leave_pending': total_leave_pending,
        'total_leave_approved': total_leave_approved,
        'total_leave_canceled': total_leave_canceled,
        'leavesubtype': LeaveSubtype.objects.filter(status=1).order_by('name'),
        'title': 'leave',
        'sub_title': 'leave_request'
    }
    return render(request, 'backend/leave/leave_request.html', context)


@login_required
@permission_required('auth.leave')
def leave_attachment(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(LeaveApplication, pk=pk)
        form = LeaveAttachmentForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()

            return JsonResponse({'data': 'success', 'msg': 'You have successfully uploaded the leave application attachment.'})

    check = LeaveApplication.objects.filter(id=pk, file=None)
    if check:
        check.update(
            file='leave/default.pdf'
        )

    obj = get_object_or_404(LeaveApplication, pk=pk)
    upload_form = LeaveAttachmentForm(instance=obj)

    context = {
        'form': upload_form,
        'pk': pk
    }
    return render(request, 'backend/leave/leave_attachment.html', context)


@login_required
@permission_required('auth.leave')
def view_leave_request(request, pk):
    if request.method == "POST":
        deduct_on = request.POST.getlist('deduct_on[]')
        days = request.POST.getlist('days[]')

        leave = LeaveApplication.objects.filter(id=pk)
        former_leavesubtype = str(leave.first().leavesubtype.name)
        former_inclusive = str(leave.first().get_inclusive())
        leave.update(
            status=1,
            leavesubtype_id=request.POST.get('leave_type'),
            approved_date=datetime.now(),
            additional_remarks=request.POST.get('additional_remarks'),
        )

        LeavespentApplication.objects.filter(leaveapp_id=leave.first().id).update(
            leavespent_id=request.POST.get('leave_spent'),
            specify=request.POST.get('reason_for_leave')
        )

        count = 0
        for row in deduct_on:
            leavetype = LeaveType.objects.filter(id=row).first()
            LeaveCreditHistory.objects.create(
                deduct_on_id=leavetype.id,
                days=days[count],
                application_id=leave.first().id
            )

            LeaveCredits.objects.filter(emp_id=leave.first().emp_id,
                                        leavetype_id=row).update(
                leave_total=F('leave_total') - days[count],
                updated_on=datetime.now()
            )

            count = count + 1

        message = "Mr./Ms. {}! please be informed that your leave request ({}) on {} with tracking number {} has been approved." \
                  "- The My PORTAL Team"\
            .format(leave.first().emp.pi.user.last_name.title(),
                    leave.first().leavesubtype.name,
                    leave.first().get_inclusive(),
                    leave.first().tracking_no)

        if leave.first().emp.pi.mobile_no:
            if request.POST.get('additional_remarks'):
                send_notification("Mr./Ms. {} please be informed that your leave request ({}) on {} has been changed to {} {}. - The My PORTAL Team"
                                  .format(
                                    leave.first().emp.pi.user.last_name.title(),
                                    former_leavesubtype,
                                    former_inclusive,
                                    leave.first().leavesubtype.name,
                                    request.POST.get('additional_remarks')
                                  ), leave.first().emp.pi.mobile_no, request.session['emp_id'], leave.first().emp.id)

            send_notification(message, leave.first().emp.pi.mobile_no, request.session['emp_id'], leave.first().emp.id)

        leave = LeaveApplication.objects.filter(id=pk).first()
        return JsonResponse({'data': 'success',
                             'msg': 'You have successfully approved the leave request with a tracking number {}'.format(
                                 leave.tracking_no)})
    context = {
        'print_attempt': LeavePrintLogs.objects.filter(leaveapp_id=pk),
        'credits_history': LeaveCreditHistory.objects.filter(application_id=pk),
        'leavesubtype': LeaveSubtype.objects.order_by('name'),
        'leave': LeavespentApplication.objects.filter(leaveapp_id=pk).first(),
        'leave_type': LeaveType.objects.filter(status=1)
    }
    return render(request, 'backend/leave/view_leave_request.html', context)


@login_required()
@csrf_exempt
@permission_required('auth.leave')
def get_leave_spent(request, pk):
    leave_spent = LeaveSpent.objects.filter(leavesubtype_id=pk)
    if leave_spent:
        data = [dict(id=row.id, name=row.name) for row in leave_spent]
        return JsonResponse({'data': data})
    else:
        return JsonResponse({'error': True})


@login_required
@csrf_exempt
@permission_required('auth.leave')
def remove_credits_history(request):
    if request.method == "POST":
        LeaveCreditHistory.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.leave')
def cancel_leave_request(request):
    if request.method == "POST":
        leave = LeaveApplication.objects.filter(id=request.POST.get('id'))

        leave.update(
            status=2
        )

        deduct_on = request.POST.getlist('deduct_on[]')
        days = request.POST.getlist('days[]')

        count = 0
        for row in deduct_on:
            LeaveCredits.objects.filter(emp_id=leave.first().emp_id,
                                        leavetype_id=row).update(
                leave_total=F('leave_total') + days[count],
                updated_on=datetime.now()
            )
            count = count + 1

        message = "Good day, {}! Your leave request ({}) on {} with tracking number {} has been cancelled by the administrator. - The My PORTAL Team" \
            .format(leave.first().emp.pi.user.first_name.title(),
                    leave.first().leavesubtype.name,
                    leave.first().get_inclusive(),
                    leave.first().tracking_no)

        if leave.first().emp.pi.mobile_no:
            send_notification(message, leave.first().emp.pi.mobile_no, request.session['emp_id'], leave.first().emp.id)
        return JsonResponse({'data': 'success', 'msg': 'You have successfully cancelled leave request with a tracking number {}'.format(leave.first().tracking_no)})


@login_required
@csrf_exempt
@permission_required('auth.leave')
def uncancel_leave_request(request):
    if request.method == "POST":
        leave = LeaveApplication.objects.filter(id=request.POST.get('id'))

        leave.update(
            status=0
        )

        deduct_on = request.POST.getlist('deduct_on[]')
        days = request.POST.getlist('days[]')

        count = 0
        for row in deduct_on:
            LeaveCredits.objects.filter(emp_id=leave.first().emp_id,
                                        leavetype_id=row).update(
                leave_total=F('leave_total') + days[count],
                updated_on=datetime.now()
            )
            count = count + 1

        message = "Good day, {}! Your leave request ({}) on {} with tracking number {} is now being process for approval. - The My PORTAL Team" \
            .format(leave.first().emp.pi.user.first_name.title(),
                    leave.first().leavesubtype.name,
                    leave.first().get_inclusive(),
                    leave.first().tracking_no)

        if leave.first().emp.pi.mobile_no:
            send_notification(message, leave.first().emp.pi.mobile_no, request.session['emp_id'], leave.first().emp.id)
        return JsonResponse({'data': 'success', 'msg': 'You have successfully uncancelled leave request with a tracking number {}'.format(leave.first().tracking_no)})


@login_required
@permission_required('auth.leave')
def bulk_import_leave_credits(request):
    if request.method == "POST":
        datasource = []

        filename = request.FILES.get('bulk-import')
        if not filename.name.endswith('.csv'):
            raise Http404("File you provided is invalid. Please try again.")
        else:
            try:
                data_set = filename.read().decode('ISO8859')
                io_string = io.StringIO(data_set)
                next(io_string)
                for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                    datasource.append({
                        'id': str(column[0]).strip(),
                        'vl': str(column[1]).strip(),
                        'sl': str(column[2]).strip(),
                        'spl': str(column[3]).strip(),
                    })
            except Exception as e:
                raise Http404(e)

            for emp in datasource:
                haserror = False

                check = Empprofile.objects.filter(id_number=emp['id']).first()

                if check:
                    employee = Empprofile.objects.filter(id_number=emp['id']).first()
                    check_vl = LeaveCredits.objects.filter(leavetype_id=1, emp_id=employee.id)
                    check_sl = LeaveCredits.objects.filter(leavetype_id=2, emp_id=employee.id)
                    check_spl = LeaveCredits.objects.filter(leavetype_id=3, emp_id=employee.id)

                    if check_vl:
                        check_vl.update(leave_total=emp['vl'])
                    else:
                        if re.match(r'^-?\d+(?:\.\d+)?$', emp['vl']) is None:
                            LeaveCredits.objects.create(leavetype_id=1, leave_total=0.00, emp_id=employee.id, updated_on=datetime.now())
                        else:
                            LeaveCredits.objects.create(leavetype_id=1, leave_total=emp['vl'], emp_id=employee.id, updated_on=datetime.now())

                    if check_sl:
                        check_sl.update(leave_total=emp['sl'])
                    else:
                        if re.match(r'^-?\d+(?:\.\d+)?$', emp['sl']) is None:
                            LeaveCredits.objects.create(leavetype_id=2, leave_total=0.00, emp_id=employee.id, updated_on=datetime.now())
                        else:
                            LeaveCredits.objects.create(leavetype_id=2, leave_total=emp['sl'], emp_id=employee.id, updated_on=datetime.now())

                    if check_spl:
                        check_spl.update(leave_total=emp['spl'])
                    else:
                        if re.match(r'^-?\d+(?:\.\d+)?$', emp['spl']) is None:
                            LeaveCredits.objects.create(leavetype_id=3, leave_total=0.00, emp_id=employee.id, updated_on=datetime.now())
                        else:
                            LeaveCredits.objects.create(leavetype_id=3, leave_total=emp['spl'], emp_id=employee.id, updated_on=datetime.now())

        messages.success(request, "Bulk import of leave credits was successful")
        return redirect('leave-credits')


def convert_to_standard(days, hours, minutes):
    # calculate total minutes
    total_minutes = days*8*60 + hours*60 + minutes
    # calculate days, hours and minutes
    standard_days = total_minutes // (8*60)
    standard_hours = (total_minutes % (8*60)) // 60
    standard_minutes = total_minutes % 60
    # return as list
    return [standard_days, standard_hours, standard_minutes]


@login_required
@permission_required('auth.leave')
def admin_ctdo_requests(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    context = {
        'ctdo': Paginator(CTDORequests.objects.filter(Q(emp__pi__user__first_name__icontains=search) |
                                                      Q(emp__pi__user__last_name__icontains=search) |
                                                      Q(tracking_no__icontains=search),
                                                      Q(status__icontains=status)).order_by('-date_filed'), rows).page(page),
        'management': True,
        'tab_title': 'CTDO Requests',
        'title': 'leave',
        'sub_title': 'ctdo_requests'
    }
    return render(request, 'backend/leave/ctdo_request.html', context)


def get_coc_total_balance(emp_id):
    CTDOBalance.objects.filter(date_expiry__lt=date.today()).update(
        status=2
    )

    coc = CTDOActualBalance.objects.filter(cocbal__emp_id=emp_id, cocbal__status=1)

    list_days = []
    list_hours = []
    list_minutes = []
    for row in coc:
        actual_balance = CTDOActualBalance.objects.filter(id=row.id, cocbal__status=1)

        if actual_balance:
            days = int(actual_balance.first().days)
            hours = int(actual_balance.first().hours)
            minutes = int(actual_balance.first().minutes)

            if days == 0 and hours == 0 and minutes == 0:
                CTDOBalance.objects.filter(id=row.cocbal_id).update(status=0)

        list_days.append(int(row.days))
        list_hours.append(int(row.hours))
        list_minutes.append(int(row.minutes))

    minutes = sum(list_minutes) // 60
    total_minutes = sum(list_minutes) - minutes * 60
    hours = sum(list_hours) // 8
    total_hours = (sum(list_hours) - hours * 8) + minutes
    total_days = sum(list_days) + hours

    return [total_days, total_hours, total_minutes]


@login_required
@permission_required('auth.leave')
def generate_ctdo_report(request, month):
    month_str = month.split("-")
    total_application_per_month = CTDORequests.objects.filter(date_filed__year=month_str[0], date_filed__month=month_str[1])

    context = {
        'total_application_per_month': total_application_per_month.count(),
        'total_application_m_per_month': total_application_per_month.filter(emp__pi__gender=1).count(),
        'total_application_f_per_month': total_application_per_month.filter(emp__pi__gender=2).count(),
        'total_pending_application_per_month': total_application_per_month.filter(status__in=[0, 3]).count(),
        'total_pending_application_m_per_month': total_application_per_month.filter(emp__pi__gender=1, status__in=[0, 3]).count(),
        'total_pending_application_f_per_month': total_application_per_month.filter(emp__pi__gender=2, status__in=[0, 3]).count(),
        'total_approved_application_per_month': total_application_per_month.filter(status=1).count(),
        'total_approved_application_m_per_month': total_application_per_month.filter(emp__pi__gender=1, status=1).count(),
        'total_approved_application_f_per_month': total_application_per_month.filter(emp__pi__gender=2,
                                                                                     status=1).count(),
        'total_cancelled_application_per_month': total_application_per_month.filter(status=2).count(),
        'total_cancelled_application_m_per_month': total_application_per_month.filter(emp__pi__gender=1,
                                                                                     status=2).count(),
        'total_cancelled_application_f_per_month': total_application_per_month.filter(emp__pi__gender=2,
                                                                                     status=2).count(),
        'month': datetime.strptime(f'{month_str[0]}-{month_str[1]}', '%Y-%m').date()
    }
    return render(request, 'backend/leave/ctdo_report.html', context)


@login_required
@permission_required('auth.leave')
def admin_ctdo_update(request, pk):
    ctdo = CTDORequests.objects.filter(id=pk).first()
    if request.method == "POST":
        CTDORequests.objects.filter(id=pk).update(
            start_date=None if not request.POST.get('start_date') else request.POST.get('start_date'),
            end_date=None if not request.POST.get('end_date') else request.POST.get('end_date'),
            status=0,
            remarks=request.POST.get('remarks')
        )

        random_dates = request.POST.getlist('dates[]')
        type = request.POST.getlist('type[]')

        data = [{'dates': dates, 'type': type}
                for dates, type in
                zip(random_dates, type)]

        check = CTDORandomDates.objects.filter(ctdo_id=pk)
        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    CTDORandomDates.objects.create(
                        ctdo_id=ctdo.id,
                        date=row['dates'],
                        type=row['type']
                    )
                else:
                    CTDORandomDates.objects.filter(id=store[x]).update(
                        date=row['dates'],
                        type=row['type']
                    )

                    y += 1
                    x += 1
        else:
            for row in data:
                CTDORandomDates.objects.create(
                    ctdo_id=ctdo.id,
                    date=row['dates'],
                    type=row['type']
                )

        CTDOHistoryBalance.objects.filter(ctdoreq_id=pk).update(
            total_days=request.POST.get('total_days'),
            total_hours=request.POST.get('total_hours'),
            total_minutes=request.POST.get('total_minutes'),
            total_u_days=request.POST.get('total_u_days'),
            total_u_hours=request.POST.get('total_u_hours'),
            total_u_minutes=request.POST.get('total_u_minutes'),
        )

        # UPDATE LEAVE APPLICATION
        deduct_on = request.POST.getlist('deduct_on[]')
        days = request.POST.getlist('days[]')

        if not any(value == '' for value in deduct_on):
            count = 0
            for row in deduct_on:
                LeaveCredits.objects.filter(emp_id=ctdo.emp_id,
                                            leavetype_id=row).update(
                    leave_total=F('leave_total') - days[count],
                    updated_on=datetime.now()
                )

                leavetype = LeaveType.objects.filter(id=row).first()
                check = LeaveCreditHistory.objects.filter(deduct_on_id=leavetype.id, application_id=ctdo.id, remarks='CTDO')
                if not check:
                    LeaveCreditHistory.objects.create(
                        deduct_on_id=leavetype.id,
                        days=days[count],
                        application_id=ctdo.id,
                        remarks='CTDO'
                    )
                else:
                    check.update(
                        days=days[count],
                    )

                count = count + 1

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the ctdo requests with a tracking no. {}'.format(ctdo.tracking_no)})

    check_history = CTDOHistoryBalance.objects.filter(ctdoreq_id=pk)

    if not check_history:
        CTDOHistoryBalance.objects.create(
            ctdoreq_id=pk
        )
    else:
        history_balance = CTDOHistoryBalance.objects.filter(ctdoreq_id=pk)
        for row in history_balance:
            total = convert_to_standard(int(row.total_days if row.total_days is not None else 0),
                                        int(row.total_hours if row.total_hours is not None else 0),
                                        int(row.total_minutes if row.total_minutes is not None else 0))
            total_u = convert_to_standard(int(row.total_u_days if row.total_u_days is not None else 0),
                                          int(row.total_u_hours if row.total_u_hours is not None else 0),
                                          int(row.total_u_minutes if row.total_u_minutes is not None else 0))

            CTDOHistoryBalance.objects.filter(id=row.id).update(
                total_days=total[0],
                total_hours=total[1],
                total_minutes=total[2],
                total_u_days=total_u[0],
                total_u_hours=total_u[1],
                total_u_minutes=total_u[2],
            )

    context = {
        'ctdo': ctdo,
        'ctdo_random_dates': CTDORandomDates.objects.filter(ctdo_id=pk),
        'print_attempt': CTDOPrintLogs.objects.filter(ctdo_id=pk),
        'coc_utilization': CTDOUtilization.objects.filter(ctdoreq_id=pk),
        'coc_actual_balance': CTDOActualBalance.objects.filter(cocbal__emp_id=ctdo.emp_id, cocbal__status=1),
        'coc_history_balance': CTDOHistoryBalance.objects.filter(ctdoreq_id=pk).first(),
        'total_days': get_coc_total_balance(ctdo.emp_id)[0],
        'total_hours': get_coc_total_balance(ctdo.emp_id)[1],
        'total_minutes': get_coc_total_balance(ctdo.emp_id)[2],
        'credits_history': LeaveCreditHistory.objects.filter(application_id=pk, remarks='CTDO'),
        'leave_type': LeaveType.objects.filter(status=1),
        'pk': pk,
    }
    return render(request, 'backend/leave/update_ctdo_request.html', context)


def get_first_date(obj):
    dates = obj.cocbal.month_earned.split(',')
    first_date_str = f'{dates[0].strip()}, {dates[-1].strip()}'
    return parse(first_date_str)


@login_required
@csrf_exempt
def auto_utilize_coc_earned_admin(request):
    if request.method == "POST":
        ctdo = CTDORequests.objects.filter(id=request.POST.get('ctdoreq_id')).first()
        actual_balance = (CTDOActualBalance.objects
                          .filter(cocbal__emp_id=ctdo.emp_id, cocbal__status=1)
                          .annotate(total_time=F('days') * 8 * 60 + F('hours') * 60 + F('minutes')))

        actual_balance = list(actual_balance)
        actual_balance.sort(key=get_first_date)

        utilized = []
        remaining = []

        input_days_hours = Balance(None, int(request.POST.get('days')), int(request.POST.get('hours')), 0)

        for row in actual_balance:
            current_balance = Balance(row.id, int(row.days), int(row.hours), int(row.minutes))

            if current_balance.to_minutes() > input_days_hours.to_minutes():
                utilized_amount = input_days_hours.to_minutes()
                new_balance = current_balance.subtract(input_days_hours)
            else:
                utilized_amount = current_balance.to_minutes()
                new_balance = Balance(row.id, 0, 0, 0)

            if utilized_amount > 0:
                days, hours, minutes = convert_to_standard(0, 0, utilized_amount)
                utilized.append(Balance(row.id, days, hours, minutes))
                remaining.append(new_balance)
                days, hours, minutes = convert_to_standard(0, 0, input_days_hours.to_minutes() - utilized_amount)
                input_days_hours = Balance(None, days, hours, minutes)

        for balance in remaining:
            CTDOActualBalance.objects.filter(id=balance.id).update(
                days=balance.days,
                hours=balance.hours,
                minutes=balance.minutes
            )

        for balance in utilized:
            CTDOUtilization.objects.create(
                ctdoreq_id=request.POST.get('ctdoreq_id'),
                cocactualbal_id=balance.id,
                days=balance.days,
                hours=balance.hours,
                minutes=balance.minutes,
                emp_id=ctdo.emp_id,
                status=1
            )

        return JsonResponse({'data': 'success', 'msg': 'Auto utilization completed. You can now select a dates for your ctdo application.'})


@login_required
@permission_required('auth.leave')
def admin_utilize_coc_earned(request, pk, ctdo_id):
    id = force_token_decryption(pk)
    coc = CTDOActualBalance.objects.filter(id=id).first()
    if request.method == "POST":
        if int(request.POST.get('days')) <= int(coc.days) and int(request.POST.get('hours')) <= int(coc.hours) and int(request.POST.get('days')) <= int(coc.minutes):
            CTDOActualBalance.objects.filter(id=id).update(
                days=F('days') - int(request.POST.get('days')),
                hours=F('hours') - int(request.POST.get('hours')),
                minutes=F('minutes') - int(request.POST.get('minutes')),
            )

            CTDOUtilization.objects.create(
                ctdoreq_id=ctdo_id,
                days=request.POST.get('days'),
                hours=request.POST.get('hours'),
                minutes=request.POST.get('minutes'),
                cocactualbal_id=coc.id,
                emp_id=coc.cocbal.emp_id,
                status=1
            )

            return JsonResponse({'data': 'success', 'msg': 'Successfully added! Your earned CoC is now available for your utilization.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Insufficient balance. Please refer to personnel administration section to file your coc earned.'})

    context = {
        'coc': coc,
        'pk': pk,
        'ctdo_id': ctdo_id
    }
    return render(request, 'backend/leave/admin_utilize_coc.html', context)


@login_required
@csrf_exempt
@permission_required('auth.leave')
def admin_ctdo_approve(request):
    if request.method == "POST":
        ctdo = CTDORequests.objects.filter(id=request.POST.get('id')).first()
        CTDORequests.objects.filter(id=request.POST.get('id')).update(status=1)

        if ctdo.start_date:
            s_date = date(ctdo.start_date.year, ctdo.start_date.month, ctdo.start_date.day)
            e_date = date(ctdo.end_date.year, ctdo.end_date.month, ctdo.end_date.day)
            delta = e_date - s_date
            total = delta.days + 1
            LeaveCredits.objects.filter(leavetype_id=4, emp_id=ctdo.emp_id).update(
                leave_total=F('leave_total') - total
            )
        else:
            total = CTDORandomDates.objects.filter(ctdo_id=ctdo.id).count()
            LeaveCredits.objects.filter(leavetype_id=4, emp_id=ctdo.emp_id).update(
                leave_total=F('leave_total') - total
            )

        message = "Good day, {}! Your CTDO request with tracking number {} has been approved. - The My PORTAL Team".format(
            ctdo.emp.pi.user.first_name,
            ctdo.tracking_no)

        if ctdo.emp.pi.mobile_no:
            t = threading.Thread(target=send_sms_notification,
                                 args=(message, ctdo.emp.pi.mobile_no, request.session['emp_id'], ctdo.emp.id))
            t.start()
        return JsonResponse({'data': 'success', 'msg': 'CTDO requests with a tracking_no {} successfully approved.'.format(
            ctdo.tracking_no
        )})


@login_required
@permission_required('auth.leave')
def leave_certification(request):
    context = {
        'tab_title': 'Leave Certification',
        'title': 'leave',
        'sub_title': 'leave_certification',
    }
    return render(request, 'backend/leave/leave_certification.html', context)


@login_required
@permission_required('auth.leave')
def leave_certificate_transaction(request, emp_id):
    employee = Empprofile.objects.filter(id_number=emp_id).first()
    context = {
        'employee': employee,
        'certification_type': LeaveCertificationType.objects.filter(status=1)
    }
    return render(request, 'backend/leave/leave_certification_transaction.html', context)


@login_required
@permission_required('auth.leave')
def leave_certification_layout(request, pk, emp_id):
    employee = Empprofile.objects.filter(id_number=emp_id).first()
    if request.method == "POST":
        LeaveCertificationTransaction.objects.filter(emp_id=employee.id, type_id=pk, status=0).update(
            date_created=datetime.now(),
            created_by_id=request.session['emp_id'],
            content=request.POST.get('content').strip(),
            title=request.POST.get('title'),
            status=1
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully created the leave certificate'})

    first_date = Workhistory.objects.values('we__we_from').filter(emp_id=employee.id).order_by('we__we_from').first()
    last_date = Workhistory.objects.values('we__we_to').filter(emp_id=employee.id).order_by('we__we_to').last()

    check = LeaveCertificationTransaction.objects.filter(emp_id=employee.id, type_id=pk, status=0)
    if not check:
        LeaveCertificationTransaction.objects.create(
            emp_id=employee.id,
            type_id=pk,
            status=0
        )

    transaction = LeaveCertificationTransaction.objects.filter(emp_id=employee.id, type_id=pk, status=0).first()
    context = {
        'today': datetime.today(),
        'lc_type': LeaveCertificationType.objects.filter(id=pk).first(),
        'transaction': transaction,
        'employee': employee,
        'first_date': first_date,
        'last_date': last_date
    }
    return render(request, 'backend/leave/leave_certification_template.html', context)


@login_required
@permission_required('auth.leave')
def edit_leave_certificate(request, pk):
    if request.method == "POST":
        LeaveCertificationTransaction.objects.filter(id=pk).update(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            drn=request.POST.get('drn')
        )
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the leave certificate.'})
    context = {
        'transaction': LeaveCertificationTransaction.objects.filter(id=pk).first()
    }
    return render(request, 'backend/leave/leave_certification_template_edit.html', context)


@login_required
@permission_required('auth.leave')
def generate_drn_lc(request, pk):
    if request.method == "POST":
        with transaction.atomic():
            lasttrack = DtsDocument.objects.order_by('-id').first()
            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'DT')
            lc = LeaveCertificationTransaction.objects.filter(id=pk)
            sender = Empprofile.objects.filter(id=request.session['emp_id']).first()
            id_number = re.split('\[|\]', request.POST.get('get-employee-name'))
            to = Empprofile.objects.filter(id_number=id_number[1]).first()

            document = DtsDocument(
                doctype_id=40,
                docorigin_id=2,
                sender=sender.pi.user.get_fullname,
                subject=lc.first().type.name,
                purpose="For Signature",
                document_date=datetime.now(),
                document_deadline=None,
                tracking_no=track_num,
                creator_id=request.session['emp_id'],
                drn=None
            )

            document.save()

            drn_data = DtsDrn(
                document_id=document.id,
                category_id=lc.first().type.type,
                doctype_id=40,
                division_id=1,
                section_id=1
            )

            drn_data.save()

            generated_drn = generateDRN(document.id, drn_data.id, True)

            if document:
                for x in range(2):
                    DtsTransaction.objects.create(
                        action=x,
                        trans_from_id=request.session['emp_id'],
                        trans_to_id=to.id,
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=document.id
                    )

            DtsDivisionCc.objects.create(
                document_id=document.id,
                division_id=1
            )

            lc.update(
                drn=generated_drn,
                forwarded_to_id=to.id
            )

            return JsonResponse({'data': 'success', 'drn': generated_drn})


@login_required
@permission_required('auth.leave')
def print_leave_certificate(request, pk):
    data = LeaveCertificationTransaction.objects.filter(id=pk).first()
    employee = Empprofile.objects.filter(id=data.emp_id).first()
    first_date = Workhistory.objects.values('we__we_from').filter(emp_id=employee.id).order_by('we__we_from').first()
    last_date = Workhistory.objects.values('we__we_to').filter(emp_id=employee.id).order_by('we__we_to').last()

    context = {
        'today': datetime.today(),
        'data': data,
        'employee': employee,
        'first_date': first_date,
        'last_date': last_date
    }
    return render(request, 'backend/leave/print_leave_certificate.html', context)


@login_required
@permission_required('auth.leave')
def coc_credits(request):
    context = {
        'tab_title': 'Compensatory Overtime Credit',
        'management': True,
        'title': 'leave',
        'sub_title': 'coc_credits'
    }
    return render(request, 'backend/leave/coc_credits.html', context)


@login_required
@permission_required('auth.leave')
def view_coc_utilization(request, pk):
    coc = CTDOBalance.objects.filter(id=pk).first()
    coc_actual_balance = CTDOActualBalance.objects.filter(cocbal_id=pk).first()
    if request.method == "POST":
        actual_balance = convert_to_standard(int(request.POST.get('actual_days')),
                                              int(request.POST.get('actual_hours')),
                                              int(request.POST.get('actual_minutes')))

        CTDOBalance.objects.filter(id=pk).update(
            month_earned=request.POST.get('month_earned'),
            days=actual_balance[0],
            hours=actual_balance[1],
            minutes=actual_balance[2],
            date_expiry=request.POST.get('date_expiry'),
            status=1
        )

        current_balance = convert_to_standard(int(request.POST.get('current_days')),
                                              int(request.POST.get('current_hours')),
                                              int(request.POST.get('current_minutes')))

        CTDOActualBalance.objects.filter(cocbal_id=pk).update(
            days=current_balance[0],
            hours=current_balance[1],
            minutes=current_balance[2]
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the balance.'})

    context = {
        'coc': coc,
        'coc_actual_balance': coc_actual_balance,
        'coc_utilization': CTDOUtilization.objects.filter(emp_id=coc.emp_id, cocactualbal_id=coc_actual_balance.id, status=1)
    }
    return render(request, 'backend/leave/view_coc_utilization.html', context)


@login_required
@permission_required('auth.leave')
def view_coc_credits(request, pk):
    emp = Empprofile.objects.filter(id_number=pk).first()
    if request.method == "POST":
        actual_balance = convert_to_standard(int(request.POST.get('days')), int(request.POST.get('hours')), int(request.POST.get('minutes')))

        balance = CTDOBalance(
            emp_id=emp.id,
            days=actual_balance[0],
            hours=actual_balance[1],
            minutes=actual_balance[2],
            date_expiry=request.POST.get('date_expiry'),
            month_earned=request.POST.get('month_earned'),
            status=1
        )

        balance.save()

        CTDOActualBalance.objects.create(
            cocbal_id=balance.id,
            days=actual_balance[0],
            hours=actual_balance[1],
            minutes=actual_balance[2],
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully added a coc.'})

    CTDOBalance.objects.filter(date_expiry__lt=date.today()).update(
        status=2
    )

    coc = CTDOBalance.objects.filter(emp_id=emp.id)

    list_days = []
    list_hours = []
    list_minutes = []
    for row in coc:
        list_days.append(int(row.days))
        list_hours.append(int(row.hours))
        list_minutes.append(int(row.minutes))

    minutes = sum(list_minutes) // 60
    total_minutes = sum(list_minutes) - minutes * 60
    hours = sum(list_hours) // 8
    total_hours = (sum(list_hours) - hours * 8) + minutes
    total_days = sum(list_days) + hours

    standard = convert_to_standard(total_days, total_hours, total_minutes)

    utilization = CTDOUtilization.objects.filter(emp_id=emp.id, ctdoreq__status__in=[0, 1])
    total_u_days = total_u_hours = total_u_minutes = 0
    total_r_days = total_r_hours = total_r_minutes = 0

    if utilization.exists():
        total = utilization.aggregate(
            total_days=Sum('days'),
            total_hours=Sum('hours'),
            total_minutes=Sum('minutes')
        )

        standard_u = convert_to_standard(int(total['total_days']),
                                         int(total['total_hours']),
                                         int(total['total_minutes']))
        total_u_days = standard_u[0]
        total_u_hours = standard_u[1]
        total_u_minutes = standard_u[2]
    else:
        total_u_days = 0
        total_u_hours = 0
        total_u_minutes = 0

    total_r_days = total_days - total_u_days
    total_r_hours = total_hours - total_u_hours
    total_r_minutes = total_minutes - total_u_minutes

    standard_r = convert_to_standard(total_r_days, total_r_hours, total_r_minutes)

    context = {
        'coc': coc,
        'emp': emp,
        'total_minutes': standard[2],
        'total_hours': standard[1],
        'total_days': standard[0],
        'total_u_minutes': total_u_minutes,
        'total_u_hours': total_u_hours,
        'total_u_days': total_u_days,
        'total_r_minutes': standard_r[2],
        'total_r_hours': standard_r[1],
        'total_r_days': standard_r[0]
    }
    return render(request, 'backend/leave/view_coc_credits.html', context)


@login_required
@csrf_exempt
@permission_required('auth.leave')
def delete_coc(request):
    CTDOBalance.objects.filter(id=request.POST.get('pk')).delete()
    return JsonResponse({'data': 'success', 'msg': 'You have successfully deleted a coc.'})


@login_required
@permission_required('auth.leave')
def print_coc(request, pk):
    id = force_token_decryption(pk)

    coc = CTDOActualBalance.objects.filter(cocbal__emp_id=id, cocbal__status=1).order_by('cocbal__date_expiry')
    list_days = []
    list_hours = []
    list_minutes = []
    for row in coc:
        list_days.append(int(row.days))
        list_hours.append(int(row.hours))
        list_minutes.append(int(row.minutes))

    minutes = sum(list_minutes) // 60
    total_minutes = sum(list_minutes) - minutes * 60
    hours = sum(list_hours) // 8
    total_hours = (sum(list_hours) - hours * 8) + minutes
    total_days = sum(list_days) + hours

    context = {
        'data': LeaveCertificationType.objects.filter(id=3).first(),
        'coc': coc,
        'employee': Empprofile.objects.filter(id=id).first(),
        'today': datetime.today(),
        'total_days': total_days,
        'total_hours': total_hours,
        'total_minutes': total_minutes
    }
    return render(request, 'backend/leave/print_coc.html', context)


@login_required
@permission_required('auth.leave')
def print_coc_previous(request, pk):
    id = force_token_decryption(pk)
    ctdo = CTDORequests.objects.filter(id=id).first()

    context = {
        'data': LeaveCertificationType.objects.filter(id=3).first(),
        'coc': CTDOCoc.objects.filter(ctdoreq_id=id).order_by('expiry_date'),
        'ctdo': ctdo,
        'today': datetime.today(),
    }
    return render(request, 'backend/leave/print_coc_previous.html', context)


@login_required
@permission_required('auth.leave')
def ctdo_attachment(request, pk):
    obj = get_object_or_404(CTDORequests, pk=pk)
    if request.method == "POST":
        form = CTDOAttachmentForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()

            return JsonResponse(
                {'data': 'success', 'msg': 'You have successfully uploaded the ctdo requests attachment.'})

    check = CTDORequests.objects.filter(id=pk, file=None)
    if check:
        check.update(
            file='ctdo/default.pdf'
        )

    upload_form = CTDOAttachmentForm(instance=obj)

    context = {
        'form': upload_form,
        'pk': pk
    }
    return render(request, 'backend/leave/ctdo_attachment.html', context)


@login_required
@permission_required('auth.leave')
def update_coc_drn(request):
    if request.method == "POST":
        CTDORequests.objects.filter(id=request.POST.get('pk')).update(
            drn=request.POST.get('drn'),
            coc_filed=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the DRN.'})


@login_required
@permission_required('auth.leave')
def add_coc_balance_on_certificate(request):
    if request.method == "POST":
        standard = convert_to_standard(int(request.POST.get('days')), int(request.POST.get('hours')), int(request.POST.get('minutes')))

        CTDOCoc.objects.create(
            ctdoreq_id=request.POST.get('pk'),
            month_earned=request.POST.get('month_earned'),
            days=standard[0],
            hours=standard[1],
            minutes=standard[2],
            expiry_date=request.POST.get('date_expiry')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully added a coc history balance.'})


@login_required
@permission_required('auth.leave')
def view_custom_coc_balance(request, pk):
    ctdo = CTDORequests.objects.filter(id=pk).first()
    context = {
        'coc': CTDOCoc.objects.filter(ctdoreq_id=pk).order_by('expiry_date'),
        'ctdo': ctdo
    }
    return render(request, 'backend/leave/view_custom_coc_balance.html', context)


@login_required
@csrf_exempt
@permission_required('auth.leave')
def remove_custom_coc_balance(request):
    if request.method == "POST":
        CTDOCoc.objects.filter(id=request.POST.get('id')).delete()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully removed a coc history balance.'})



@login_required
@csrf_exempt
@permission_required('auth.leave')
def update_custom_coc_balance(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        month_earned = request.POST.get('month_earned')
        days = request.POST.get('days')
        hours = request.POST.get('hours')
        minutes = request.POST.get('minutes')
        expiry_date = request.POST.get('expiry_date')

        # Look up the model instance and update the fields.
        obj = CTDOCoc.objects.get(id=id)
        obj.month_earned = month_earned
        obj.days = days
        obj.hours = hours
        obj.minutes = minutes
        obj.expiry_date = expiry_date
        obj.save()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated a coc history balance.'})


@login_required
@csrf_exempt
@permission_required('auth.leave')
def move_leave_application_to_ctdo(request):
    if request.method == "POST":
        id = request.POST.get('pk')

        leave_application = LeavespentApplication.objects.filter(leaveapp_id=id).first()

        lasttrack = CTDORequests.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'CTDO')

        ctdo = CTDORequests(
            tracking_no=track_num,
            start_date=None,
            end_date=None,
            date_filed=leave_application.leaveapp.date_of_filing,
            emp_id=leave_application.leaveapp.emp_id,
            status=0,
            remarks=None
        )

        ctdo.save()

        if leave_application.leaveapp.start_date:
            start_date = leave_application.leaveapp.start_date
            end_date = leave_application.leaveapp.end_date

            if end_date is None:
                end_date = start_date

            current_date = start_date
            while current_date <= end_date:
                CTDORandomDates.objects.create(
                    ctdo_id=ctdo.id,
                    date=current_date
                )

                current_date += timedelta(days=1)
        else:
            leave_custom_dates = LeaveRandomDates.objects.filter(leaveapp_id=id)

            for row in leave_custom_dates:
                CTDORandomDates.objects.create(
                    ctdo_id=ctdo.id,
                    date=row.date
                )

        LeaveApplication.objects.filter(id=id).delete()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully moved the leave application to ctdo requests'})
