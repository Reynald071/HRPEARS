import threading
from datetime import datetime, date
import re

from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_notification
from backend.libraries.leave.models import LeaveSubtype, LeaveCredits, LeaveSpent, LeaveApplication, \
    LeavespentApplication, LeavePermissions, LeaveRandomDates, CTDORequests, CTDORandomDates, LeavePrintLogs, \
    CTDOPrintLogs, CTDOBalance, CTDOUtilization, CTDOActualBalance, CTDOHistoryBalance, CTDOCoc

from backend.models import Section, Division, Designation, Empprofile, AuthUserUserPermissions, AuthUser
from backend.templatetags.tags import force_token_decryption
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration
from frontend.templatetags.tags import gamify


@login_required
def leave_application(request):
    if request.method == "POST":
        leavespent_check = request.POST.get('leavespent_check')

        if leavespent_check:
            leavespent_specify = request.POST.get('leavespent_specify' + leavespent_check)
        else:
            leavespent_specify = request.POST.get('leavespent_specify')

        lasttrack = LeaveApplication.objects.filter(status=0).last()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'LV')

        l_application = LeaveApplication(
            tracking_no=track_num,
            leavesubtype_id=request.POST.get('leavesubtype'),
            start_date=None if not request.POST.get('start_date') else request.POST.get('start_date'),
            end_date=None if not request.POST.get('end_date') else request.POST.get('end_date'),
            reasons=request.POST.get('reasons'),
            remarks=None if not request.POST.get('remarks') else request.POST.get('remarks'),
            date_of_filing=datetime.now(),
            status=0,
            emp_id=request.session['emp_id']
        )

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

    emp = Empprofile.objects.filter(id=request.session['emp_id']).first()
    context = {
        'leavesubtype': LeavePermissions.objects.filter(empstatus_id=emp.empstatus_id, leavesubtype__status=1).order_by('leavesubtype__name'),
        'leave_credits': LeaveCredits.objects.filter(emp_id=request.session['emp_id']),
        'date': datetime.now(),
        'tab_parent': 'Leave Management',
        'tab_title': 'Leave Requests',
        'title': 'leave_management',
        'sub_title': 'user_leave'
    }
    return render(request, 'frontend/leave/leave_application.html', context)


@login_required
def edit_leave_application(request, pk):
    if request.method == "POST":
        leavespent_check = request.POST.get('leavespent_check')

        if leavespent_check:
            leavespent_specify = request.POST.get('leavespent_specify' + leavespent_check)
        else:
            leavespent_specify = request.POST.get('leavespent_specify')

        leave_spent = LeavespentApplication.objects.filter(leaveapp_id=pk).first()

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        LeaveApplication.objects.filter(id=pk).update(
            leavesubtype_id=request.POST.get('leavesubtype'),
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            reasons=request.POST.get('reasons'),
            remarks=None if not request.POST.get('remarks') else request.POST.get('remarks'),
            date_of_filing=request.POST.get('date_of_filing') if request.POST.get('date_of_filing') else F('date_of_filing'),
            status=0,
        )

        LeavespentApplication.objects.filter(id=leave_spent.id).update(
            leavespent_id=leavespent_check,
            status=1 if leavespent_check != "" else None,
            specify=leavespent_specify
        )

        random_dates = request.POST.getlist('dates[]')
        if random_dates[0] != '':
            custom_dates = [str(row.date) for row in LeaveRandomDates.objects.filter(leaveapp_id=pk)]
            comparison = list(set(random_dates) - set(custom_dates))

            for row in comparison:
                LeaveRandomDates.objects.create(
                    leaveapp_id=pk,
                    date=row
                )

            LeaveRandomDates.objects.filter(~Q(date__in=random_dates), Q(leaveapp_id=pk)).delete()

        return JsonResponse({'data': 'success', 'tracking_no': leave_spent.leaveapp.tracking_no})

    permission = AuthUserUserPermissions.objects.filter(
        user_id=request.user.id,
        permission_id=36
    )
    superadmin = AuthUser.objects.filter(id=request.user.id).first()
    if permission or superadmin.is_superuser:
        emp = Empprofile.objects.filter(id=1).first()
    else:
        emp = Empprofile.objects.filter(id=request.session['emp_id']).first()

    context = {
        'leavesubtype': LeavePermissions.objects.filter(empstatus_id=emp.empstatus_id),
        'leave_random_dates': LeaveRandomDates.objects.filter(leaveapp_id=pk),
        'leave': LeavespentApplication.objects.filter(leaveapp_id=pk).first(),
        'pk': pk,
    }
    return render(request, 'frontend/leave/edit_leave_application.html', context)


@login_required
@csrf_exempt
def cancel_leave(request):
    if request.method == "POST":
        LeaveApplication.objects.filter(id=request.POST.get('id'), emp_id=request.session['emp_id']).update(
            status=2
        )
        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
def get_leavespent(request):
    leave_spent = LeaveSpent.objects.filter(leavesubtype_id=request.POST.get('id'), status=1)
    leave_subtype = LeaveSubtype.objects.filter(id=request.POST.get('id')).first()
    data = [dict(id=row.id, name=row.name, is_specify=row.is_specify) for row in leave_spent]
    return JsonResponse({'data': data, 'has_reason': leave_subtype.has_reason, 'remarks_text': leave_subtype.remarks_text,
                         'with_days': leave_subtype.with_days})


@login_required
def print_leaveapp(request, pk):
    leave = LeaveApplication.objects.filter(id=pk).first()

    if leave.leavesubtype_id == 12:     # Monetization ID
        designation = Designation.objects.filter(emp_id=leave.emp_id, id=1).first()
    else:
        designation = Designation.objects.filter(emp_id=leave.emp_id).first()

    if designation:
        first_level = PortalConfiguration.objects.filter(id=5).first()
        first_level_pos = first_level.key_name
        second_level = PortalConfiguration.objects.filter(id=6).first()
        second_level_pos = second_level.key_name
        classes = 3
    else:
        head = Designation.objects.filter(emp_id=leave.emp_id).first()
        div_head = Division.objects.filter(div_chief_id=leave.emp_id).first()
        sec_head = Section.objects.filter(sec_head_id=leave.emp_id).first()

        if div_head:
            if div_head.designation_id == 1 or head:  # PPD
                first_level = ""
                first_level_pos = ""
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            else:
                first_level = div_head.designation.emp_id
                first_level_pos = Designation.objects.filter(emp_id=div_head.designation.emp_id).first()
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            classes = 2
        elif sec_head:
            if sec_head.div.designation_id == 1:  # PPD
                first_level = ""
                first_level_pos = ""
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            else:
                first_level = sec_head.div.designation.emp_id
                first_level_pos = Designation.objects.filter(emp_id=sec_head.div.designation.emp_id).first()
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            classes = 2
        else:
            emp = Empprofile.objects.filter(id=leave.emp_id).first()
            first_level = emp.section.div.div_chief_id
            first_level_pos = Division.objects.filter(div_chief_id=emp.section.div.div_chief_id).first()

            if emp.aoa.name != "Field Office Caraga":
                second_level = emp.section.div.designation.emp_id
                second_level_pos = Designation.objects.filter(emp_id=emp.section.div.designation.emp_id).first()
            else:
                fo_staff = PortalConfiguration.objects.filter(key_name='Leave Second Level Signatory').first()
                second_level = fo_staff.key_acronym if fo_staff.key_acronym else None
                check = Designation.objects.filter(emp_id=fo_staff.key_acronym)
                if check:
                    second_level_pos = check
                else:
                    second_level_pos = None
            classes = 1

    context = {
        'leave': LeavespentApplication.objects.filter(leaveapp_id=pk,
                                                      leaveapp__emp_id=leave.emp_id).first(),
        'leavesubtype': LeaveSubtype.objects.filter(status=1).order_by('order'),
        'first_level': first_level,
        'first_level_pos': first_level_pos,
        'second_level': second_level,
        'second_level_pos': second_level_pos,
        'classes': classes,
        'personnel_officer': PortalConfiguration.objects.filter(key_name='Personnel Officer').first()
    }
    return render(request, 'frontend/leave/print_leave_revised_2020_npmo.html', context)


@login_required
def set_signature_leave(request):
    if request.POST.get('recommended_by'):
        recommended_by = re.split('\[|\]', request.POST.get('recommended_by'))
        recommended_by_name = Empprofile.objects.filter(id_number=recommended_by[1]).first()
        check_recommended_by_position = Designation.objects.filter(emp_id=recommended_by_name.id).first()
        if check_recommended_by_position:
            recommended_by_position = check_recommended_by_position.name
        else:
            division = Division.objects.filter(div_chief_id=recommended_by_name.id).first()
            if division:
                recommended_by_position = "Chief, {}".format(division.div_acronym)
            else:
                section = Section.objects.filter(sec_head_id=recommended_by_name.id).first()
                if section:
                    recommended_by_position = "Head, {}".format(section.sec_acronym)
                else:
                    recommended_by_position = recommended_by_name.position.name

        first_level = recommended_by_name.pi.user.get_fullname.upper()
        first_level_pos = recommended_by_position
    else:
        first_level = None
        first_level_pos = None

    if request.POST.get('approved_by'):
        approved_by_position_wacronym = ''
        approved_by = re.split('\[|\]', request.POST.get('approved_by'))
        approved_by_name = Empprofile.objects.filter(id_number=approved_by[1]).first()
        check_approved_by_position = Designation.objects.filter(emp_id=approved_by_name.id).first()
        if check_approved_by_position:
            approved_by_position = check_approved_by_position.name
            approved_by_position_wacronym = ''
        else:
            division = Division.objects.filter(div_chief_id=approved_by_name.id).first()
            if division:
                approved_by_position = "Chief, {}".format(division.div_acronym)
                approved_by_position_wacronym = "Chief, {}".format(division.div_name)
            else:
                section = Section.objects.filter(sec_head_id=approved_by_name.id).first()
                if section:
                    approved_by_position = "Head, {}".format(section.sec_acronym)
                    approved_by_position_wacronym = "Head, {}".format(section.sec_name)
                else:
                    approved_by_position = approved_by_name.position.name

        second_level = approved_by_name.pi.user.get_fullname.upper()
        second_level_w_pos = "{}, {}".format(approved_by_name.pi.user.get_fullname.upper(), approved_by_name.position.acronym)
        second_level_pos_not_acronym = approved_by_position_wacronym
        second_level_pos = approved_by_position
    else:
        second_level = None
        second_level_pos = None
        second_level_w_pos = None
        second_level_pos_not_acronym = None
    return JsonResponse({'first_level': first_level, 'first_level_pos': first_level_pos,
                         'second_level': second_level, 'second_level_pos': second_level_pos,
                         'second_level_w_pos': second_level_w_pos, 'second_level_pos_not_acronym': second_level_pos_not_acronym})


@login_required
@csrf_exempt
def leave_after_print(request):
    if request.method == "POST":
        LeavePrintLogs.objects.create(
            leaveapp_id=request.POST.get('pk')
        )

        return JsonResponse({'data': 'success' })


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
def ctdo_requests(request):
    if request.method == "POST":
        with transaction.atomic():
            lasttrack = CTDORequests.objects.order_by('-id').first()
            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'CTDO')

            random_dates = request.POST.getlist('dates[]')
            type = request.POST.getlist('type[]')

            utilization = CTDOUtilization.objects.filter(emp_id=request.session['emp_id'], status=0)

            if utilization:
                ctdo = CTDORequests(
                    tracking_no=track_num,
                    start_date=request.POST.get('start_date') if request.POST.get('start_date') else None,
                    end_date=request.POST.get('end_date') if request.POST.get('end_date') else None,
                    date_filed=datetime.now(),
                    emp_id=request.session['emp_id'],
                    status=0,
                    remarks=request.POST.get('remarks')
                )

                # Save points for requesting a CTDO
                gamify(12, request.session['emp_id'])

                ctdo.save()

                total = convert_to_standard(int(request.POST.get('total_days')),
                                            int(request.POST.get('total_hours')),
                                            int(request.POST.get('total_minutes')))
                total_u = convert_to_standard(int(request.POST.get('total_u_days')),
                                              int(request.POST.get('total_u_hours')),
                                            int(request.POST.get('total_u_minutes')))

                CTDOHistoryBalance.objects.create(
                    total_days=total[0],
                    total_hours=total[1],
                    total_minutes=total[2],
                    total_u_days=total_u[0],
                    total_u_hours=total_u[1],
                    total_u_minutes=total_u[2],
                    ctdoreq_id=ctdo.id
                )

                utilization.update(
                    ctdoreq_id=ctdo.id,
                    status=1
                )

                CTDOCoc.objects.filter(emp_id=request.session['emp_id'], ctdoreq_id=None).update(
                    ctdoreq_id=ctdo.id
                )

                data = [{'dates': dates, 'type': type}
                        for dates, type in
                        zip(random_dates, type)]

                for row in data:
                    CTDORandomDates.objects.create(
                        ctdo_id=ctdo.id,
                        date=row['dates'],
                        type=row['type']
                    )

                return JsonResponse({'data': 'success', 'msg': 'This will serve as your tracking no. {}. Please wait for the reviewal of your ctdo request. Thank you.'.format(track_num)})
            else:
                return JsonResponse({'error': True, 'msg': 'The filing process for your CTDO cannot proceed without selecting your earned CoC. Please ensure to choose your earned CoC.'})
        return JsonResponse({'error': True, 'msg': 'System encountered an error. Please try again.'})

    coc = CTDOActualBalance.objects.filter(cocbal__emp_id=request.session['emp_id'], cocbal__status=1)

    list_days = []
    list_hours = []
    list_minutes = []
    for row in coc:
        if int(row.days) == 0 and int(row.hours) == 0 and int(row.minutes) == 0:
            CTDOBalance.objects.filter(id=row.cocbal_id).update(
                status=0
            )

        list_days.append(int(row.days))
        list_hours.append(int(row.hours))
        list_minutes.append(int(row.minutes))

    minutes = sum(list_minutes) // 60
    total_minutes = sum(list_minutes) - minutes * 60
    hours = sum(list_hours) // 8
    total_hours = (sum(list_hours) - hours * 8) + minutes
    total_days = sum(list_days) + hours
    standard = convert_to_standard(total_days, total_hours, total_minutes)

    context = {
        'date': datetime.now(),
        'tab_title': 'CTDO Requests (COS / JO)',
        'title': 'personnel_transactions',
        'sub_title': 'ctdo_request',
        'total_days': standard[0]
    }
    return render(request, 'frontend/leave/ctdo_requests.html', context)


@login_required
def coc_earned_content(request):
    CTDOBalance.objects.filter(date_expiry__lt=date.today()).update(
        status=2
    )

    coc = CTDOActualBalance.objects.filter(cocbal__emp_id=request.session['emp_id'], cocbal__status=1)

    list_days = []
    list_hours = []
    list_minutes = []
    for row in coc:
        if int(row.days) == 0 and int(row.hours) == 0 and int(row.minutes) == 0:
            CTDOBalance.objects.filter(id=row.cocbal_id).update(
                status=0
            )

        list_days.append(int(row.days))
        list_hours.append(int(row.hours))
        list_minutes.append(int(row.minutes))

    minutes = sum(list_minutes) // 60
    total_minutes = sum(list_minutes) - minutes * 60
    hours = sum(list_hours) // 8
    total_hours = (sum(list_hours) - hours * 8) + minutes
    total_days = sum(list_days) + hours

    utilization = CTDOUtilization.objects.filter(emp_id=request.session['emp_id'], status=0)

    list_u_days = []
    list_u_hours = []
    list_u_minutes = []
    for row in utilization:
        list_u_days.append(int(row.days))
        list_u_hours.append(int(row.hours))
        list_u_minutes.append(int(row.minutes))

    u_minutes = sum(list_u_minutes) // 60
    total_u_minutes = sum(list_u_minutes) - u_minutes * 60
    u_hours = sum(list_u_hours) // 8
    total_u_hours = (sum(list_u_hours) - u_hours * 8) + u_minutes
    total_u_days = sum(list_u_days) + u_hours

    standard_u = convert_to_standard(total_u_days, total_u_hours, total_u_minutes)
    now = timezone.now()
    total_utilization = CTDORandomDates.objects.filter(ctdo__date_filed__year=now.year,
                                                       ctdo__date_filed__month=now.month,
                                                       ctdo__emp_id=request.session['emp_id'],
                                                       ctdo__status__in=[0, 1])

    for row in coc:
        check = CTDOCoc.objects.filter(emp_id=request.session['emp_id'], ctdoreq_id=None, month_earned=row.cocbal.month_earned)
        if not check:
            CTDOCoc.objects.create(
                month_earned=row.cocbal.month_earned,
                days=row.days,
                hours=row.hours,
                minutes=row.minutes,
                expiry_date=row.cocbal.date_expiry,
                emp_id=request.session['emp_id']
            )

    context = {
        'coc': CTDOActualBalance.objects.filter(cocbal__emp_id=request.session['emp_id'], cocbal__status=1),
        'total_days': total_days,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'utilization': utilization,
        'total_u_days': standard_u[0],
        'total_u_hours': standard_u[1],
        'total_u_minutes': standard_u[2],
        'total_utilization': total_utilization.count()
    }
    return render(request, 'frontend/leave/coc_earned_content.html', context)


@login_required
@csrf_exempt
def delete_coc_utilization(request):
    if request.POST.get('ctdoreq_id'):
        utilization = CTDOUtilization.objects.filter(ctdoreq_id=request.POST.get('ctdoreq_id'), emp_id=request.POST.get('token'))
    else:
        utilization = CTDOUtilization.objects.filter(ctdoreq_id=None, emp_id=request.POST.get('token'))

    coc_actual_balance = CTDOActualBalance.objects.filter(id=utilization.first().cocactualbal_id)
    CTDOBalance.objects.filter(id=coc_actual_balance.first().cocbal_id).update(
        status=1
    )

    coc_actual_balance.update(
        days=F('days') + int(utilization.first().days),
        hours=F('hours') + int(utilization.first().hours),
        minutes=F('minutes') + int(utilization.first().minutes),
    )

    standard_format = convert_to_standard(int(coc_actual_balance.first().days),
                        int(coc_actual_balance.first().hours),
                        int(coc_actual_balance.first().minutes))

    coc_actual_balance.update(
        days=standard_format[0],
        hours=standard_format[1],
        minutes=standard_format[2],
    )

    utilization.delete()
    return JsonResponse({'data': 'success', 'msg': 'Your earned CoC for utilization has been removed successfully.'})


class Balance:
    def __init__(self, id, days, hours, minutes):
        self.id = id
        self.days = days
        self.hours = hours
        self.minutes = minutes

    def to_minutes(self):
        return self.days * 8 * 60 + self.hours * 60 + self.minutes

    def subtract(self, other):
        new_minutes = max(self.to_minutes() - other.to_minutes(), 0)
        days, hours, minutes = convert_to_standard(0, 0, new_minutes)
        return Balance(self.id, days, hours, minutes)


def get_first_date(obj):
    dates = obj.cocbal.month_earned.split(',')
    first_date_str = f'{dates[0].strip()}, {dates[-1].strip()}'
    return parse(first_date_str)


@login_required
@csrf_exempt
def auto_utilize_coc_earned(request):
    if request.method == "POST":
        days = int(request.POST.get('days'))
        hours = int(request.POST.get('hours'))
        if days != 0 or hours !=0:
            actual_balance = (CTDOActualBalance.objects
                              .filter(cocbal__emp_id=request.session['emp_id'], cocbal__status=1)
                              .annotate(total_time=F('days') * 8 * 60 + F('hours') * 60 + F('minutes')))

            actual_balance = list(actual_balance)
            actual_balance.sort(key=get_first_date)

            utilized = []
            remaining = []

            input_days_hours = Balance(None, days, hours, 0)

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
                    cocactualbal_id=balance.id,
                    days=balance.days,
                    hours=balance.hours,
                    minutes=balance.minutes,
                    emp_id=request.session['emp_id'],
                    status=0
                )

            return JsonResponse({'data': 'success', 'msg': 'Auto utilization completed. You can now select a dates for your ctdo application.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Processing is not possible due to insufficient balance for utilization.'})


@login_required
@csrf_exempt
def request_for_ctdo_cancellation(request):
    if request.method == "POST":
        CTDORequests.objects.filter(id=request.POST.get('id')).update(
            status=3
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully request for cancellation on your CTDO Application.'})


@login_required
def utilize_coc_earned(request, pk):
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
                days=request.POST.get('days'),
                hours=request.POST.get('hours'),
                minutes=request.POST.get('minutes'),
                cocactualbal_id=coc.id,
                emp_id=coc.cocbal.emp_id,
                status=0
            )

            return JsonResponse({'data': 'success', 'msg': 'Successfully added! Your earned CoC is now available for your utilization.'})
        else:
            return JsonResponse({'error': True, 'msg': 'Insufficient balance. Please refer to personnel administration section to file your coc earned.'})

    context = {
        'coc': coc,
        'pk': pk
    }
    return render(request, 'frontend/leave/utilize_coc.html', context)


def convert_to_minutes(days, hours, minutes):
    return days*8*60 + hours*60 + minutes


def convert_to_days_hours_minutes(minutes):
    days = minutes // (8*60)
    minutes %= 8*60
    hours = minutes // 60
    minutes %= 60
    return days, hours, minutes


@login_required
def print_ctdo(request, pk):
    data = CTDORequests.objects.filter(id=pk).first()
    emp = Empprofile.objects.filter(id=data.emp_id).first()

    if emp.section.div.div_name == "Office of the Regional Director":
        first_level = emp.section.sec_head_id
    else:
        first_level = emp.section.div.div_chief_id

    designation = Designation.objects.filter(id=1).first()
    second_level = designation.emp_id
    second_level_pos = designation.name

    history = CTDOHistoryBalance.objects.filter(ctdoreq_id=pk).first()

    available = [history.total_days if history is not None else 0,
                 history.total_hours if history is not None else 0,
                 history.total_minutes if history is not None else 0]
    applied = [history.total_u_days if history is not None else 0,
               history.total_u_hours if history is not None else 0,
               history.total_u_minutes if history is not None else 0]

    available_minutes = convert_to_minutes(*available)
    applied_minutes = convert_to_minutes(*applied)

    balance = [0, 0, 0]

    # Only calculate the remaining balance if the available minutes exceed the applied minutes
    if available_minutes >= applied_minutes:
        balance_minutes = available_minutes - applied_minutes
        balance = list(convert_to_days_hours_minutes(balance_minutes))

        if balance[1] < 0:  # if hours are negative
            balance[0] -= 1
            balance[1] += 8

        if balance[2] < 0:  # if minutes are negative
            balance[1] -= 1
            balance[2] += 60

        if balance[1] < 0:  # if hours are still negative
            balance[0] -= 1
            balance[1] += 8
    if emp.empstatus.id in [1, 2]:
        context = {
            'data': data,
            'history': history,
            'total_b_days': balance[0] if history else None,
            'total_b_hours': balance[1] if history else None,
            'total_b_minutes': balance[2] if history else None,
            'personnel_officer': PortalConfiguration.objects.filter(key_name='Personnel Officer').first(),
            'first_level': first_level,
            'second_level': second_level,
            'second_level_pos': second_level_pos
        }
        return render(request, 'frontend/leave/print_ctdo.html', context)
    else:
        head = Designation.objects.filter(emp_id=emp.id).first()
        div_head = Division.objects.filter(div_chief_id=emp.id).first()
        sec_head = Section.objects.filter(sec_head_id=emp.id).first()

        if div_head:
            if div_head.designation_id == 1 or head:  # PPD
                first_level = ""
                first_level_pos = ""
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            else:
                first_level = div_head.designation.emp_id
                first_level_pos = Designation.objects.filter(emp_id=div_head.designation.emp_id).first()
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            classes = 2
        elif sec_head:
            if sec_head.div.designation_id == 1:  # PPD
                first_level = ""
                first_level_pos = ""
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            else:
                first_level = sec_head.div.designation.emp_id
                first_level_pos = Designation.objects.filter(emp_id=sec_head.div.designation.emp_id).first()
                second_level = Designation.objects.filter(id=1).first()
                second_level_pos = second_level.name
            classes = 2
        else:
            emp = Empprofile.objects.filter(id=emp.id).first()
            first_level = emp.section.div.div_chief_id
            first_level_pos = Division.objects.filter(div_chief_id=emp.section.div.div_chief_id).first()

            if emp.aoa.name != "Field Office Caraga":
                second_level = emp.section.div.designation.emp_id
                second_level_pos = Designation.objects.filter(emp_id=emp.section.div.designation.emp_id).first()
            else:
                fo_staff = PortalConfiguration.objects.filter(key_name='Leave Second Level Signatory').first()
                second_level = fo_staff.key_acronym if fo_staff.key_acronym else None
                check = Designation.objects.filter(emp_id=fo_staff.key_acronym)
                if check:
                    second_level_pos = check
                else:
                    second_level_pos = None
            classes = 1

        context = {
            'data': data,
            'first_level': first_level,
            'first_level_pos': first_level_pos,
            'second_level': second_level,
            'second_level_pos': second_level_pos,
            'classes': classes,
            'leavesubtype': LeaveSubtype.objects.order_by('order'),
            'personnel_officer': PortalConfiguration.objects.filter(key_name='Personnel Officer').first(),
            'history': history,
        }
        return render(request, 'frontend/leave/print_regcon_ctdo.html', context)


@login_required
@csrf_exempt
def ctdo_add_remarks(request):
    if request.method == "POST":
        CTDORequests.objects.filter(id=request.POST.get('pk')).update(
            remarks=request.POST.get('remarks')
        )

        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
def cancel_ctdo(request):
    if request.method == "POST":
        with transaction.atomic():
            ctdo = CTDORequests.objects.filter(id=request.POST.get('id'))
            ctdo.update(
                status=2
            )

            utilization = CTDOUtilization.objects.filter(ctdoreq_id=request.POST.get('id'))
            if utilization:
                for row in utilization:
                    CTDOBalance.objects.filter(id=row.cocactualbal.cocbal_id).update(
                        status=1
                    )

                    CTDOActualBalance.objects.filter(id=row.cocactualbal_id).update(
                        days=F('days') + int(row.days),
                        hours=F('hours') + int(row.hours),
                        minutes=F('minutes') + int(row.minutes),
                    )

            message = "Good day, {}! Your CTDO request with tracking number {} has been cancelled by the administrator. - The My PORTAL Team".format(
                ctdo.first().emp.pi.user.first_name,
                ctdo.first().tracking_no)
            if ctdo.first().emp.pi.mobile_no:
                t = threading.Thread(target=send_notification,
                                     args=(message, ctdo.first().emp.pi.mobile_no, request.session['emp_id'], ctdo.first().emp.id))
                t.start()

            return JsonResponse({'data': 'success', 'msg': "The cancellation of CTDO with the tracking number {} has been successfully processed.".format(ctdo.first().tracking_no)})
        return JsonResponse({'error': True, 'msg': 'System encountered an error. Please try again later.'})


@login_required
@csrf_exempt
def ctdo_after_print(request):
    if request.method == "POST":
        CTDOPrintLogs.objects.create(
            ctdo_id=request.POST.get('pk')
        )

        return JsonResponse({'data': 'success' })