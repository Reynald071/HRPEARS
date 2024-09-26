import json
import urllib

from bson import json_util
from django import template
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from num2words import num2words

from backend.models import Empprofile
from backend.pas.payroll.models import PayrollTransaction, PayrollColumns, PayrollOrder, PayrollGroup
from portal.global_variables import db

register = template.Library()


@register.simple_tag
def get_employee_details(emp_id):
    return Empprofile.objects.values('id_number').filter(id=emp_id).first()


@register.simple_tag
def get_column_name(column_id):
    column = PayrollColumns.objects.filter(id=column_id).first()
    return column


@register.simple_tag
def get_draft_group(cg_id, column_id):
    check = PayrollGroup.objects.filter(column_group_id=cg_id, column_id=column_id).first()
    if check:
        return True
    else:
        return False


@register.simple_tag
def get_column_type(column_id):
    check = PayrollColumns.objects.filter(id=column_id).first()
    if check:
        column = check.column_type_id
    return column


@register.simple_tag
def get_payroll_value(payroll_id, column_id, emp_id):
    return PayrollTransaction.objects.filter(Q(payroll_id=payroll_id) & Q(column_id=column_id) & Q(emp_id=emp_id) & ~Q(value=0.00)).first()


@register.simple_tag
def get_user_payroll_order(payroll_id):
    return PayrollOrder.objects.filter(id=payroll_id).first()


@register.simple_tag
def get_column_value(column_id, emp_id, period_from, period_to):
    payroll = PayrollTransaction.objects.filter((Q(payroll__period_from__gte=period_from) & Q(payroll__period_to__lte=period_to)),
                                                Q(column_id=column_id), Q(emp_id=emp_id)).exclude(value="0")

    total = 0.0
    for row in payroll:
        if payroll != "" and row.payroll.purpose.category_id != 5 and row.payroll.purpose.category_id != 2:
            total += float(row.value.replace(',', ''))
    return total


@register.simple_tag
def get_benefits_value_on_payslip(column_id, emp_id, period_from, period_to):
    payroll = PayrollTransaction.objects.filter((Q(payroll__period_from__gte=period_from) & Q(payroll__period_to__lte=period_to)),
                                                Q(column_id=column_id), Q(emp_id=emp_id)).exclude(value="0")

    total = 0.0
    for row in payroll:
        if payroll != "" and row.payroll.purpose.category_id == 5 or row.payroll.purpose.category_id == 2:
            total += float(row.value.replace(',', ''))
    return total


@register.simple_tag
def get_additional_benefits_value(column_id, emp_id, period_from, period_to):
    payroll = PayrollTransaction.objects.filter((Q(payroll__period_from__gte=period_from) & Q(payroll__period_to__lte=period_to)),
                                                Q(column_id=column_id), Q(emp_id=emp_id)).exclude(value="")

    total = 0.0
    for row in payroll:
        if payroll != "":
            total += float(row.value.replace(',', ''))
    return total


@register.simple_tag
def get_payslip_total(period_from, period_to, emp_id):
    payroll = PayrollTransaction.objects.filter((Q(payroll__period_from__gte=period_from) & Q(payroll__period_to__lte=period_to)), emp_id=emp_id, column__column_type_id=2).exclude(value="")
    total_deductions = 0.0
    for row in payroll:
        total_deductions += float(row.value.replace(',', ''))

    return [round(total_deductions, 2)]


@register.simple_tag
def parseSrc(src):
    return urllib.parse.quote(src).replace('%20', '+')


@register.simple_tag
def get_total_deductions(emp_id, payroll_id):
    payroll = PayrollTransaction.objects.filter(Q(emp_id=emp_id), Q(payroll_id=payroll_id)).exclude(value="")
    total = 0.0
    for row in payroll:
        if row.column.column_type_id == 2:
            total += float(row.value)

    check = PayrollTransaction.objects.filter(emp_id=emp_id, payroll_id=payroll_id, column_id=109)
    if check:
        check.update(value=round(total, 2))
    else:
        PayrollTransaction.objects.create(
            emp_id=emp_id,
            payroll_id=payroll_id,
            column_id=109,
            value=round(total, 2)
        )

    return total


@register.simple_tag
def get_amount_deducted_salary(emp_id, payroll_id, is_per_day=None):
    payroll = PayrollTransaction.objects.filter(Q(emp_id=emp_id), Q(payroll_id=payroll_id)).exclude(value="")
    total = 0.0
    if is_per_day:
        for row in payroll:
            if row.column_id == 82:
                total += (float(row.value) / 480)
            if row.column_id == 2:
                total = total * float(row.value)
    else:
        for row in payroll:
            if row.column_id == 82:
                total += (float(row.value) / 22)
            elif row.column_id == 2:
                total = total * (float(row.value) / 480)

    check = PayrollTransaction.objects.filter(emp_id=emp_id, payroll_id=payroll_id, column_id=3)
    if check:
        check.update(value=round(total, 2))
    else:
        PayrollTransaction.objects.create(
            emp_id=emp_id,
            payroll_id=payroll_id,
            column_id=3,
            value=round(total, 2)
        )

    return total


@register.simple_tag
def get_amount_accrude(emp_id, payroll_id, is_per_day=None):
    payroll = PayrollTransaction.objects.filter(Q(emp_id=emp_id), Q(payroll_id=payroll_id)).exclude(value="")
    total = 0.0
    benefits = 0.0
    if is_per_day:
        for row in payroll:
            if row.column_id == 82:
                total += float(row.value)
            elif row.column.column_type_id == 3 or row.column.column_type_id == 4:
                benefits += float(row.value)
            elif row.column_id == 1:
                total = total * float(row.value) - get_amount_deducted_salary(emp_id, payroll_id, True)
    else:
        for row in payroll:
            if row.column_id == 82:
                total += (float(row.value) / 22)
            elif row.column.column_type_id == 3 or row.column.column_type_id == 4:
                benefits += float(row.value)
            elif row.column_id == 1:
                total = total * float(row.value) - get_amount_deducted_salary(emp_id, payroll_id)

    overall = total + benefits
    check = PayrollTransaction.objects.filter(emp_id=emp_id, payroll_id=payroll_id, column_id=4)
    if check:
        check.update(value=round(overall, 2))
    else:
        PayrollTransaction.objects.create(
            emp_id=emp_id,
            payroll_id=payroll_id,
            column_id=4,
            value=round(overall, 2)
        )

    return overall


@register.simple_tag
def get_amount_due(emp_id, payroll_id, is_per_day=None):
    check = PayrollTransaction.objects.filter(emp_id=emp_id, payroll_id=payroll_id, column_id=75)
    total = 0.0
    if is_per_day:
        total += float(get_amount_accrude(emp_id, payroll_id, True)) - float(get_total_deductions(emp_id, payroll_id))
    else:
        total += float(get_amount_accrude(emp_id, payroll_id)) - float(get_total_deductions(emp_id, payroll_id))

    if check:
        check.update(value=round(total, 2))
    else:
        PayrollTransaction.objects.create(
            emp_id=emp_id,
            payroll_id=payroll_id,
            column_id=75,
            value=round(total, 2)
        )
    return total


@register.simple_tag
def get_overall_value(payroll_id, column_id, type):
    types = list(PayrollTransaction.objects.filter(value=type, payroll_id=payroll_id).values_list('emp_id', flat=True))
    payroll = PayrollTransaction.objects.filter(payroll_id=payroll_id, emp_id__in=types, column_id=column_id)
    if column_id == 83:
        return len(types)
    else:
        return payroll.aggregate(Sum('value'))['value__sum'] if payroll.aggregate(Sum('value'))['value__sum'] != 0 else '-'


@register.simple_tag
def amount_to_words(amount):
    total = amount.split('.')
    amount_in_words = "{} pesos".format(num2words(total[0])).title()
    if int(total[1]) > 0:
        amount_in_words = amount_in_words.replace(' And', '').strip() + " and {}/100 only".format(total[1])

    return amount_in_words


@register.simple_tag
def get_sheet_value(page, pk, type):
    payroll = PayrollTransaction.objects.values('emp_id').distinct() \
        .filter(payroll_id=pk, value=type).order_by(
        'emp__pi__user__last_name')
    return Paginator(payroll, 40).page(page)


@register.simple_tag
def get_group_total(charges, dv, payroll_id):
    payroll = PayrollTransaction.objects.filter(Q(payroll_id=payroll_id) & Q(value=dv)).values_list('emp_id', flat=True)
    dv_number_values = PayrollTransaction.objects.filter(Q(emp_id__in=list(payroll)) & Q(payroll_id=payroll_id))

    amount_accrude = []
    amount_due = []
    fund_charges = []

    for row in dv_number_values:
        if row.column_id == 4:
            amount_accrude.append(row.value)
        if row.column_id == 75:
            amount_due.append(row.value)
        if row.column_id == 79:
            fund_charges.append(row.value)

    total_amount_due = 0.0
    total_amount_accrude = 0.0
    try:
        index_fund_charges = [i for i, e in enumerate(fund_charges) if e == charges]
        for row in index_fund_charges:
            total_amount_accrude += float(amount_accrude[row])
            total_amount_due += float(amount_due[row])
    except IndexError:
        index_fund_charges = []

    return [total_amount_accrude, total_amount_due]


@register.simple_tag
def check_column(key, column_type, loans):
    if column_type == "details":
        check = PayrollColumns.objects.filter(Q(attribute=key) & Q(column_type_id=7))
        return True if check else False
    elif column_type == "received":
        check = PayrollColumns.objects.filter(Q(attribute=key) & Q(column_type_id=1))
        return True if check else False
    elif column_type == "deduction":
        if loans == 'no':
            check = PayrollColumns.objects.filter(Q(attribute=key) & Q(column_type_id=2) & ~Q(attribute__icontains='loan'))
        else:
            check = PayrollColumns.objects.filter(
                Q(attribute=key) & Q(column_type_id=2))

        return True if check else False


@register.simple_tag
def get_quencena_value(type, quencena, month, year, id_number, key):
    if type == "first_quencena":
        period_from = "{}-{}-01".format(year, month)
        period_to = "{}-{}-15".format(year, month)
        collection = db["payroll"]
        data = collection.find_one({"$and": [{'Period From': period_from}, {'Period To': period_to},
                                         {'Employee ID': id_number}]})
        try:
            return data[key]
        except KeyError:
            return ""
    elif type == "second_quencena":
        value = quencena.split('-')
        period_from = "{}-{}-16".format(year, month)
        period_to = "{}-{}-{}".format(year, month, value[1])
        collection = db["payroll"]
        data = collection.find_one({"$and": [{'Period From': period_from}, {'Period To': period_to},
                                         {'Employee ID': id_number}]})
        try:
            return data[key]
        except KeyError:
            return ""


@register.simple_tag
def get_benefits_value(month, year, quencena, id_number, key):
    value = quencena.split('-')
    period_from = "{}-{}-01".format(year, month)
    period_to = "{}-{}-{}".format(year, month, value[1])
    collection = db["payroll"]
    data = collection.find_one({"$and": [{'Period From': period_from}, {'Period To': period_to},
                                     {'Employee ID': id_number}, {'Purpose': key}]})
    if data:
        return data['Amount Due']


@register.simple_tag
def get_column_id(attribute):
    check = PayrollColumns.objects.filter(attribute__iexact=attribute.strip()).first()
    if check:
        return [check.id, check.is_computed, check.attribute]

