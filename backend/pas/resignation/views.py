import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from backend.models import PasRfd, Rcompliance, Empprofile, Resignationreq, AuthUser, Personalinfo, PasTempseparation


@login_required
@permission_required("auth.resignation_request")
def deactivation_request(request):
    if request.method == "POST":
        user_id = re.split('\[|\]', request.POST.get('user_id'))
        emp = Empprofile.objects.filter(id_number=user_id[1]).first()

        PasRfd.objects.create(
            user_id=emp.id,
            date_effectivity=request.POST.get('date_effectivity'),
            tfs_id=request.POST.get('tempsep'),
            remarks=request.POST.get('remarks'),
            status=0,
        )

        messages.success(request, "The resignation request was successfully added")
        return JsonResponse({'data': 'success'})

    rows = request.GET.get('rows', 20)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')

    context = {
        'data': Paginator(PasRfd.objects.filter(Q(user__pi__user__first_name__icontains=search) |
                                                Q(user__pi__user__last_name__icontains=search) |
                                                Q(user__empstatus__name__icontains=search) |
                                                Q(user__empstatus__acronym__icontains=search) |
                                                Q(user__position__name__icontains=search) |
                                                Q(user__position__acronym__icontains=search) |
                                                Q(date_requested__icontains=search) |
                                                Q(tfs__name__icontains=search)).order_by('-date_requested'), rows)
            .page(page),
        'tempsep': PasTempseparation.objects.all(),
        'title': 'employee',
        'sub_title': 'deactivation_request'
    }
    return render(request, 'backend/pas/resignation/deactivation_request.html', context)


@login_required
@csrf_exempt
@permission_required("auth.resignation_request")
def view_resignation_request(request, pk):
    if request.method == "POST":
        check = Rcompliance.objects.filter(user_id=request.POST.get('emp_id'), rreq_id=request.POST.get('req_id'))

        if check is not None:
            Rcompliance.objects.create(
                user_id=request.POST.get('emp_id'),
                rreq_id=request.POST.get('req_id')
            )

        return JsonResponse({'data': 'success'})

    emp = Empprofile.objects.filter(id=pk).first()
    context = {
        'req': Resignationreq.objects.filter(empstatus_id=emp.empstatus_id),
        'emp': emp,
        'rfd': PasRfd.objects.filter(user_id=pk).first(),
        'total_compliance': Rcompliance.objects.filter(user_id=pk).count(),
    }
    return render(request, 'backend/pas/resignation/view_resignation_detail.html', context)


@login_required
@permission_required("auth.resignation_request")
def deactivate_user(request):
    if request.method == "POST":
        AuthUser.objects.filter(id=request.POST.get('user_id')).update(
            is_active=0,
            is_staff=0
        )

        PasRfd.objects.filter(user_id=request.POST.get('emp_id')).update(
            status=1,
            date_approved=datetime.now()
        )
        return redirect('resignation_request')


@login_required
@csrf_exempt
@permission_required("auth.resignation_request")
def delete_compliance(request):
    Rcompliance.objects.filter(Q(user_id=request.POST.get('emp_id')) & Q(rreq_id=request.POST.get('req_id'))).delete()
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required("auth.resignation_request")
def activate_user(request, pk):
    AuthUser.objects.filter(id=pk).update(is_active=1)
    return JsonResponse({'data': 'success', 'msg': 'User account has been activated successfully!'})


@login_required
@permission_required("auth.resignation_request")
def rfd(request):
    if request.method == "POST":
        PasRfd.objects.create(
            user_id=request.POST.get('user_id'),
            date_effectivity=request.POST.get('date_effectivity'),
            tfs_id=request.POST.get('tempsep'),
            remarks=request.POST.get('remarks'),
            status=0,
        )
        return JsonResponse({'data': 'success'})
