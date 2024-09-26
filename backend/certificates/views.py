import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render

from backend.certificates.models import CertTemplate, CertTransaction
from backend.documents.models import DtsDocument, DtsDrn, DtsTransaction, DtsDivisionCc
from backend.models import Empprofile
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration
from frontend.templatetags.tags import generateDRN


@login_required
def certification_management(request):
    context = {
        'management': True,
        'title': 'certification_management'
    }
    return render(request, 'backend/certification/certification.html', context)


@login_required
def certification_transaction(request, id_number):
    employee = Empprofile.objects.filter(id_number=id_number).first()

    context = {
        'template': CertTemplate.objects.order_by('name'),
        'employee': employee
    }
    return render(request, 'backend/certification/transaction.html', context)


@login_required
def certification_template(request, pk, id_number):
    employee = Empprofile.objects.filter(id_number=id_number).first()
    if request.method == "POST":
        check = CertTransaction.objects.filter(emp_id=employee.id, certtemp_id=pk, status=0)
        config = PortalConfiguration.objects.filter(key_name="LS")

        check.update(
            content=request.POST.get('content'),
            created_by_id=request.session['emp_id'],
            cert_no=int(config.first().key_acronym) + 1 if check.first().certtemp.is_iso else None,
            status=1
        )

        config.update(
            key_acronym=F('key_acronym') + 1
        )

        return JsonResponse({'data': 'success'})

    today = datetime.today()

    check = CertTransaction.objects.filter(emp_id=employee.id, certtemp_id=pk, status=0)

    if not check:
        CertTransaction.objects.create(
            emp_id=employee.id,
            certtemp_id=pk,
            status=0
        )

    transaction = CertTransaction.objects.filter(emp_id=employee.id, certtemp_id=pk, status=0).first()
    context = {
        'template': CertTemplate.objects.filter(id=pk).first(),
        'transaction': transaction,
        'employee': employee,
        'today': today
    }
    return render(request, 'backend/certification/template.html', context)


@login_required
def edit_certificate(request, pk):
    if request.method == "POST":
        CertTransaction.objects.filter(id=pk).update(
            content=request.POST.get('content')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the leave certificate.'})
    context = {
        'transaction': CertTransaction.objects.filter(id=pk).first()
    }
    return render(request, 'backend/certification/edit_template.html', context)


@login_required
def print_certification(request, pk):
    transaction = CertTransaction.objects.filter(id=pk).first()
    today = datetime.today()
    context = {
        'transaction': transaction,
        'cert_no': '%03d' % int(transaction.cert_no) if transaction.cert_no else None,
        'today': today
    }
    return render(request, 'backend/certification/print_certifications.html', context)

