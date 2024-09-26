import json
from calendar import monthrange
from datetime import datetime

from bson import json_util, ObjectId
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from backend.models import InfimosPurpose
from backend.pas.payroll.models import PayrollColumns, PayrollColumnType
from backend.templatetags.tags import getemployeebyempid
from frontend.models import PortalConfiguration
from portal.global_variables import db


@login_required
def f_payroll_list(request):
    context = {
        'current_year': datetime.now().year,
        'columns': PayrollColumns.objects.filter(attribute__in=['Purpose',
                                                                'Period From',
                                                                'Period To',
                                                                'Monthly Rate',
                                                                'Amount Accrued',
                                                                'Amount Due']).order_by('order'),
        'tab_title': 'Payroll',
        'title': 'personnel_transactions',
        'sub_title': 'payroll_view'
    }
    return render(request, 'frontend/pas/payroll/payroll.html', context)


def getKey(collection):
    key_list = []
    for row in collection:
        for field in row.keys():
            key_list.append(field)

    return list(dict.fromkeys(key_list))


@login_required
def generate_user_payslip(request):
    def get_period_data(type, period_from, period_to, employee):
        collection = db["payroll"]
        data = collection.find({
            "$and": [
                {'Period From': period_from},
                {'Period To': period_to},
                {'Employee ID': employee}
            ]
        })
        return data

    try:
        if request.method == "POST":
            type = request.POST.get('type')
            month = request.POST.get('month').split('-')
            list_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                           "November", "December"]

            range = monthrange(int(month[0]), int(month[1]))
            config = PortalConfiguration.objects.filter(key_name='Payslip Signatory').first()
            employee_id = getemployeebyempid(request.session['emp_id']).id_number
            period_from, period_to = None, None

            if type in ["first_quencena", "second_quencena"]:
                start_day = 1 if type == "first_quencena" else 16
                end_day = 15 if type == "first_quencena" else range[1]

                period_from = "{}-{}-{}".format(month[0], month[1], start_day)
                period_to = "{}-{}-{}".format(month[0], month[1], end_day)
                period = "{} {}-{}, {}".format(list_months[int(month[1]) - 1], start_day, end_day, month[0])

                data = get_period_data(type, period_from, period_to, employee_id)

                context = {
                    'loans': 'yes',
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
                common_query = {'Employee ID': employee_id, 'Period From': period_from}
                keys = collection.find(
                    {"$and": [common_query, {'Purpose': 'Salary'}, {'Period To': {"$lte": period_to}}]}).sort(
                    "Period To", 1)

                salary = collection.find({
                    "$or": [
                        {'Period From': period_from},
                        {'Period To': period_to},
                    ],
                    "$and": [
                        {'Employee ID': employee_id},
                    ]
                })

                benefits = InfimosPurpose.objects.filter(category_id=2)
                additional_benefits = InfimosPurpose.objects.filter(category_id=5)
                context = {
                    'loans': 'yes',
                    'salary': json.loads(json_util.dumps(salary)),
                    'keys': json.loads(json_util.dumps(getKey(keys))),
                    'period': period,
                    'year': month[0],
                    'month': month[1],
                    'first_quencena': '{}-{}'.format(month[1], 15),
                    'second_quencena': '{}-{}'.format(16, range[1]),
                    'id_number': getemployeebyempid(request.session['emp_id']).id_number,
                    'benefits': benefits,
                    'additional_benefits': additional_benefits,
                    'date': datetime.now(),
                    'config': config,
                    'type': type
                }
                return render(request, 'frontend/pas/payroll/payslip_viewing.html', context)
    except Exception as e:
        return render(request, 'frontend/pas/payroll/payslip_viewing.html', {'error': "There's no payroll data uploaded within first and second quencena."})


@login_required
def payroll_details_content(request, pk):
    collection = db["payroll"]
    context = {
        'details': json.loads(json_util.dumps(list(collection.find({"_id" : ObjectId(pk)})))),
        'column_type': PayrollColumnType.objects.order_by('order')
    }
    return render(request, 'frontend/pas/payroll/payroll_details_content.html', context)


def get_employee_payroll_list(request, year):
    collection = db["payroll"]

    data = list(collection.find({"Period To": {"$regex": "^{}".format(year), '$options': 'i'},
                                 "Employee ID": getemployeebyempid(request.session['emp_id']).id_number}).sort("Period To", -1))

    data = json.loads(json_util.dumps(data))
    return JsonResponse({'data': data})
