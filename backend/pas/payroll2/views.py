import csv
import json
import re
import io
from calendar import monthrange
from datetime import datetime

from bson import json_util, ObjectId
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook

from api.wiserv import send_notification
from backend.models import InfimosPurpose, Empprofile
from backend.pas.payroll.models import PayrollColumns, PayrollTaxComputation, PayrollMovsType, PayrollMovs
from frontend.models import PortalConfiguration
from frontend.pas.payroll.views import getKey
from portal.global_variables import db


def payroll_list_all(request):
    context = {
        'current_year': datetime.now().year,
        'columns': PayrollColumns.objects.order_by('order'),
        'management': True,
        'title': 'payroll_management',
        'sub_title': 'payroll_list_all',
    }
    return render(request, 'backend/pas/payroll2/payroll_list.html', context)


def get_payroll_list_all(request, year):
    collection = db["payroll"]
    data = list(collection.find({"Period To": {"$regex": "^{}".format(year), '$options': 'i'}}).sort("_id", -1))
    data = json.loads(json_util.dumps(data))
    return JsonResponse({'data': data})


def payroll_uploading(request):
    collection = db["payroll"]

    if request.method == "POST":
        jsonArray = []
        data_set = request.FILES.get('file').read().decode('ISO8859')
        io_string = io.StringIO(data_set)
        data = csv.DictReader(io_string)
        total = 0
        for row in data:
            jsonArray.append(row)
            total = total + 1

        collection.insert_many(jsonArray)
        return JsonResponse({'data': 'success', 'msg': 'The csv has been successfully uploaded. <br>'
                                    'Total processed: {} row(s)'.format(total)})

    context = {
        'current_year': datetime.now().year,
        'columns': PayrollColumns.objects.order_by('order'),
        'management': True,
        'tab_title': 'Payroll Uploading',
        'title': 'payroll_management',
        'sub_title': 'payroll_uploading',
    }
    return render(request, "backend/pas/payroll2/payroll.html", context)


def new_generate_template(request):
    if request.method == "POST":
        workbook = Workbook()
        worksheet = workbook.active

        worksheet.title = request.POST.get('filename')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(request.POST.get('filename'))
        writer = csv.writer(response, csv.excel)
        writer.writerow(["{}".format(row) for row in request.POST.getlist('column[]')])
        return response


def getPayrollInchargeFullName(emp_id):
    emp = Empprofile.objects.filter(id=emp_id).first()

    if emp.pi.user.middle_name:
        return "{} {}. {}".format(emp.pi.user.first_name.title(), emp.pi.user.middle_name[0].title(), emp.pi.user.last_name.title())
    else:
        return "{} {}".format(emp.pi.user.first_name.title(), emp.pi.user.last_name.title())


def get_payroll_list(request, year):
    collection = db["payroll"]
    data = list(collection.find({"Period To": {"$regex": "^{}".format(year), '$options': 'i'},
                                'Payroll Incharge': getPayrollInchargeFullName(request.session['emp_id'])}).sort("_id", -1))

    data = json.loads(json_util.dumps(data))
    return JsonResponse({'data': data})


@csrf_exempt
def delete_payroll_one(request):
    if request.method == "POST":
        collection = db["payroll"]

        id = request.POST.getlist('id[]')
        for row in id:
            collection.delete_one({"_id": ObjectId(row)})
        return JsonResponse({'data': 'success', 'msg': 'Payroll data successfully deleted.'})


@login_required
def delete_payroll_many(request):
    if request.method == "POST":
        collection = db["payroll"]

        collection.delete_many({"DV Number": request.POST.get('dv_number')})
        return JsonResponse({'data': 'success', 'msg': 'Payroll with DV Number "{}" has successfully deleted'.format(request.POST.get('dv_number'))})


@login_required
def print_payroll(request):
    if request.method == "POST":
        collection = db["payroll"]
        keys = collection.find({'DV Number': request.POST.get('dv_number')})
        data = collection.find({'DV Number': request.POST.get('dv_number')})

        amount_accrued = collection.find({'DV Number': request.POST.get('dv_number')})

        total_amount_accrued = 0
        for row in amount_accrued:
            total_amount_accrued = total_amount_accrued + float(row["Amount Accrued"])

        context = {
            'data': data,
            'keys': json.loads(json_util.dumps(getKey(keys))),
            'amount_accrued': total_amount_accrued,
            'dv_number': request.POST.get('dv_number')
        }
        return render(request, 'backend/pas/payroll2/print_payroll.html', context)


@login_required
def generate_employee_payslip(request):
    def get_period_data(type, period_from, period_to):
        collection = db["payroll"]
        data = collection.find({
            "$and": [
                {'Period From': period_from},
                {'Period To': period_to},
                {'Employee ID': re.split('\[|\]', request.POST.get('employee'))[1]}
            ]
        })
        return data

    try:
        if request.method == "POST":
            type = request.POST.get('type')
            loans = request.POST.get('loans')
            month = request.POST.get('month').split('-')
            list_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            range = monthrange(int(month[0]), int(month[1]))
            config = PortalConfiguration.objects.filter(key_name='Payslip Signatory').first()

            if type in ["first_quencena", "second_quencena"]:
                period_from = "{}-{}-01".format(month[0], month[1])
                period_to = "{}-{}-15".format(month[0], month[1]) if type == "first_quencena" else "{}-{}-{}".format(month[0], month[1], range[1])
                period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], 1, 15 if type == "first_quencena" else 16, month[0])

                data = get_period_data(type, period_from, period_to)

                context = {
                    'loans': request.POST.get('loans'),
                    'data': json.loads(json_util.dumps(data)),
                    'period': period,
                    'date': datetime.now(),
                    'config': config,
                    'type': type
                }
                return render(request, 'frontend/pas/payroll/payslip_viewing.html', context)

            elif type == "whole_month":
                period_from = "{}-{}-01".format(month[0], month[1])
                period_to = "{}-{}-{}".format(month[0], month[1], range[1])
                period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], 1, range[1], month[0])
                collection = db["payroll"]
                keys = collection.find({
                    "$or": [
                        {'Period From': period_from},
                        {'Period To': {"$lte": period_to}},
                    ],
                    "$and": [
                        {'Employee ID': re.split('\[|\]', request.POST.get('employee'))[1]},
                        {'Purpose': 'Salary'}
                    ]
                }).sort("Period To", 1)

                salary = collection.find({
                    "$or": [
                        {'Period From': period_from},
                        {'Period To': period_to},
                    ],
                    "$and":[
                        {'Employee ID': re.split('\[|\]', request.POST.get('employee'))[1]},
                    ]
                })

                benefits = InfimosPurpose.objects.filter(category_id=2)
                additional_benefits = InfimosPurpose.objects.filter(category_id=5)
                context = {
                    'salary': json.loads(json_util.dumps(salary)),
                    'keys': json.loads(json_util.dumps(getKey(keys))),
                    'period': period,
                    'year': month[0],
                    'month': month[1],
                    'first_quencena': '{}-{}'.format(month[1], 15),
                    'second_quencena': '{}-{}'.format(16, range[1]),
                    'id_number': re.split('\[|\]', request.POST.get('employee'))[1],
                    'benefits': benefits,
                    'additional_benefits': additional_benefits,
                    'date': datetime.now(),
                    'config': config,
                    'loans': loans,
                    'type': type
                }
                return render(request, 'frontend/pas/payroll/payslip_viewing.html', context)
    except Exception as e:
        return render(request, 'frontend/pas/payroll/payslip_viewing.html',
                              {'error': "There's no payroll data uploaded within first and second quencena."})


@login_required
@permission_required("auth.payroll_incharge")
def tax(request):
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('employee_name'))
        emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
        if request.POST.get('quarter') == '1':
            check = PayrollTaxComputation.objects.filter(quarter=1, year=request.POST.get('year'), emp_id=emp['id'])
            if check:
                check.update(
                    four_seven=request.POST.get('one_four_seven'),
                    five_two=request.POST.get('one_five_two'),
                    five_three=request.POST.get('one_five_three'),
                    five_four=request.POST.get('one_five_four'),
                    six_three=request.POST.get('one_six_three'),
                )
            else:
                PayrollTaxComputation.objects.create(
                    four_seven=request.POST.get('one_four_seven'),
                    five_two=request.POST.get('one_five_two'),
                    five_three=request.POST.get('one_five_three'),
                    five_four=request.POST.get('one_five_four'),
                    six_three=request.POST.get('one_six_three'),
                    year=request.POST.get('year'),
                    quarter=1,
                    emp_id=emp['id']
                )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully save the first quarter tax computation'})
        elif request.POST.get('quarter') == '2':
            check = PayrollTaxComputation.objects.filter(quarter=2, year=request.POST.get('year'), emp_id=emp['id'])
            if check:
                check.update(
                    four_seven=request.POST.get('two_four_seven'),
                    five_zero=request.POST.get('two_five_zero'),
                    five_two=request.POST.get('two_five_two'),
                    five_three=request.POST.get('two_five_three'),
                    five_four=request.POST.get('two_five_four'),
                    five_six=request.POST.get('two_five_six'),
                    five_seven=request.POST.get('two_five_seven'),
                    five_eight=request.POST.get('two_five_eight'),
                    six_three=request.POST.get('two_six_three'),
                )
            else:
                PayrollTaxComputation.objects.create(
                    four_seven=request.POST.get('two_four_seven'),
                    five_zero=request.POST.get('two_five_zero'),
                    five_two=request.POST.get('two_five_two'),
                    five_three=request.POST.get('two_five_three'),
                    five_four=request.POST.get('two_five_four'),
                    five_six=request.POST.get('two_five_six'),
                    five_seven=request.POST.get('two_five_seven'),
                    five_eight=request.POST.get('two_five_eight'),
                    six_three=request.POST.get('two_six_three'),
                    year=request.POST.get('year'),
                    quarter=2,
                    emp_id=emp['id']
                )
            return JsonResponse({'data': 'success', 'msg': 'You have successfully save the second quarter tax computation'})
        elif request.POST.get('quarter') == '3':
            check = PayrollTaxComputation.objects.filter(quarter=3, year=request.POST.get('year'), emp_id=emp['id'])
            if check:
                check.update(
                    four_seven=request.POST.get('three_four_seven'),
                    five_zero=request.POST.get('three_five_zero'),
                    five_two=request.POST.get('three_five_two'),
                    five_three=request.POST.get('three_five_three'),
                    five_four=request.POST.get('three_five_four'),
                    five_six=request.POST.get('three_five_six'),
                    five_seven=request.POST.get('three_five_seven'),
                    five_eight=request.POST.get('three_five_eight'),
                    six_three=request.POST.get('three_six_three'),
                )
            else:
                PayrollTaxComputation.objects.create(
                    four_seven=request.POST.get('three_four_seven'),
                    five_zero=request.POST.get('three_five_zero'),
                    five_two=request.POST.get('three_five_two'),
                    five_three=request.POST.get('three_five_three'),
                    five_four=request.POST.get('three_five_four'),
                    five_six=request.POST.get('three_five_six'),
                    five_seven=request.POST.get('three_five_seven'),
                    five_eight=request.POST.get('three_five_eight'),
                    six_three=request.POST.get('three_six_three'),
                    year=request.POST.get('year'),
                    quarter=3,
                    emp_id=emp['id']
                )
            return JsonResponse({'data': 'success', 'msg': 'You have successfully save the third quarter tax computation'})
    context = {
        'title': 'payroll_management',
        'sub_title': 'tax',
        'year': datetime.now().year
    }
    return render(request, 'backend/pas/payroll2/tax.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll_incharge")
def get_tax_data(request):
    id_number = re.split('\[|\]', request.POST.get('employee_name'))
    emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
    if request.POST.get('quarter') == '1':
        data = PayrollTaxComputation.objects.\
                values('four_seven', 'five_zero', 'five_two', 'five_three', 'five_four', 'five_six',
                       'five_seven', 'five_eight', 'six_three').\
                    filter(emp_id=emp['id'],
                    year=request.POST.get('year'),
                    quarter=1)
        return JsonResponse({'data': list(data)})
    elif request.POST.get('quarter') == '2':
        data = PayrollTaxComputation.objects. \
            values('four_seven', 'five_zero', 'five_two', 'five_three', 'five_four', 'five_six',
                   'five_seven', 'five_eight', 'six_three'). \
            filter(emp_id=emp['id'],
                   year=request.POST.get('year'),
                   quarter=2)
        if data:
            return JsonResponse({'data_two': list(data)})
        else:
            data = PayrollTaxComputation.objects. \
                values('four_seven'). \
                filter(emp_id=emp['id'],
                       year=request.POST.get('year'),
                       quarter=1)
            return JsonResponse({'data_one': list(data)})
    elif request.POST.get('quarter') == '3':
        data = PayrollTaxComputation.objects. \
            values('four_seven', 'five_zero', 'five_two', 'five_three', 'five_four', 'five_six',
                   'five_seven', 'five_eight', 'six_three'). \
            filter(emp_id=emp['id'],
                   year=request.POST.get('year'),
                   quarter=3)
        if data:
            return JsonResponse({'data_two': list(data)})
        else:
            data = PayrollTaxComputation.objects. \
                values('four_seven', 'five_zero'). \
                filter(emp_id=emp['id'],
                       year=request.POST.get('year'),
                       quarter=2)
            return JsonResponse({'data_one': list(data)})


@login_required
@permission_required("auth.payroll_incharge")
def send_tax_computation(request):
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('employee_name'))
        emp = Empprofile.objects.values('id', 'pi__mobile_no').filter(id_number=id_number[1]).first()
        send_notification(request.POST.get('message'), emp['pi__mobile_no'], request.session['emp_id'], emp['id'])

        return JsonResponse({'data': 'success', 'msg': 'You have successfully sent the notification'})


@login_required
@permission_required("auth.payroll_incharge")
def payroll_movs(request):
    context = {
        'management': True,
        'title': 'payroll_management',
        'sub_title': 'movs',
        'tab_title': 'MOVs',
        'mov_type': PayrollMovsType.objects.filter(status=1)
    }
    return render(request, 'backend/pas/payroll2/movs.html', context)


@login_required
@permission_required("auth.payroll_incharge")
def view_payroll_movs(request, pk):
    if request.method == "POST":
        PayrollMovs.objects.create(
            mov_type_id=pk,
            file=request.FILES.get('file'),
            year=request.POST.get('year'),
            uploaded_by_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully uploaded the movs.'})
    context = {
        'year': datetime.now().year,
        'mov_type': PayrollMovsType.objects.filter(id=pk).first()
    }
    return render(request, 'backend/pas/payroll2/view_movs.html', context)


@login_required
@csrf_exempt
@permission_required("auth.payroll_incharge")
def delete_payroll_movs(request):
    if request.method == "POST":
        PayrollMovs.objects.filter(id=request.POST.get('id')).delete()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully deleted the file'})