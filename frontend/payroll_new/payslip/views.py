from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render

from backend.templatetags.tags import force_token_decryption

from frontend.payroll_new.models import Payslip
from backend.models import Empprofile


@login_required
def payslip(request):

    context = {
        'title': 'payroll',
        'sub_title': 'payslip',
        'emp': Empprofile.objects.filter(pi__user__id=request.user.id).first() 
    }
    return render(request, 'frontend/payroll_new/payslip/payslip.html', context)


@login_required
def payslip_detail(request, pk):

    context = {
        'payslip': Payslip.objects.using('payslip').filter(id=pk).first(),
    }
    return render(request, 'frontend/payroll_new/payslip/payslip_detail.html', context)

