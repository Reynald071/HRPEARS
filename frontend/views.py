import json
import math
import re
import urllib
from datetime import datetime, date, timedelta
from random import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1
from ldap3 import MODIFY_REPLACE

from api.wiserv import send_notification, send_sms_notification
from backend.forms import DownloadableForm, FaqsForm
from backend.iso.models import IsoForms, IsoDownloadhistory
from backend.libraries.leave.models import LeaveApplication, LeaveRandomDates
from backend.models import WfhType, WfhTime, Empprofile, Division, Section, Aoa, ForgotPasswordCode, \
    AuthUser, Patches, DtrPin, PayrollIncharge
from backend.pas.accomplishment.models import DTRAssignee
from backend.pas.payroll.models import PasEmpPayrollIncharge
from frontend.models import Downloadableforms, Feedback, Faqs, PasAccomplishmentOutputs, SocialMediaAccount, \
    IncaseOfEmergency, DownloadableformsClass, Ritopeople, TravelOrder
from frontend.pas.accomplishment.models import Dtr
from frontend.templatetags.tags import getHash, gamify, get_signatory
from portal import settings
from portal.active_directory import searchSamAccountName


@login_required
def developer_update(request):
    context = {
        'version': Patches.objects.order_by('-release_date')
    }
    return render(request, 'developer_update.html', context)


@login_required
def downloadable_forms(request):
    form = DownloadableForm()
    if request.method == "POST":
        form = DownloadableForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request,
                             'The downloadable forms {} was added successfully.'.format(form.cleaned_data['title']))
            form.save()
            return redirect('downloadable-forms')

    search = request.GET.get('search', '')
    forms = Downloadableforms.objects.filter(Q(title__icontains=search), Q(status=True)).order_by('-date', 'title')
    context = {
        'form': form,
        'downloadable': forms,
        'class': DownloadableformsClass.objects.filter(Q(status=True), Q(is_sop=False)),
        'tab_title': 'Downloadable Files',
        'title': 'downloadables',
    }
    return render(request, 'frontend/downloadable_forms.html', context)


@login_required
def iso_forms(request):
    search = request.GET.get('search', '')
    forms = IsoForms.objects.order_by('title').filter(Q(is_deleted=0), Q(title__icontains=search))
    context = {
        'downloadable': forms,
        'title': 'f_documents',
        'sub_title': 'downloadable_forms',
        'sub_sub_title': 'iso',
    }
    return render(request, 'frontend/iso_forms.html', context)


@login_required
def iso_forms_downloaded(request):
    if request.method == "POST":
        IsoDownloadhistory.objects.create(
            form_id=request.POST.get('id'),
            emp_id=request.session['emp_id']
        )
        return JsonResponse({'data': 'success'})
    else:
        return JsonResponse(
            {'error': 'You are not authorized to access this content. Please contact your administrator.'})


def submit_feedback(request):
    if request.method == "POST":
        Feedback.objects.create(
            rate=request.POST.get('rate'),
            comment=request.POST.get('comment'),
            emp_id=request.session['emp_id'] if request.session.keys() else None,
            date=datetime.now()
        )

        # Save points for RITO
        if request.session.keys():
            gamify(16, request.session['emp_id'])

            employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
            send_notification("Thanks for taking the time to give us feedback. We do use feedback like yours to improve "
                              "the Caraga PORTAL experience for everyone. - The My PORTAL Team",
                              employee.pi.mobile_no, request.session['emp_id'])
        return JsonResponse({'data': 'success'})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Work from Home Attendance
@login_required
def wfh_attendance(request):
    if request.method == "POST":
        today = date.today()
        check = WfhTime.objects.filter(emp_id=request.session['emp_id'], type_id=request.POST.get('type'),
                                       datetime__gt=today)
        wfh_type = WfhType.objects.filter(id=request.POST.get('type')).first()

        if check:
            messages.error(request, "You have already {}!".format(wfh_type.type_desc))
            return JsonResponse({'data': 'success'})
        else:
            WfhTime.objects.create(
                datetime=datetime.now(),
                type_id=request.POST.get('type'),
                emp_id=request.session['emp_id'],
                ip_address=get_client_ip(request)
            )

            # Save points for use of wfh time in/out
            gamify(15, request.session['emp_id'])

            return JsonResponse({'data': 'success'})

    today = date.today()
    check = WfhTime.objects.filter(emp_id=request.session['emp_id'], datetime__gt=today).first()

    has_attendance = 0
    if check:
        has_attendance = 1

    context = {
        'has_attendance': has_attendance,
        'date': datetime.now(),
        'type': WfhType.objects.all(),
        'accomplishment': PasAccomplishmentOutputs.objects.filter(emp_id=request.session['emp_id'],
                                                                  date_period=today).first(),
        'tab_title': 'Work from Home Attendance',
        'emp_id': request.session['emp_id']
    }
    return render(request, 'dtr/wfh_attendance.html', context)


@login_required
def get_attendance_status_for_today(request):
    if request.method == "GET":
        today = date.today()
        check = WfhTime.objects.annotate(hash=SHA1('emp_id')).filter(hash=request.GET.get('employee_id'),
                                                                     datetime__gt=today)
        data = [dict(type_id=row.type_id) for row in check]
        return JsonResponse({'data': data})


@login_required
def wfh_accomplishment(request):
    if request.method == "POST":
        check = PasAccomplishmentOutputs.objects.filter(emp_id=request.session['emp_id'], date_period=date.today())
        if check:
            PasAccomplishmentOutputs.objects.filter(emp_id=request.session['emp_id'], date_period=date.today()).update(
                date_period=date.today(),
                place_visited="Office Works" if request.POST.get('type') == "0" else "Work from Home",
                output=request.POST.get('output'),
            )
        else:
            PasAccomplishmentOutputs.objects.create(
                emp_id=request.session['emp_id'],
                date_period=date.today(),
                place_visited="Office Works" if request.POST.get('type') == "0" else "Work from Home",
                output=request.POST.get('output'),
                remarks=''
            )
        messages.success(request, "You have successfully updated your accomplishment report for today!")
        return redirect('wfh_attendance')


@login_required
@permission_required('auth.monitoring')
def wfh_dtr(request):
    if request.method == "POST":
        to_include = request.POST.getlist('to_include[]')

        employees = Empprofile.objects.filter(id__in=to_include).order_by('pi__user__last_name')
        start_date = datetime.strptime(request.POST.get('start_date_hidden'), "%Y-%m-%d")
        end_date = datetime.strptime(request.POST.get('end_date_hidden'), "%Y-%m-%d")
        delta = end_date - start_date
        alldays = list()
        for i in range(delta.days + 1):
            alldays.append(start_date + timedelta(days=i))

        context = {
            'employees': employees,
            'ifcheck': request.POST.get('ifcheck'),
            'start_date': start_date,
            'end_date': end_date,
            'all_days': alldays,
        }
        return render(request, 'dtr/print_dtr_batch.html', context)

    section = Section.objects.all()
    division = Division.objects.all()
    payroll_incharge = PayrollIncharge.objects.filter(~Q(emp_id=None))

    context = {
        'aoa': Aoa.objects.all().order_by('name'),
        'division': division,
        'section': section,
        'payroll_incharge': payroll_incharge,
        'tab_title': 'Daily Time Records',
        'title': 'employee',
        'sub_title': 'monitoring',
        'sub_sub_title': 'dtr'
    }
    return render(request, 'dtr/wfh_dtr.html', context)


@login_required
@permission_required('auth.monitoring')
def load_employee_by_payroll_incharge(request, pk, start_date, end_date):
    print("DATES: ", start_date, end_date)
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'employee': PasEmpPayrollIncharge.objects.filter(payroll_incharge_id=pk).order_by('emp__pi__user__last_name')
    }
    return render(request, 'dtr/load_employee_by_pr.html', context)


@login_required
@permission_required('auth.monitoring')
def load_employee_by_section(request, section_id, aoa_id, start_date, end_date):
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'data': Empprofile.objects.filter(Q(pi__user__is_active=1) & Q(section_id=section_id) & Q(aoa_id=aoa_id) & ~Q(position__name__icontains='OJT')).order_by('pi__user__last_name')
    }
    return render(request, 'dtr/load_employee_by_section.html', context)


@login_required
@permission_required('auth.monitoring')
def load_employee_dtr(request, employee_name, start_date, end_date):
    id_number = re.split('\[|\]', employee_name)
    employee = Empprofile.objects.filter(id_number=id_number[1]).first()

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end_date - start_date
    alldays = list()
    for i in range(delta.days + 1):
        alldays.append(start_date + timedelta(days=i))

    context = {
        'employee': employee,
        'total_length': len(alldays),
        'ifcheck': request.POST.get('ifcheck'),
        'start_date': start_date,
        'end_date': end_date,
        'all_days': alldays,
    }
    return render(request, 'dtr/load_employee_dtr.html', context)


@login_required
@csrf_exempt
def get_employee_time_async(request):
    emp_id = request.POST.get('emp_id')
    date = request.POST.get('date')
    dtr_time = {'check_in': '', 'break_out': '', 'break_in': '', 'check_out': ''}

    if not date:
        return JsonResponse({'data': dtr_time})

    weekday = datetime.strptime(date, '%Y-%m-%d').weekday()

    travel = Ritopeople.objects.values_list('detail__rito_id', flat=True). \
        filter(name_id=emp_id,
               detail__inclusive_to__gte=datetime.strptime(date, '%Y-%m-%d').date(),
               detail__inclusive_from__lte=datetime.strptime(date, '%Y-%m-%d').date(),
               detail__rito__status=3
               ).first()

    leave = LeaveApplication.objects.values_list('tracking_no', flat=True).filter(
                emp_id=emp_id,
                end_date__gte=datetime.strptime(date, '%Y-%m-%d').date(),
                start_date__lte=datetime.strptime(date, '%Y-%m-%d').date(),
                status__in=[0, 1]
            ).first()

    if not leave:
        leave = LeaveRandomDates.objects.values_list('leaveapp__tracking_no', flat=True).filter(
            leaveapp__emp_id=emp_id,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            leaveapp__status__in=[0, 1]
        ).first()

    to = TravelOrder.objects.values_list('rito__tracking_no', flat=True).filter(rito_id=travel, status=2).first()
    dtr = DtrPin.objects.filter(emp_id=emp_id).first()

    wfh_query = WfhTime.objects.filter(Q(emp_id=emp_id), Q(datetime__date=date))

    if dtr is not None:
        data_query = Dtr.objects.using('amscoa').filter(Q(employeeid=dtr.pin_id),
                                                    Q(date=datetime.strptime(date, '%Y-%m-%d').date())).order_by('time')
    else:
        data_query = Dtr.objects.none()

    dtr_time = process_data_query(data_query, dtr_time)

    if weekday in [5, 6] or to or leave or not dtr:
        # wfh_query_non_ojt = wfh_query
        wfh_query_ojt = wfh_query.filter(emp__position__name='OJT')

        # dtr_time = process_wfh_query(wfh_query_non_ojt, dtr_time, wfh_label=True)
        dtr_time = process_wfh_query(wfh_query_ojt, dtr_time, wfh_label=False)

        if weekday == 5:
            if dtr_time['break_out'] != '' or dtr_time['break_in'] != '' or dtr_time['check_out'] != '':
                dtr_time['check_in'] = dtr_time['check_in']
            else:
                dtr_time['check_in'] = dtr_time['check_in'] or 'Saturday'
        elif weekday == 6:
            if dtr_time['break_out'] != '' or dtr_time['break_in'] != '' or dtr_time['check_out'] != '':
                dtr_time['check_in'] = dtr_time['check_in']
            else:
                dtr_time['check_in'] = dtr_time['check_in'] or 'Sunday'
        elif to:
            dtr_time['check_in'] = dtr_time['check_in'] or f'OB: {to}'
        elif leave:
            dtr_time['check_in'] = dtr_time['check_in'] or f'L: {leave}'
    else:
        dtr_time = process_data_query(data_query, dtr_time)

    # PROCESS IF IT'S EMPLOYEE
    dtr_time = process_wfh_query(wfh_query, dtr_time, wfh_label=True)

    return JsonResponse({'data': dtr_time})


def process_wfh_query(wfh_query, dtr_time, wfh_label=True):
    for w in wfh_query:
        if w.type_id == 1:
            dtr_time['check_in'] = w.datetime.strftime('%H:%M %p') + (' WFH' if wfh_label else '')
        elif w.type_id == 2:
            dtr_time['break_out'] = w.datetime.strftime('%H:%M %p') + (' WFH' if wfh_label else '')
        elif w.type_id == 3:
            dtr_time['break_in'] = w.datetime.strftime('%H:%M %p') + (' WFH' if wfh_label else '')
        elif w.type_id == 4:
            dtr_time['check_out'] = w.datetime.strftime('%H:%M %p') + (' WFH' if wfh_label else '')

    return dtr_time


def process_data_query(data_query, dtr_time):
    for row in data_query:
        if row.status == 0:
            dtr_time['check_in'] = row.time.strftime('%I:%M %p')
        elif row.status == 2:
            dtr_time['break_out'] = row.time.strftime('%I:%M %p')
        elif row.status == 3:
            dtr_time['break_in'] = row.time.strftime('%I:%M %p')
        elif row.status == 1:
            dtr_time['check_out'] = row.time.strftime('%I:%M %p')

    return dtr_time


@login_required
@permission_required('auth.monitoring')
def manage_dtr(request):
    if request.method == "POST":
        employee_id_number = re.split('\[|\]', request.POST.get('employee_name'))
        employee = Empprofile.objects.values('id').filter(id_number=employee_id_number[1]).first()

        assigned_id_number = re.split('\[|\]', request.POST.get('assigned_to'))
        assigned = Empprofile.objects.values('id').filter(id_number=assigned_id_number[1]).first()

        DTRAssignee.objects.create(
            emp_id=employee['id'],
            assigned_id=assigned['id'],
            date_assigned=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully added the employee.'})

    return render(request, 'dtr/dtr_manage.html')


@login_required
@csrf_exempt
@permission_required('auth.monitoring')
def delete_dtr_assignee(request):
    DTRAssignee.objects.filter(emp_id=request.POST.get('pk')).delete()
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.monitoring')
def manage_dtr_layout(request):
    context = {
        'data': DTRAssignee.objects.values('assigned_id').distinct()
    }
    return render(request, 'dtr/dtr_manage_template.html', context)


@login_required
@permission_required('auth.monitoring')
def print_employee_dtr(request, pk, start_date, end_date):
    sdd = datetime.strptime(start_date, '%Y-%m-%d')
    edd = datetime.strptime(end_date, '%Y-%m-%d')

    emp = Empprofile.objects.annotate(hash_pk=SHA1('id')).filter(hash_pk=pk).first()
    delta = edd - sdd

    alldays = list()
    for i in range(delta.days + 1):
        alldays.append(sdd + timedelta(days=i))

    context = {
        'employee': emp,
        'signatory': get_signatory(emp.id)['signatory'],
        'signatory_pos': get_signatory(emp.id)['signatory_pos'],
        'start_date': sdd,
        'end_date': edd,
        'all_days': alldays,
    }
    return render(request, 'frontend/pas/accomplishment/print_dtr.html', context)


@login_required
def print_timerecordprinter(request):
    employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
    employees = DTRAssignee.objects.filter(assigned_id=employee.id)

    page = request.GET.get('page', 1)

    # Check if we're on the first page or if the session keys don't exist
    if page == "1" or 'dtr_start_date' not in request.session or 'dtr_end_date' not in request.session:
        start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
        end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")

        request.session['dtr_start_date'] = start_date.strftime("%Y-%m-%d")
        request.session['dtr_end_date'] = end_date.strftime("%Y-%m-%d")

        start_date = datetime.strptime(request.session['dtr_start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.session['dtr_end_date'], "%Y-%m-%d")
    else:
        start_date = datetime.strptime(request.session['dtr_start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.session['dtr_end_date'], "%Y-%m-%d")

    delta = end_date - start_date
    alldays = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    context = {
        'employees': Paginator(employees, 40).page(page),
        'ifcheck': request.POST.get('ifcheck'),
        'all_days': alldays,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'dtr/print_dtr_authorized.html', context)


@login_required
@csrf_exempt
@permission_required('auth.administrator')
def load_employees(request):
    if request.method == 'POST':
        employees = list(
            Empprofile.objects.filter(section=request.POST.get('section'), aoa=request.POST.get('aoa')).values_list(
                'id', flat=True))
        return JsonResponse({'data': employees})


@login_required
@permission_required('auth.administrator')
def getemployeebyempid(request, empid):
    empname = Empprofile.objects.get(id=empid)
    if empname:
        return JsonResponse({'data': {'empid': empname.id,
                                      'fullname': empname.pi.user.last_name + ', ' +
                                                  empname.pi.user.first_name + ' ' +
                                                  empname.pi.user.middle_name[0:1] + '.'
                                      if empname.pi.user.middle_name is not None or empname.pi.user.middle_name != ''
                                      else '',
                                      'divsec': empname.section.div.div_acronym + ' / ' + empname.section.sec_name,
                                      'empstatus': empname.empstatus.acronym, 'position': empname.position.acronym}})
    return JsonResponse({'data': ''})


@login_required
def faqs(request):
    form = FaqsForm()
    if request.method == "POST":
        form = FaqsForm(request.POST)
        if form.is_valid():
            if request.POST.get('id') == '':
                messages.success(request,
                                 'The frequently asked question, with title {} was added successfully.'.format(
                                     form.cleaned_data['title']))
                Faqs.objects.create(
                    title=form.cleaned_data['title'],
                    question=form.cleaned_data['question'],
                    answer=form.cleaned_data['answer'],
                    link=form.cleaned_data['link'],
                    isactive=form.cleaned_data['isactive'],
                    created_by=request.session['emp_id']
                )
            else:
                messages.success(request,
                                 'The frequently asked question, with title {} was updated.'.format(
                                     form.cleaned_data['title']))
                faq = Faqs.objects.get(id=request.POST.get('id'))
                faq.title = form.cleaned_data['title']
                faq.question = form.cleaned_data['question']
                faq.answer = form.cleaned_data['answer']
                faq.link = form.cleaned_data['link']
                faq.isactive = form.cleaned_data['isactive']
                faq.save()
            return redirect('faqs')

    context = {
        'form': form,
        'title': 'faqs',
        'activefaqs': Faqs.objects.filter(isactive=1),
    }
    return render(request, 'frontend/faqs.html', context)


def profiles(request, id_number):
    employee = Empprofile.objects.filter(id_number=id_number).first()
    context = {
        'incase_of_emergency': IncaseOfEmergency.objects.filter(pi_id=employee.pi_id).first(),
        'sm': SocialMediaAccount.objects.filter(emp__id_number=id_number).first(),
        'data': employee
    }
    return render(request, 'profiles.html', context)


def forgot_password(request):
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result['success']:
            id_number = Empprofile.objects.filter(id_number=request.POST.get('id_number')).first()
            if id_number:
                if id_number.pi.mobile_no:
                    digits = [i for i in range(0, 10)]
                    code = ""
                    for i in range(6):
                        index = math.floor(random() * 10)
                        code += str(digits[index])

                    check = ForgotPasswordCode.objects.filter(emp_id=id_number.id)

                    if check:
                        check.update(
                            code=code.strip(),
                            is_active=1
                        )
                    else:
                        f_code = ForgotPasswordCode(
                            code=code.strip(),
                            emp_id=id_number.id,
                            is_active=1
                        )
                        f_code.save()

                    print(code.strip())

                    message = "Good day, {}! Please use the code {} to reset your password. If you did not request your " \
                              "password to be reset, ignore this message. - The My PORTAL Team" \
                        .format(id_number.pi.user.first_name, code.strip())

                    send_sms_notification(message, id_number.pi.mobile_no, id_number.id, id_number.id)

                    return JsonResponse({'data': 'success', 'token': '{}'.format(getHash(id_number.id))})
                else:
                    return JsonResponse(
                        {'error': 'True', 'msg': 'Empty Phone Number. Please email us at ictsupport.focrg@dswd.gov.ph'})
            else:
                return JsonResponse({'error': 'True', 'msg': 'Please identify your account using the correct id number.'})
        else:
           return JsonResponse({'msg': 'Invalid reCAPTCHA. Please try again..'})
    return render(request, 'password_reset/forgot_pass_new.html')


@csrf_exempt
def resend_code(request, token):
    if request.method == "POST":
        digits = [i for i in range(0, 10)]
        code = ""
        for i in range(6):
            index = math.floor(random() * 10)
            code += str(digits[index])

        check = ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token)
        check.update(code=code.strip(), is_active=1)
        message = "Good day, {}! Please use the code {} to reset your password. If you did not request your password " \
                  "to be reset, ignore this message. - The My PORTAL Team" \
            .format(check.first().emp.pi.user.first_name, code.strip())

        send_notification(message, check.first().emp.pi.mobile_no, check.first().emp.id, check.first().emp.id)
        return JsonResponse({'data': 'success'})


def forgot_password_code(request, token):
    if request.method == "POST":
        check = ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token,
                                                                                code=request.POST.get('code'),
                                                                                is_active=1)
        if check:
            return JsonResponse({'data': 'success', 'token': token})
        else:
            return JsonResponse({'error': 'True', 'msg': 'You have entered a wrong code. Please try again.'})
    check = ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token, is_active=1)
    if check:
        context = {
            'phone_number': check.first().emp.pi.mobile_no[-4:],
            'token': token
        }
        return render(request, 'password_reset/six_digit_code_new.html', context)
    else:
        return render(request, "404.html")


@csrf_exempt
def forgot_password_expire_code(request, token):
    if request.method == "POST":
        ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token).filter(is_active=0)
        return JsonResponse({'data': 'success'})


def set_new_password(request, token):
    if request.method == "POST":
        employee = Empprofile.objects.annotate(hash=SHA1('id')).filter(hash=token).first()

        # user = searchSamAccountName(employee.pi.user.username)
        #
        # if user["status"]:
        #     enc_pwd = '"{}"'.format(str(request.POST.get('password'))).encode('utf-16-le')
        #     user["connection"].modify(user["userDN"], {'unicodePwd': [(MODIFY_REPLACE, [enc_pwd])]})
        #
        #     ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token).update(is_active=0)
        #     AuthUser.objects.filter(id=employee.pi.user_id).update(
        #         password=make_password(request.POST.get('password'))
        #     )
        #     return JsonResponse({'data': 'success',
        #                          'msg': 'Please note that your password has been successfully reset.'})
        # else:
        #     return JsonResponse({'error': 'True', 'msg': 'Active Directory not created. Please email us at '
        #                                                  'ictsupport.focrg@dswd.gov.ph'})

        ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token).update(is_active=0)
        AuthUser.objects.filter(id=employee.pi.user_id).update(
            password=make_password(request.POST.get('password'))
        )
        return JsonResponse({'data': 'success',
                             'msg': 'Please note that your password has been successfully reset.'})
    check = ForgotPasswordCode.objects.annotate(hash=SHA1('emp_id')).filter(hash=token, is_active=1)
    if check:
        context = {
            'token': token
        }
        return render(request, 'password_reset/set_new_pass_new.html', context)
    else:
        return render(request, "404.html")
