
import re
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.db.models.functions import Concat, Upper
from django.db.models import Value
from django.utils.timezone import now

from backend.models import Empprofile
from frontend.models import Outpass, Outpassdetails, Locatorslip



@login_required
def outpass(request):
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('in_behalf_of'))
        if id_number == ['']:
            id_number = Empprofile.objects.filter(id=request.session['emp_id']).first()
            emp = Empprofile.objects.filter(id_number=id_number.id_number).first()
        else:
            emp = Empprofile.objects.filter(id_number=id_number[1]).first()

        if datetime.combine(datetime.strptime(request.POST.get('date'), '%Y-%m-%d'),
                            datetime.strptime(request.POST.get('time_out'), '%H:%M').time()) > datetime.now():
            op = Outpass(status=1, emp_id=request.session['emp_id'],
                         in_behalf_of_id=request.session['emp_id'] if (
                                 request.POST.get('in_behalf_of') == request.session['emp_id'] or request.POST.get(
                             'in_behalf_of') is None) else emp.id)
        else:
            op = Outpass(status=3, emp_id=request.session['emp_id'],
                         in_behalf_of_id=request.session['emp_id'] if (
                                 request.POST.get('in_behalf_of') == request.session['emp_id'] or request.POST.get(
                             'in_behalf_of') is None) else emp.id)
        op.save()

        Outpassdetails.objects.create(
            outpass_id=op.id,
            date=request.POST.get('date'),
            time_out=request.POST.get('time_out'),
            destination=request.POST.get('destination'),
            activity=request.POST.get('activity'),
            nature=request.POST.get('nature'),
            signatory=request.POST.get('signatory')
        )

        Locatorslip.objects.create(
            outpass_id=op.id,
            date=now(),
            status=1,
        )

        return redirect('outpass')

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    op = Outpass.objects.filter(Q(status=1) & Q(in_behalf_of=request.session['emp_id'])).first()
    context = {
        "outpass": Paginator(
            Outpassdetails.objects.filter(
                Q(outpass__in_behalf_of=request.session['emp_id']) & Q(date__icontains=search)).order_by(
                '-date'),
            rows).page(page),
        'opdetails': Outpassdetails.objects.filter(outpass_id=op.id) if op else None,
        'title': 'passport',
        'sub_title': 'outpass',
        'sub_sub_title': 'add_outpass',
        'datetoday': datetime.now().strftime('%Y-%m-%d'),
        'emp_id': request.session['emp_id']
    }
    return render(request, 'frontend/pas/outpass/request-outpass.html', context)


@login_required
def outpass_update(request, pk):
    op = Outpass.objects.filter(id=pk).first()
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('in_behalf_of'))
        if id_number == ['']:
            id_number = Empprofile.objects.filter(id=request.session['emp_id']).first()
            emp = Empprofile.objects.filter(id_number=id_number.id_number).first()
        else:
            emp = Empprofile.objects.filter(id_number=id_number[1]).first()

        opdetails = Outpassdetails.objects.filter(outpass_id=op.id).update(
            date=request.POST.get('date'),
            time_out=request.POST.get('time_out'),
            destination=request.POST.get('destination'),
            activity=request.POST.get('activity'),
            nature=request.POST.get('nature'),
            signatory=None,
        )

        outpass = Outpass.objects.filter(id=op.id).update(
            in_behalf_of_id=request.session['emp_id'] if (request.POST.get('in_behalf_of') == request.session['emp_id'] or request.POST.get('in_behalf_of') is None) else emp.id,
        )
        return redirect('outpass')

    context = {
        'opdetails': Outpassdetails.objects.filter(outpass_id=op.id).first() if op else None,
        'op': op,
        'title': 'passport',
        'sub_title': 'outpass',
        'sub_sub_title': 'add_outpass'
    }
    return render(request, 'frontend/pas/outpass/update-outpass.html', context)


@login_required
def print_outpass(request, pk):
    outpass = Outpass.objects.filter(id=pk).first()
    context = {
        'outpassdetails': Outpassdetails.objects.filter(outpass_id=outpass.id),
        # 'employee': Ritopeople.objects.filter(rito_id=rito.id),
        'name': outpass,
    }
    return render(request, 'frontend/pas/outpass/print_outpass.html', context)


@login_required
def filter_employee_except_me(request):
    employee_name = Empprofile.objects.exclude(id=request.session['emp_id']).annotate(
        fullname=Concat(Value('['), 'id_number', Value('] '), Upper('pi__user__first_name'), Value(' '),
                        Upper('pi__user__last_name'))
    ).values_list('fullname', flat=True)
    results = list(employee_name)
    data = json.dumps(results)
    return HttpResponse(data, 'application/json')


@login_required
def count_outpass_for_date(request, mydate, id):
    x = Outpassdetails.objects.filter(Q(date__icontains=mydate), Q(outpass__in_behalf_of_id=id)).all().count()
    return JsonResponse({'x': x})


@login_required
def get_employee(request, id):  # by id number
    y = Empprofile.objects.filter(id_number=id).first()
    return JsonResponse({'id': y.id})