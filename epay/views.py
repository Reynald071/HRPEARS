import csv
import re
import threading
from datetime import datetime
from io import StringIO

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_sms_notification
from backend.infimos.models import Transactions
from backend.libraries.leave.models import CTDORequests, LeaveApplication
from backend.models import PayrollIncharge, Empprofile, InfimosPurpose
from backend.pas.payroll.models import PasEmpPayrollIncharge, PayrollTimelineWorkFlow, PayrollTimelineWorkflowComments
from backend.templatetags.tags import getemployee, force_token_decryption
from epay.models import PasEmpPayrollNotification
from frontend.models import Ritopeople, PortalConfiguration


@login_required
@permission_required("auth.payroll_incharge")
def epay_home(request):
    return render(request, 'epay/home.html')


@login_required
@permission_required("auth.payroll_incharge")
def manage_payroll_employee(request):
    check = PayrollIncharge.objects.filter(emp_id=request.session['emp_id'])
    if request.method == "POST":
        if check:
            id_number = re.split('\[|\]', request.POST.get('employee_name'))
            employee = getemployee(id_number[1])

            check_if_exists = PasEmpPayrollIncharge.objects.filter(emp_id=employee.id)
            if not check_if_exists:
                PasEmpPayrollIncharge.objects.create(
                    payroll_incharge_id=check.first().id,
                    emp_id=employee.id
                )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully added an employee to your payroll list.'})
            else:
                return JsonResponse({'error': True, 'msg': 'Employee already added by another payroll incharge.'})

    context = {
        'employee': PasEmpPayrollIncharge.objects.filter(payroll_incharge_id=check.first().id).order_by('emp__pi__user__last_name')
    }
    return render(request, 'epay/manage_employee.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_employee_payroll_details(request, pk):
    employee = PasEmpPayrollIncharge.objects.filter(id=pk).first()
    context = {
        'employee': employee,
        'ctdo_requests': CTDORequests.objects.filter(emp_id=employee.emp_id).order_by('-date_filed')[:5],
        'leave_application': LeaveApplication.objects.filter(emp_id=employee.emp_id).order_by('-date_of_filing')[:5],
        'travel_history': Ritopeople.objects.filter(name_id=employee.emp_id).order_by('-detail__rito__date')[:5]
    }
    return render(request, 'epay/view_employee.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_employee_ctdo_requests(request, pk):
    id = force_token_decryption(pk)
    context = {
        'employee': Empprofile.objects.filter(id=id).first(),
    }
    return render(request, 'epay/ctdo_requests.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_employee_leave_application(request, pk):
    id = force_token_decryption(pk)
    context = {
        'employee': Empprofile.objects.filter(id=id).first(),
    }
    return render(request, 'epay/leave_application.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_employee_travel_history(request, pk):
    id = force_token_decryption(pk)
    context = {
        'employee': Empprofile.objects.filter(id=id).first(),
    }
    return render(request, 'epay/travel_history.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll_incharge")
def remove_payroll_employee(request):
    PasEmpPayrollIncharge.objects.filter(id=request.POST.get('pk')).delete()

    return JsonResponse({'data': 'success', 'msg': 'You have successfully deleted an employee to your payroll list.'})


@login_required
@permission_required("auth.payroll_incharge")
def payroll_sent_notification(request):
    check = PayrollIncharge.objects.filter(emp_id=request.session['emp_id'])
    if request.method == "POST":
        employee = request.POST.getlist('employee_name[]')

        for row in employee:
            emp = Empprofile.objects.filter(id=row).first()

            if emp.pi.mobile_no:
                purpose = request.POST.get('purpose')
                start_date_str = request.POST.get('start_date')
                end_date_str = request.POST.get('end_date')
                date_processed_str = request.POST.get('date_processed')
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                date_processed = datetime.strptime(date_processed_str, "%Y-%m-%d")

                formatted_start_date = start_date.strftime("%B %d")
                formatted_end_date = end_date.strftime("%d, %Y")
                formatted_date_processed = date_processed.strftime("%B %d, %Y")

                period_date = "{}-{}".format(formatted_start_date, formatted_end_date)

                check_purpose = InfimosPurpose.objects.filter(name=purpose)

                if check_purpose.first().category_id == 5:
                    year_str = str(start_date.year)
                    message = """
                        Dear {}, please be informed that your {} for the period of {}, 
                        has already been processed by PAS under the disbursement voucher {} (Date Processed: {}).
                        HRMDD administrative staff has also transmitted the said DV to FMD for further processing.
                        Should you have any queries, feel free to contact us. Thank you for your service and dedication.
                    """.format(emp.pi.user.first_name.title(), purpose, year_str,
                               request.POST.get('dv_no'), formatted_date_processed)
                else:
                    message = """
                        Dear {}, please be informed that your {} for the period {}, 
                        has already been processed by PAS under the disbursement voucher {} (Date Processed: {}).
                        HRMDD administrative staff has also transmitted the said DV to FMD for further processing.
                        Should you have any queries, feel free to contact us. Thank you for your service and dedication.
                    """.format(emp.pi.user.first_name.title(), purpose.lower(), period_date, request.POST.get('dv_no'), formatted_date_processed)

                PasEmpPayrollNotification.objects.create(
                    emp_id=row,
                    dv_no=request.POST.get('dv_no'),
                    date_sent=datetime.now(),
                    period_date=period_date,
                    sentby_id=request.session['emp_id'],
                    purpose=purpose
                )

                t = threading.Thread(target=send_sms_notification,
                                     args=(message, emp.pi.mobile_no, request.session['emp_id'], emp.id))
                t.start()

        return JsonResponse({'data': 'success', 'msg': 'Notification have been sent successfully.'})

    context = {
        'employee': PasEmpPayrollIncharge.objects.filter(payroll_incharge_id=check.first().id),
        'sms_logs': PasEmpPayrollNotification.objects.filter(sentby_id=request.session['emp_id']).order_by('-date_sent')[:10],
        'purpose': InfimosPurpose.objects.order_by('name')
    }
    return render(request, 'epay/payroll_sent_notification.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_payroll_sent_logs(request):
    return render(request, 'epay/payroll_sent_notification_logs.html')


@login_required
@permission_required("auth.payroll_incharge")
def bulk_send_payroll_notification(request):
    if request.method == "POST":
        file = request.FILES['template_file']
        content = file.read().decode('utf-8')
        csvfile = StringIO(content)
        csv_reader = csv.reader(csvfile)

        header_row = next(csv_reader)
        header_str = ','.join(header_row)

        if header_str == 'Purpose,ID Number,Period From,Period To,DV No,Date Processed':
            for row in csv_reader:
                employee = Empprofile.objects.filter(id_number=row[1])

                if employee:
                    if employee.first().pi.mobile_no:
                        purpose = row[0]
                        start_date = datetime.strptime(row[2], "%Y-%m-%d")
                        end_date = datetime.strptime(row[3], "%Y-%m-%d")
                        date_processed = datetime.strptime(row[5], "%Y-%m-%d")

                        formatted_start_date = start_date.strftime("%B %d")
                        formatted_end_date = end_date.strftime("%d, %Y")
                        formatted_date_processed = date_processed.strftime("%B %d, %Y")

                        period_date = "{}-{}".format(formatted_start_date, formatted_end_date)

                        check_purpose = InfimosPurpose.objects.filter(name=row[0])

                        if check_purpose.first().category_id == 5:
                            year_str = str(start_date.year)
                            message = """
                                                Dear {}, please be informed that your {} for the period of {}, 
                                                has already been processed by PAS under the disbursement voucher {} (Date Processed: {}).
                                                HRMDD administrative staff has also transmitted the said DV to FMD for further processing.
                                                Should you have any queries, feel free to contact us. Thank you for your service and dedication.
                                            """.format(employee.first().pi.user.first_name.title(), purpose, year_str, row[4], formatted_date_processed)
                        else:
                            message = """
                                                Dear {}, please be informed that your {} for the period {}, 
                                                has already been processed by PAS under the disbursement voucher {} (Date Processed: {}).
                                                HRMDD administrative staff has also transmitted the said DV to FMD for further processing.
                                                Should you have any queries, feel free to contact us. Thank you for your service and dedication.
                                            """.format(employee.first().pi.user.first_name.title(), purpose.lower(), period_date, row[4], formatted_date_processed)

                        PasEmpPayrollNotification.objects.create(
                            emp_id=employee.first().id,
                            dv_no=row[4],
                            date_sent=datetime.now(),
                            period_date=period_date,
                            sentby_id=request.session['emp_id'],
                            purpose=purpose
                        )

                        t = threading.Thread(target=send_sms_notification,
                                             args=(message, employee.first().pi.mobile_no, request.session['emp_id'], employee.first().id))
                        t.start()

        return JsonResponse({'data': 'success', 'msg': 'Notification have been sent successfully.'})


@login_required
@permission_required("auth.payroll_tracker")
def payroll_workflow(request):
    if request.method == "POST":
        PayrollTimelineWorkFlow.objects.create(
            start_date=request.POST.get('start_date'),
            timeline_id=1,
            assignee_id=request.session['emp_id'],
            date_created=datetime.now(),
            type=request.POST.get('type')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully created a payroll.'})
    context = {
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first()
    }
    return render(request, 'epay/payroll_workflow.html', context)


@login_required
@permission_required("auth.payroll_tracker")
def view_payroll_workflow_detail(request, pk):
    if request.method == "POST":
        PayrollTimelineWorkFlow.objects.filter(id=pk).update(
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') if request.POST.get('end_date') else None,
            date_transmitted=request.POST.get('date_transmitted') if request.POST.get('date_transmitted') else None,
            dv_no=request.POST.get('dv_no'),
            type=request.POST.get('type')
        )

        check = PayrollTimelineWorkFlow.objects.filter(dv_no=request.POST.get('dv_no'), timeline_id=2)

        id_number = re.split('\[|\]', request.POST.get('forward_payroll'))
        employee = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()

        if check:
            check.update(
                dv_no=request.POST.get('dv_no'),
                timeline_id=2,
                assignee_id=employee['id']
            )
        else:
            PayrollTimelineWorkFlow.objects.create(
                dv_no=request.POST.get('dv_no'),
                timeline_id=2,
                assignee_id=employee['id']
            )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated a payroll.'})

    payroll = PayrollTimelineWorkFlow.objects.filter(id=pk).first()
    if payroll.dv_no:
        check = PayrollTimelineWorkFlow.objects.filter(dv_no=payroll.dv_no, timeline_id=2)

        if not check:
            PayrollTimelineWorkFlow.objects.create(
                dv_no=payroll.dv_no,
                timeline_id=2,
            )

    context = {
        'pk': pk,
        'payroll': payroll,
        'forward_payroll': PayrollTimelineWorkFlow.objects.filter(dv_no=payroll.dv_no, timeline_id=2).first(),
    }
    return render(request, 'epay/payroll_workflow_detail.html', context)


@login_required
@permission_required("auth.payroll_tracker")
def view_payroll_tracker(request, dv_no):
    latest_status = PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no).order_by('-id').first()

    if request.method == "POST":
        timeline = request.POST.get('timeline_value')
        PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no, timeline_id=timeline).update(
            date_received=request.POST.get('date_received'),
            start_date=request.POST.get('start_date') if request.POST.get('start_date') else None,
            end_date=request.POST.get('end_date') if request.POST.get('end_date') else None,
            date_transmitted=request.POST.get('date_transmitted') if request.POST.get('date_transmitted') else None,
        )

        if request.POST.get('date_transmitted'):
            forward_payroll = re.split('\[|\]', request.POST.get('forward_payroll'))

            employee = Empprofile.objects.values('id').filter(id_number=forward_payroll[1]).first()

            if employee:
                timeline_forward = int(timeline) + 1
                if timeline_forward <= 4:
                    check = PayrollTimelineWorkFlow.objects.filter(timeline_id=timeline_forward, assignee_id=employee['id'], dv_no=dv_no)
                    if not check:
                        PayrollTimelineWorkFlow.objects.create(
                            timeline_id=timeline_forward,
                            assignee_id=employee['id'],
                            dv_no=dv_no
                        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated payroll tracker for this dv no. {}'.format(dv_no)})

    check_hold = PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no, is_lock=1)

    context = {
        'history': PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no).order_by('-id'),
        'dv_no': dv_no,
        'latest_status': latest_status,
        'check_hold': check_hold.first() if check_hold else None,
        'your_status': PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no, assignee_id=request.session['emp_id']).first(),
        'comments': PayrollTimelineWorkflowComments.objects.filter(dv_no=dv_no).order_by('-date_comment'),
        'check_hold_permission': PortalConfiguration.objects.filter(key_name='Payroll Reviewer', key_acronym=request.session['emp_id'])
    }
    return render(request, 'epay/payroll_tracker.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll_tracker")
def payroll_mark_hold(request, dv_no):
    if request.method == "POST":
        PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no, assignee_id=request.session['emp_id']).update(
            is_lock=1,
            start_date=request.POST.get('start_date') if request.POST.get('start_date') else None,
            date_received=request.POST.get('date_received') if request.POST.get('date_received') else None
        )

        if request.POST.get('comment'):
            PayrollTimelineWorkflowComments.objects.create(
                dv_no=dv_no,
                comment=request.POST.get('comment'),
                date_comment=datetime.now(),
                commentby_id=request.session['emp_id']
            )

        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required("auth.payroll_tracker")
def payroll_unmark_hold(request, dv_no):
    if request.method == "POST":
        PayrollTimelineWorkFlow.objects.filter(dv_no=dv_no, assignee_id=request.session['emp_id']).update(
            is_lock=0
        )

        if request.POST.get('comment'):
            check = PayrollTimelineWorkflowComments.objects.filter(dv_no=dv_no, comment=request.POST.get('comment'))
            if not check:
                check.update(
                    dv_no=dv_no,
                    comment=request.POST.get('comment'),
                    date_comment=datetime.now(),
                    commentby_id=request.session['emp_id']
                )
            else:
                PayrollTimelineWorkflowComments.objects.create(
                    dv_no=dv_no,
                    comment=request.POST.get('comment'),
                    date_comment=datetime.now(),
                    commentby_id=request.session['emp_id']
                )

        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.payroll_tracker")
def add_payroll_timeline_comments(request, dv_no):
    if request.method == "POST":
        PayrollTimelineWorkflowComments.objects.create(
            dv_no=dv_no,
            comment=request.POST.get('comment'),
            date_comment=datetime.now(),
            commentby_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.payroll_tracker")
def payroll_monitoring(request):
    return render(request, 'epay/payroll_monitoring.html')


@login_required
@permission_required("auth.payroll_tracker")
def payroll_monitoring_view(request, start_date, end_date):
    year = start_date.split("-")[0]
    database = year[-2:]
    context = {
        'infimos': Transactions.objects.using('infimos{}'.format(database)).filter(dv_date__range=[start_date, end_date], remarks='Personnel'),
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'epay/payroll_monitoring_view.html', context)


def script_for_auto_add_employee_on_payroll_incharge(request):
    id_number = [
    ]
    for row in id_number:
        employee = Empprofile.objects.filter(id_number=row)
        if employee:
            check_if_exists = PasEmpPayrollIncharge.objects.filter(emp_id=employee.first().id)
            if not check_if_exists:
                PasEmpPayrollIncharge.objects.create(
                    payroll_incharge_id=4,
                    emp_id=employee.first().id
                )

    return HttpResponse("Success")