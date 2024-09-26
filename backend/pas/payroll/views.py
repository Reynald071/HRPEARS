import csv
import io
import re

from calendar import monthrange
from datetime import datetime, date

from django.contrib.auth.decorators import login_required, permission_required

from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook

from backend.models import Empprofile, InfimosPurpose, InfimosCategory, AuthUser, ExtensionName, Position, Empstatus, \
    Personalinfo, Aoa, Fundsource
from backend.pas.payroll.models import PayrollEmployees, PayrollColumns, \
    PayrollColumnType, PayrollOrder, PayrollTransaction, PayrollTemplate, PayrollColumnGroup, PayrollGroup, \
    PayrollEmployeeGroup
from backend.pas.payroll.tags import get_total_deductions, get_amount_accrude, get_amount_deducted_salary, \
    get_amount_due, get_group_total
from frontend.models import PortalConfiguration


@login_required
@permission_required("auth.payroll")
def payroll_employee(request):
    if request.method == "POST":
        user_id = re.split('\[|\]', request.POST.get('employee_name'))
        emp = Empprofile.objects.filter(id_number=user_id[1]).first()
        check = PayrollEmployees.objects.filter(emp_id=emp.id).first()
        if check:
            return JsonResponse({'error': 'error', 'msg': '* Employee name already existed.'})
        else:
            PayrollEmployees.objects.create(
                emp_id=emp.id,
                upload_by_id=request.session['emp_id'],
                status=1,
                is_per_day=0
            )
            return JsonResponse({'data': 'success'})

    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    context = {
        'employee': Paginator(PayrollEmployees.objects.filter(Q(upload_by_id=request.session['emp_id']) &
                                                              Q(emp__pi__user__first_name__icontains=search) |
                                                               Q(emp__pi__user__last_name__icontains=search) |
                                                               Q(emp__pi__user__middle_name__icontains=search) |
                                                               Q(emp__empstatus__name__icontains=search)).order_by('emp__pi__user__last_name'), 50).page(page),
        'employee_group': PayrollEmployeeGroup.objects.filter(upload_by_id=request.session['emp_id']).order_by('name'),
        'management': True,
        'title': 'payroll_management',
        'sub_title': 'employees'
    }
    return render(request, 'backend/pas/payroll/payroll_employee.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll")
def process_employee(request):
    if request.method == "POST":
        employee = request.POST.getlist('data[]')
        if request.POST.get('type') == "delete":
            for row in employee:
                PayrollEmployees.objects.filter(id=row).delete()
        elif request.POST.get('type') == 'move':
            for row in employee:
                PayrollEmployees.objects.filter(id=row).update(
                    empgroup_id=request.POST.get('empgroup')
                )
        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.payroll")
def employee_edit(request, emp_id):
    if request.method == "POST":
        employee = Empprofile.objects.filter(id=emp_id).first()
        AuthUser.objects.filter(id=employee.pi.user_id).update(
            last_name=request.POST.get('last_name'),
            first_name=request.POST.get('first_name'),
            middle_name=request.POST.get('middle_name'),
        )

        Personalinfo.objects.filter(id=employee.pi_id).update(
            ext_id=request.POST.get('extension')
        )

        Empprofile.objects.filter(id=emp_id).update(
            id_number=request.POST.get('id_number'),
            position_id=request.POST.get('position'),
            aoa_id=request.POST.get('aoa'),
            fundsource_id=request.POST.get('fundsource'),
            empstatus_id=request.POST.get('emp_status'),
            salary_rate=request.POST.get('salary_rate'),
            salary_grade=request.POST.get('salary_grade'),
            step_inc=request.POST.get('step_inc'),
        )

        PayrollEmployees.objects.filter(emp_id=emp_id).update(
            remarks=request.POST.get('remarks'),
            status=request.POST.get('status'),
            is_per_day=request.POST.get('is_per_day') if request.POST.get('is_per_day') == '1' else 0
        )

        return JsonResponse({'data': 'success'})

    context = {
        'employee': PayrollEmployees.objects.filter(emp_id=emp_id).first(),
        'extension': ExtensionName.objects.order_by('name'),
        'position': Position.objects.filter(status=1).order_by('name'),
        'emp_status': Empstatus.objects.filter(status=1).order_by('name'),
        'aoa': Aoa.objects.filter(status=1).order_by('name'),
        'fundsource': Fundsource.objects.filter(status=1).order_by('name'),
    }
    return render(request, 'backend/pas/payroll/edit_employee.html', context)


@login_required
@permission_required("auth.payroll")
def employee_group(request):
    if request.method == "POST":
        PayrollEmployeeGroup.objects.create(
            name=request.POST.get('employee_group'),
            upload_by_id=request.session['emp_id'],
            date_created=datetime.now()
        )

        return JsonResponse({'data': 'success'})

    context = {
        'data': PayrollEmployeeGroup.objects.filter(upload_by_id=request.session['emp_id']).order_by('-date_created')
    }
    return render(request, 'backend/pas/payroll/employee_group.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll")
def employee_group_delete(request):
    if request.method == "POST":
        PayrollEmployeeGroup.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.payroll")
def draft_column_group(request):
    if request.method == "POST":
        PayrollColumnGroup.objects.create(
            name=request.POST.get('cg_name'),
            date_created=datetime.now(),
            is_active=1,
            created_by_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success'})
    context = {
        'data': PayrollColumnGroup.objects.filter(created_by_id=request.session['emp_id']).order_by('-date_created')
    }
    return render(request, 'backend/pas/payroll/draft_column_group.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll")
def delete_draft_columns(request):
    if request.method == "POST":
        PayrollColumnGroup.objects.filter(id=request.POST.get('id')).delete()
        PayrollGroup.objects.filter(column_group_id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.payroll")
def draft_column_group_start(request, cg_id):
    if request.method == "POST":
        PayrollColumnGroup.objects.filter(id=cg_id).update(
            name=request.POST.get('cg_name'),
            date_created=datetime.now(),
            is_active=1,
            created_by_id=request.session['emp_id']
        )

        columns = request.POST.getlist('column_start[]')

        for row in columns:
            payroll_group = PayrollGroup.objects.filter(column_group_id=cg_id, column_id=row).first()
            if payroll_group is None:
                PayrollGroup.objects.create(
                    column_group_id=cg_id,
                    column_id=row
                )

        return JsonResponse({'data': 'success'})
    context = {
        'data': PayrollColumnGroup.objects.filter(id=cg_id).first(),
        'default_column': PayrollColumns.objects.order_by('order'),
    }
    return render(request, 'backend/pas/payroll/draft_columns.html', context)


@login_required
@permission_required("auth.payroll")
def payroll_list(request):
    if request.method == "POST":
        filter_dates = request.POST.get('filter_dates')
        if filter_dates == "1":
            period_from = request.POST.get('period_from')
            period_to = request.POST.get('period_to')
        elif filter_dates == "2":
            month = request.POST.get('period_from').split('-')
            period_from = date(int(month[0]), int(month[1]), 1)
            period_to = "{}-{}-{}".format(month[0], month[1], monthrange(int(month[0]), int(month[1]))[1])
        check = PayrollOrder.objects.filter(id=request.POST.get('update_id'))

        columns = request.POST.getlist('column[]')
        if check:
            check.update(
                purpose_id=request.POST.get('purpose'),
                period_from=period_from,
                period_to=period_to,
                upload_by_id=request.session['emp_id'],
                description=request.POST.get('description'),
                payroll_status=request.POST.get('payroll_status'),
                empstatus_id=request.POST.get('empstatus')
            )

            for row in columns:
                payroll_template = PayrollTemplate.objects.filter(payroll_id=request.POST.get('update_id'),
                                                                  column_id=row).first()
                if payroll_template is None:
                    PayrollTemplate.objects.create(
                        payroll_id=request.POST.get('update_id'),
                        column_id=row
                    )
        else:
            payroll = PayrollOrder(
                purpose_id=request.POST.get('purpose'),
                period_from=period_from,
                period_to=period_to,
                upload_by_id=request.session['emp_id'],
                status=0,
                date_created=datetime.now(),
                description=request.POST.get('description'),
                payroll_status=request.POST.get('payroll_status'),
                empstatus_id=request.POST.get('empstatus')
            )

            payroll.save()

            for row in columns:
                PayrollTemplate.objects.create(
                    payroll_id=payroll.id,
                    column_id=row
                )

        return JsonResponse({'data': 'success'})

    page = request.GET.get('page', 1)

    context = {
        'category': InfimosCategory.objects.order_by('name'),
        'purpose': InfimosPurpose.objects.order_by('name'),
        'columns': PayrollColumns.objects.order_by('order'),
        'column_group': PayrollColumnGroup.objects.filter(created_by_id=request.session['emp_id']),
        'employee_group': PayrollEmployeeGroup.objects.filter(upload_by_id=request.session['emp_id']).order_by('name'),
        'data': Paginator(PayrollOrder.objects.filter(upload_by_id=request.session['emp_id']).order_by('-date_created'),
                          20).page(page),
        'title': 'payroll_management',
        'management': True,
        'sub_title': 'payroll_list',
    }
    return render(request, 'backend/pas/payroll/list.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll")
def get_column(request, type_id):
    if request.method == "POST":
        if type_id == 1:
            payroll = [dict(column_id=row.column_id) for row in
                       PayrollTemplate.objects.filter(payroll_id=request.POST.get('payroll_id'))]
            return JsonResponse({'data': payroll})
        elif type_id == 2:
            payroll = [dict(column_id=row.column_id) for row in
                       PayrollGroup.objects.filter(column_group_id=request.POST.get('cg_id'))]
            return JsonResponse({'data': payroll})


@login_required
@permission_required("auth.payroll")
def payrolL_list_view(request, id):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')

    payroll = PayrollTransaction.objects.values('emp_id').distinct() \
        .filter(Q(value__icontains=search), Q(payroll_id=id)).order_by('emp__pi__user__last_name')
    columns = PayrollTemplate.objects.values('column_id').distinct() \
        .filter(column_id__in=[113, 112, 79, 80, 83, 84, 85, 78, 108, 4, 75, 109]).order_by('column__order')

    if payroll:
        for row in payroll:
            check_status = PayrollTransaction.objects.filter(column_id=112, emp_id=row['emp_id'], payroll_id=id).first()
            check_dv = PayrollTransaction.objects.filter(column_id=113, emp_id=row['emp_id'], payroll_id=id).first()
            if not check_status:
                PayrollTransaction.objects.create(
                    column_id=112,
                    emp_id=row['emp_id'],
                    payroll_id=id,
                    value='without DTR'
                )

            if not check_dv:
                PayrollTransaction.objects.create(
                    column_id=113,
                    emp_id=row['emp_id'],
                    payroll_id=id,
                    value=''
                )
    amount_due = PayrollTransaction.objects.filter(payroll_id=id, column_id=75).aggregate(Sum('value'))
    amount_accrude = PayrollTransaction.objects.filter(payroll_id=id, column_id=4).aggregate(Sum('value'))
    total_deductions = PayrollTransaction.objects.filter(payroll_id=id, column__column_type_id=2).aggregate(Sum('value'))
    context = {
        'payroll': Paginator(payroll, rows).page(page),
        'data': PayrollOrder.objects.filter(id=id).first(),
        'columns': columns,
        'pk': id,
        'management': True,
        'amount_due': amount_due,
        'total_deductions': total_deductions,
        'amount_accrude': amount_accrude,
        'title': 'payroll_management',
        'sub_title': 'payroll_list',
    }
    return render(request, 'backend/pas/payroll/list_view.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll")
def status_dtr(request):
    if request.method == "POST":
        employee = request.POST.getlist('data[]')
        if request.POST.get('type') == "without_dtr":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id'),
                                                  column_id=112).update(
                    value="without DTR"
                )
        elif request.POST.get('type') == "with_dtr":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id'),
                                                  column_id=112).update(
                    value="with DTR"
                )
        elif request.POST.get('type') == "to_print":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id'),
                                                  column_id=112).update(
                    value="to Print"
                )
        elif request.POST.get('type') == "completed":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id'),
                                                  column_id=112).update(
                    value="Completed"
                )
        elif request.POST.get('type') == "dv_number":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id'),
                                                  column_id=113).update(
                    value=request.POST.get('dv_number')
                )
        elif request.POST.get('type') == "delete":
            for row in employee:
                PayrollTransaction.objects.filter(emp_id=row, payroll_id=request.POST.get('payroll_id')).delete()

        return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.payroll')
def print_payroll(request, id, type):
    payroll = PayrollTransaction.objects.values('emp_id').distinct() \
        .filter(payroll__upload_by_id=request.session['emp_id'], payroll_id=id, value=type).order_by(
        'emp__pi__user__last_name')
    columns = PayrollTemplate.objects.values('column_id').distinct() \
        .filter(Q(payroll_id=id) & Q(column__is_hidden=False) & ~Q(column_id=108) & ~Q(column_id=112) & ~Q(column_id=113)).order_by('column__order')

    count_received = PayrollColumns.objects.filter(column_type_id__in=[1, 4, 3], id__in=[columns], is_hidden=False).count()
    count_deductions = PayrollColumns.objects.filter(column_type_id__in=[2, 6], id__in=[columns]).count()
    page = request.GET.get('page', 1)

    context = {
        'payroll': Paginator(payroll, 40).page(page),
        'column_type': PayrollColumnType.objects.order_by('id'),
        'data': PayrollOrder.objects.filter(id=id).first(),
        'columns': columns,
        'count_deductions': count_deductions,
        'count_received': count_received + 10,
        'type': type,
        'pk': id
    }
    return render(request, 'backend/pas/payroll/print_payroll.html', context)


@login_required
@permission_required("auth.payroll")
def lock_payroll(request, payroll_id):
    PayrollOrder.objects.filter(id=payroll_id).update(status=1)
    return redirect('payroll_list')


@login_required
@permission_required("auth.payroll")
def unlock_payroll(request, payroll_id):
    PayrollOrder.objects.filter(id=payroll_id).update(status=0)
    return redirect('payroll_list')


@login_required
@permission_required("auth.payroll")
def recalculate(request, payroll_id):
    emp = PayrollTransaction.objects.values('emp_id').distinct().filter(payroll__upload_by_id=request.session['emp_id'],
                                                                        payroll_id=payroll_id).order_by(
        'emp__pi__user__last_name')
    for row in emp:
        check = PayrollEmployees.objects.filter(emp_id=row['emp_id']).first()
        if check.is_per_day:
            get_amount_deducted_salary(row['emp_id'], payroll_id, True)
            get_amount_accrude(row['emp_id'], payroll_id, True)
            get_total_deductions(row['emp_id'], payroll_id)
            get_amount_due(row['emp_id'], payroll_id, True)
        else:
            get_amount_deducted_salary(row['emp_id'], payroll_id)
            get_amount_accrude(row['emp_id'], payroll_id)
            get_total_deductions(row['emp_id'], payroll_id)
            get_amount_due(row['emp_id'], payroll_id)


@login_required
@permission_required("auth.payroll")
def recalculate_url(request, pk):
    emp = PayrollTransaction.objects.values('emp_id').distinct().filter(payroll__upload_by_id=request.session['emp_id'],
                                                                        payroll_id=pk).order_by('emp__pi__user__last_name')
    for row in emp:
        check = PayrollEmployees.objects.filter(emp_id=row['emp_id']).first()
        if check.is_per_day:
            get_amount_deducted_salary(row['emp_id'], pk, True)
            get_amount_accrude(row['emp_id'], pk, True)
            get_total_deductions(row['emp_id'], pk)
            get_amount_due(row['emp_id'], pk, True)
        else:
            get_amount_deducted_salary(row['emp_id'], pk)
            get_amount_accrude(row['emp_id'], pk)
            get_total_deductions(row['emp_id'], pk)
            get_amount_due(row['emp_id'], pk)

    return redirect('payrolL_list_view', id=pk)


@login_required
@permission_required("auth.payroll")
def import_template(request, id):
    if request.method == "POST":
        total = 0
        payroll = PayrollOrder.objects.filter(id=id).first()

        PayrollOrder.objects.filter(id=id).update(auto_calculate=1 if request.POST.get('auto_calculate') == "1" else 0)

        try:
            filename = request.FILES.get('file')
            data_set = filename.read().decode('ISO8859')
            io_string = io.StringIO(data_set)

            column_header = list()
            for row in csv.reader(io_string, delimiter=','):
                column_header = row
                break

            for column in csv.reader(io_string, delimiter=','):
                total += 1
                for indx, row in enumerate(column):
                    columns = PayrollColumns.objects.filter(attribute=column_header[indx]).first()
                    employee = Empprofile.objects.filter(id_number=column[0].strip()).first()

                    if columns:
                        check = PayrollTransaction.objects.filter(payroll_id=id, column_id=columns.id,
                                                                  emp_id=employee.id)
                        if check:
                            check.update(value=row.strip() if row else '0.00')
                        else:
                            payroll = PayrollTransaction(
                                payroll_id=id,
                                column_id=columns.id,
                                emp_id=employee.id,
                                value=row.strip() if row else '0.00')

                            payroll.save()

            if request.POST.get('auto_calculate') == "1":
                recalculate(request, id)  # Function auto compute when upload.

            return JsonResponse({'data': 'success',
                             'msg': 'The csv has been successfully uploaded with Payroll {} ({}-{}). <br>'
                                    'Total processed: {} row(s).'.
                            format(payroll.purpose.name, payroll.period_from.strftime("%Y - %d"),
                                   payroll.period_to.strftime("%d"), total)})
        except Exception as e:
            return JsonResponse({'error': repr(e), 'msg': 'The csv has been successfully uploaded with Payroll {} ({}-{}). <br>'
                                    'Total processed: {} row(s).'.format(payroll.purpose.name, payroll.period_from.strftime("%Y - %d"),
                                   payroll.period_to.strftime("%d"), total)})


@login_required
@permission_required("auth.payroll")
def generate_payroll(request, payroll_id):
    payroll = PayrollOrder.objects.filter(id=payroll_id).first()
    payroll_template = PayrollTemplate.objects.filter(payroll_id=payroll_id).values_list('column_id')
    workbook = Workbook()
    worksheet = workbook.active

    worksheet.title = "{} ({} - {})".format(payroll.purpose.name, payroll.period_from.strftime("%Y - %d"),
                                            payroll.period_to.strftime("%d"))
    default_columns = ["Employee ID"]
    database_columns = [row.attribute for row in
                        PayrollColumns.objects.filter(id__in=payroll_template, is_computed=False,
                                                      is_hidden=False).order_by('order')]
    default_columns.extend(database_columns)

    if payroll.empstatus.name != "All":
        value = PayrollEmployees.objects.filter(upload_by_id=request.session['emp_id'], status=payroll.payroll_status,
                                                empgroup_id=payroll.empstatus_id).values('emp__project__name',
                                                                                         'emp__id_number',
                                                                                         'emp__fundsource__name',
                                                                                         'emp__pi__user__last_name',
                                                                                         'emp__pi__user__first_name',
                                                                                         'emp__pi__user__middle_name',
                                                                                         'emp__empstatus__acronym',
                                                                                         'emp__position__acronym',
                                                                                         'emp__salary_grade',
                                                                                         'emp__step_inc',
                                                                                         'emp__salary_rate').order_by(
            'emp__pi__user__last_name')
    else:
        value = PayrollEmployees.objects.filter(upload_by_id=request.session['emp_id'],
                                                status=payroll.payroll_status).values('emp__project__name',
                                                                                      'emp__id_number',
                                                                                      'emp__fundsource__name',
                                                                                      'emp__pi__user__last_name',
                                                                                      'emp__pi__user__first_name',
                                                                                      'emp__pi__user__middle_name',
                                                                                      'emp__empstatus__acronym',
                                                                                      'emp__position__acronym',
                                                                                      'emp__salary_grade',
                                                                                      'emp__step_inc',
                                                                                      'emp__salary_rate').order_by(
            'emp__pi__user__last_name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(payroll.purpose.name,
                                                                           payroll.period_from.strftime("%Y - %d"),
                                                                           payroll.period_to.strftime("%d"))
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    writer.writerow([smart_str(u"{}".format(row)) for row in default_columns])
    for row in value:
        writer.writerow([
            row['emp__id_number'],
            row['emp__fundsource__name'],
            row['emp__project__name'],
            row['emp__pi__user__last_name'].title(),
            row['emp__pi__user__first_name'].title(),
            row['emp__pi__user__middle_name'].title() if row['emp__pi__user__middle_name'] else '',
            row['emp__position__acronym'],
            row['emp__empstatus__acronym'],
            " {}-{}".format(round(row['emp__salary_grade'], 2), round(row['emp__step_inc'], 2)),
            round(row['emp__salary_rate'], 2),
        ])
    return response


@login_required
@csrf_exempt
def payroll_detail_view(request, payroll_id, emp_id, type):
    if request.method == "POST":
        id = request.POST.getlist('list_id[]')
        value = request.POST.getlist('value[]')
        remarks = request.POST.getlist('remarks[]')

        data = [{'id': i, 'value': v, 'remarks': r}
                for i, v, r in zip(id, value, remarks)]

        for row in data:
            check = PayrollTransaction.objects.filter(emp_id=emp_id, column_id=row['id'], payroll_id=payroll_id)
            if check:
                PayrollTransaction.objects.filter(emp_id=emp_id, column_id=row['id'], payroll_id=payroll_id).update(
                    value=row['value'],
                    remarks=row['remarks']
                )
            else:
                PayrollTransaction.objects.create(
                    emp_id=emp_id,
                    column_id=row['id'],
                    payroll_id=payroll_id,
                    value=row['value'],
                    remarks=row['remarks']
                )

        return JsonResponse({'data': 'success', 'msg': 'The changes were saved successfully.'})

    data = PayrollTransaction.objects.filter(Q(payroll_id=payroll_id), ~Q(value=0.00)).values('column_id').distinct().order_by('column__order')[11:]
    details = PayrollTransaction.objects.filter(payroll_id=payroll_id, emp_id=emp_id)[:9]
    context = {
        'data': data,
        'column_type': PayrollColumnType.objects.order_by('-name'),
        'payroll_id': payroll_id,
        'emp_id': emp_id,
        'details': details,
        'type': type
    }
    return render(request, 'backend/pas/payroll/detail_view.html', context)


@login_required
@permission_required("auth.payroll")
def generate_employee_payslip(request):
    if request.method == "POST":
        type = request.POST.get('type')

        employee = Empprofile.objects.filter(id_number=re.split('\[|\]', request.POST.get('employee'))[1]).first()

        month = request.POST.get('month').split('-')
        list_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                       "November", "December"]

        range = monthrange(int(month[0]), int(month[1]))
        if type == "whole_month":
            period_from = datetime(int(month[0]), int(month[1]), 1)
            period_to = datetime(int(month[0]), int(month[1]), range[1])

            period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], 1,
                                           monthrange(int(month[0]), int(month[1]))[1], month[0])

        elif type == "first_quencena":
            period_from = datetime(int(month[0]), int(month[1]), 1)
            period_to = datetime(int(month[0]), int(month[1]), 15)
            period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], 1, 15, month[0])

        elif type == "second_quencena":
            period_from = datetime(int(month[0]), int(month[1]), 16)
            period_to = datetime(int(month[0]), int(month[1]), range[1])

            period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], 16, range[1], month[0])

        details = PayrollTransaction.objects.filter(Q(emp__id=employee.id),
                                                    (Q(payroll__period_from__gte=period_from) & Q(
                                                        payroll__period_to__lte=period_to)))[2:9]

        copies = request.POST.get('copies')
        columns = PayrollTransaction.objects.values('column_id').distinct().filter(
            Q(emp__id=employee.id),
            (Q(payroll__period_from__gte=period_from) & Q(payroll__period_to__lte=period_to))).exclude(value="0.00")

        total_net_take = 0
        net_take = 0

        if type == "whole_month":
            amount_due = PayrollTransaction.objects.filter(Q(emp__id=employee.id), Q(column__attribute='Amount Due'),
                                                           Q(payroll__purpose__category__name='Salary'),
                                                           (Q(payroll__period_from__gte=period_from) & Q(
                                                               payroll__period_to__lte=period_to)))

            total_due = PayrollTransaction.objects.filter(Q(emp__id=employee.id), Q(column__attribute='Amount Due'),
                                                           (Q(payroll__period_from__gte=period_from) & Q(
                                                               payroll__period_to__lte=period_to)))

        else:
            amount_due = PayrollTransaction.objects.filter(Q(emp__id=employee.id),
                                                           Q(payroll__purpose__category__name='Salary'),
                                                           Q(column__attribute='Amount Due'), (
                                                                       Q(payroll__period_from__gte=period_from) & Q(
                                                                   payroll__period_to__lte=period_to)))

            total_due = PayrollTransaction.objects.filter(Q(emp__id=employee.id), Q(column__attribute='Amount Due'),
                                                          (Q(payroll__period_from__gte=period_from) & Q(
                                                              payroll__period_to__lte=period_to)))

        column_type = PayrollColumnType.objects.filter(id__in=[1, 2]).order_by('id')
        benefits = columns.filter(column__column_type_id=4)
        additional_benefits = columns.filter(column__column_type_id=3)
        config = PortalConfiguration.objects.filter(key_name='Personnel Officer').first()

        for row in amount_due:
            net_take += round(float(row.value.replace(',', '')), 2)

        for row in total_due:
            total_net_take += round(float(row.value.replace(',', '')), 2)

        context = {
            'details': details,
            'columns': columns,
            'config': config,
            'column_type': column_type,
            'benefits': benefits,
            'emp_id': employee.id,
            'additional_benefits': additional_benefits,
            'net_take': net_take,
            'total_net_take': total_net_take,
            'period': period,
            'period_from': period_from,
            'period_to': period_to,
            'date': datetime.now(),
            'with_loans': request.POST.get('loans'),
            'copies': copies
        }
        return render(request, 'frontend/pas/payroll/payslip.html', context)


@login_required
@permission_required("auth.payroll")
def print_obs_dv_form(request):
    if request.method == "POST":
        dv_number = PayrollTransaction.objects.filter(value=request.POST.get('dv_number'))
        payroll_id = dv_number.first()

        payroll_order = PayrollOrder.objects.filter(id=payroll_id.payroll_id).first()
        payroll = PayrollTransaction.objects.filter(emp_id__in=list(dv_number.values_list('emp_id', flat=True)))
        fund_charges = PayrollTransaction.objects.values('value').distinct().filter(
            emp_id__in=list(dv_number.values_list('emp_id', flat=True)), column_id=79)

        total_accrude = 0
        total_due = 0
        for row in fund_charges:
            total_accrude += get_group_total(row['value'], request.POST.get('dv_number'), payroll_order.id)[0]
            total_due += get_group_total(row['value'], request.POST.get('dv_number'), payroll_order.id)[1]

        context = {
            'total_accrude': total_accrude,
            'total_due': total_due,
            'payroll_order': payroll_order,
            'fund_charges': fund_charges,
            'dv_number': request.POST.get('dv_number'),
            'payroll': payroll
        }
        return render(request, 'backend/pas/payroll/print_obs_dv.html', context)


@login_required
@permission_required("auth.payroll")
def payroll_list_all(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    payroll = PayrollTransaction.objects.filter(Q(value__icontains=search)).values('payroll_id', 'emp_id').annotate(ct=Count('id')).order_by('payroll__period_to', 'emp_id')
    columns = PayrollColumns.objects.filter(~Q(id=112), id__in=[113, 112, 79, 80, 83, 84, 85, 78, 108, 4, 75, 109]).values('id').order_by('order')

    context = {
        'payroll': Paginator(payroll, rows).page(page),
        'columns': columns,
        'title': 'payroll_management',
        'management': True,
        'sub_title': 'payroll_list_all'
    }
    return render(request, 'backend/pas/payroll/payroll_viewing.html', context)


@login_required
def download_template(request, id):
    payroll_template = PayrollGroup.objects.filter(column_group_id=id).values_list('column_id')
    group = PayrollColumnGroup.objects.filter(id=id).first()
    workbook = Workbook()
    worksheet = workbook.active

    worksheet.title = "{}".format(group.name)
    default_columns = ["Employee ID"]
    database_columns = [row.attribute for row in
                        PayrollColumns.objects.filter(id__in=payroll_template).order_by('order')]
    default_columns.extend(database_columns)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(group.name)
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    writer.writerow([smart_str(u"{}".format(row)) for row in default_columns])
    return response