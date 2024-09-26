import re
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.db.models.functions import Concat
from django.db.models import Value
from django.views.decorators.csrf import csrf_exempt

from backend.models import PayrollIncharge, Empstatus, Project, InfimosCategory, InfimosPurpose, Empprofile, \
    PortalErrorLogs
from backend.infimos.models import Transactions, ProjectSrc, LibSupplier, LibOthersPayee, EmployeeInfo, Config, \
    TransPayeename, InfimosHistoryTracking
from backend.pas.payroll.models import PayrollTimeline, PayrollTimelineWorkFlow, PayrollWorkflowTemplateData, \
    PayrollWorkflowDetails


@login_required
@permission_required('auth.infimos')
def infimos_beta(request):
    current_date = datetime.now()
    current_year = datetime.now().year
    year = request.GET.get('year', current_year)
    shorten_year = str(year)[-2:]

    if request.method == "POST":
        try:
            with transaction.atomic():
                year = request.POST.get('year')
                shorten_year = str(year)[-2:]

                dv_number = Config.objects.using('infimos' + shorten_year).filter(field_handler='GENERATE_DV').first()
                split_dv_no = re.split('-', dv_number.field_value)

                cutoff_date = datetime(int(year) + 1, 1, 1)
                if current_date >= cutoff_date:
                    current_month = 12
                else:
                    current_month = current_date.month

                accountable = PayrollIncharge.objects.filter(id=request.POST.get('accountable')).first()
                dv_no = "{}-{:02}-{}".format(shorten_year, current_month, split_dv_no[2])
                payee_table_name = ''
                payee_id = ''

                payee = re.split('\[|\]', request.POST.get('payee'))

                if payee[0]:
                    check_lib = LibSupplier.objects.using('libraries').filter(supplier_name=request.POST.get('payee')).first()
                    check_other = LibOthersPayee.objects.using('libraries').filter(name=request.POST.get('payee')).first()
                    if check_lib:
                        payee_table_name = 'lib_supplier'
                        payee_id = check_lib.supplier_id
                    else:
                        payee_table_name = ''
                        payee_id = ''

                    if check_other:
                        payee_table_name = 'lib_others_payee'
                        payee_id = check_other.others_payee_id
                    else:
                        payee_table_name = ''
                        payee_id = ''

                    tr = Transactions.objects.using('infimos' + shorten_year).create(
                        dv_no=dv_no,
                        payee=request.POST.get('payee'),
                        modepayment=request.POST.get('description'),
                        amt_certified=float(request.POST.get('amt_certified').replace(',', '')),
                        accountable=accountable.name,
                        projectsrc_id=request.POST.get('projectsrc'),
                        payee_table_name=payee_table_name,
                        payee_id=payee_id,
                        recon=0,
                        userlog=accountable.username,
                        remarks="Personnel",
                        is_active=0,
                        approval_date=None,
                        scaned_voucher=None,
                        submit_coa=None
                    )

                    TransPayeename.objects.using('infimos' + shorten_year).create(
                        transaction_id=tr.transaction_id,
                        dv_no=dv_no,
                        dv_yr=shorten_year,
                        dv_month=current_month,
                        dv_sequence=tr.transaction_id,
                        validate_budget=0
                    )
                else:
                    tr = Transactions.objects.using('infimos' + shorten_year).create(
                        dv_no=dv_no,
                        payee=payee[2].strip(),
                        modepayment=request.POST.get('description'),
                        amt_certified=float(request.POST.get('amt_certified').replace(',', '')),
                        accountable=accountable.name,
                        projectsrc_id=request.POST.get('projectsrc'),
                        payee_table_name='employee_info',
                        payee_id=payee[1],
                        recon=0,
                        remarks='Personnel',
                        userlog=accountable.username,
                        is_active=0,
                        approval_date=None,
                        scaned_voucher=None,
                        submit_coa=None
                    )

                    TransPayeename.objects.using('infimos' + shorten_year).create(
                        transaction_id=tr.transaction_id,
                        dv_no=dv_no,
                        dv_yr=shorten_year,
                        dv_month=current_month,
                        dv_sequence=tr.transaction_id,
                        validate_budget=0
                    )

                InfimosHistoryTracking.objects.create(
                    dv_no=dv_no,
                    payee=request.POST.get('payee'),
                    projectsrc_id=request.POST.get('projectsrc'),
                    empstatus=request.POST.get('empstatus'),
                    project=request.POST.get('project'),
                    purpose=request.POST.getlist('purpose'),
                    filter_dates=request.POST.get('filter_dates'),
                    date_from=request.POST.get('period_from'),
                    date_to=request.POST.get('period_to') if request.POST.get('period_to') else '',
                    description=request.POST.get('description'),
                    amount_certified=float(request.POST.get('amt_certified').replace(',', '')),
                    accountable=accountable.name,
                    emp_id=accountable.emp_id
                )
                dv_no = re.split('-', dv_number.field_value)
                Config.objects.using('infimos' + shorten_year).filter(field_handler='GENERATE_DV').update(
                    field_value="{}-{:02}-{}".format(shorten_year, current_month, str(int(dv_no[2]) + 1).zfill(len(dv_no[2])))
                )

                return JsonResponse({'data': 'success', 'tracking_no': dv_number.field_value})
            return JsonResponse({'error': True, 'msg': 'Unauthorized Transaction.'})
        except Exception as e:
            print(e)
            PortalErrorLogs.objects.create(
                logs="Infimos: {}".format(e),
                date_created=datetime.now(),
                emp_id=request.session['emp_id']
            )

    context = {
        'ps': ProjectSrc.objects.using('infimos' + shorten_year).all().order_by('name'),
        'empstatus': Empstatus.objects.all().order_by('name'),
        'project': Project.objects.all().order_by('name'),
        'category': InfimosCategory.objects.all().order_by('name'),
        'purpose': InfimosPurpose.objects.all().order_by('name'),
        'accountable': PayrollIncharge.objects.all().order_by('name'),
        'tab_title': 'Infimos Beta',
        'title': 'infimos',
        'year': year
    }
    return render(request, 'backend/infimos/infimos_beta.html', context)


@login_required
@permission_required('auth.infimos')
def infimos_beta_view(request, year, dv_no):
    current_year = year[-2:]
    if request.method == "POST":
        Transactions.objects.using('infimos' + current_year).filter(dv_no=dv_no).update(
            projectsrc_id=request.POST.get('projectsrc'),
            payee=request.POST.get('payee'),
            modepayment=request.POST.get('description'),
            amt_certified=float(request.POST.get('amt_certified').replace(',', '')),
            accountable=request.POST.get('accountable'),
        )

        return JsonResponse({'data': 'success', 'msg': "The DV Number '{}' was successfully updated.".format(dv_no)})
    context = {
        'transactions': Transactions.objects.using('infimos' + current_year).filter(dv_no=dv_no).first(),
        'ps': ProjectSrc.objects.using('infimos' + current_year).all().order_by('name'),
        'year': year
    }
    return render(request, 'backend/infimos/edit_infimos_beta.html', context)


@login_required
@permission_required('auth.infimos')
def filter_payee(request):
    payee = LibSupplier.objects.using('libraries').all().values_list('supplier_name', flat=True)
    others_payee = LibOthersPayee.objects.using('libraries').all().values_list('name', flat=True)
    employee_name = EmployeeInfo.objects.using('libraries').annotate(
        fullname=Concat(Value('['), 'id_number', Value('] '), 'firstname', Value(' '), 'lastname')).values_list(
        'fullname', flat=True)
    results = list(payee) + list(employee_name) + list(others_payee)
    data = json.dumps(results)
    return HttpResponse(data, 'application/json')


@csrf_exempt
@login_required
@permission_required('auth.infimos')
def repeat_last_infimos_transaction(request):
    if request.method == "POST":
        infimos = InfimosHistoryTracking.objects.filter(accountable=request.POST.get('accountable')).last()
        if infimos:
            data = [dict(payee=infimos.payee, projectsrc_id=infimos.projectsrc_id, empstatus=infimos.empstatus,
                         project=infimos.project, accountable=infimos.accountable)]
            return JsonResponse({'data': data})
        return JsonResponse({'error': 'error'})


@login_required
@permission_required('auth.infimos')
def view_payroll_tracker(request, dv_no):
    if request.method == "POST":
        for key, value in request.POST.items():
            if 'column-' in key:
                column_id = key.split('-')[1]
                pfd = PayrollWorkflowDetails()
                pfd.dv_no = dv_no
                pfd.column_id = column_id
                pfd.value = value
                pfd.save()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the payroll details.'})

    context = {
        'dv_no': dv_no,
        'infimos_history': InfimosHistoryTracking.objects.filter(dv_no=dv_no).first(),
        'timeline': PayrollTimeline.objects.order_by('id'),
        'template': PayrollWorkflowTemplateData.objects.filter(pw_id=1),
        'details': PayrollWorkflowDetails.objects.filter(dv_no=dv_no)
    }
    return render(request, 'backend/infimos/view_payroll_tracker.html', context)


@login_required
@permission_required('auth.infimos')
def view_payroll_workflow(request, timeline, dv_no):
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('employee'))
        employee = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()

        PayrollTimelineWorkFlow.objects.filter(timeline_id=timeline, dv_no=dv_no).update(
            start_date=request.POST.get('start_date') if request.POST.get('start_date') else None,
            end_date=request.POST.get('end_date') if request.POST.get('end_date') else None,
            date_transmitted=request.POST.get('date_transmitted') if request.POST.get('date_transmitted') else None,
            date_received=request.POST.get('date_received') if request.POST.get('date_received') else None,
            date_returned=request.POST.get('date_returned') if request.POST.get('date_returned') else None,
            comments=request.POST.get('comments') if request.POST.get('comments') else None,
            assignee_id=employee['id'],
            date_created=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'Success! The payroll workflow has been updated successfully.'})

    if timeline == 1:
        check_infimos = InfimosHistoryTracking.objects.filter(dv_no=dv_no).first()
        check = PayrollTimelineWorkFlow.objects.filter(timeline_id=1, assignee_id=check_infimos.emp_id, dv_no=dv_no)
        if not check:
            PayrollTimelineWorkFlow.objects.create(
                timeline_id=1,
                assignee_id=check_infimos.emp_id,
                dv_no=dv_no
            )
    else:
        check = PayrollTimelineWorkFlow.objects.filter(timeline_id=timeline, dv_no=dv_no)
        if not check:
            PayrollTimelineWorkFlow.objects.create(
                timeline_id=timeline,
                dv_no=dv_no
            )

    context = {
        'workflow': PayrollTimelineWorkFlow.objects.filter(timeline_id=timeline, dv_no=dv_no).first()
    }
    return render(request, 'backend/infimos/view_payroll_workflow.html', context)

