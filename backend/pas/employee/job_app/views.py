from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render

from backend.templatetags.tags import force_token_decryption

from backend.models import PositionVacancy
from landing.models import AppStatus, JobApplication, AppEligibility


@login_required
@permission_required("auth.recruitment")
def job_app(request):

    context = {
        'title': 'recruit',
        'sub_title': 'job_app',
        'app_status': AppStatus.objects.filter(status=1).order_by('order')
    }
    return render(request, 'backend/recruitment/job_app.html', context)


@login_required
@permission_required("auth.recruitment")
def application_detail(request, pk):

    context = {
        'application': JobApplication.objects.filter(id=pk).first(),
        'el': AppEligibility.objects.filter(app_id=pk),
    }
    return render(request, 'backend/recruitment/application_view.html', context)


@login_required
@permission_required('auth.recruitment')
def app_totals(request):
    total_app = JobApplication.objects.all().count()
    job_app = JobApplication.objects.filter(Q(is_rejected=0) | Q(is_rejected__isnull=True))
    total_new_app = job_app.filter(app_status_id=1).count()
    total_paperscreen = job_app.filter(app_status_id=2).count()
    total_qualified = job_app.filter(app_status_id=3).count()
    total_initial_qual = job_app.filter(app_status_id=4).count()
    total_technical = job_app.filter(app_status_id=5).count()
    total_interview = job_app.filter(app_status_id=6).count()
    total_deliberation = job_app.filter(app_status_id=7).count()
    total_appointed = job_app.filter(app_status_id=8).count()
    total_hired = job_app.filter(app_status_id=9).count()
    total_reject = JobApplication.objects.filter(is_rejected=1).count()

    return JsonResponse({
        'total_app': total_app,
        'total_new_app': total_new_app,
        'total_paperscreen': total_paperscreen,
        'total_qualified': total_qualified,
        'total_initial_qual': total_initial_qual,
        'total_technical': total_technical,
        'total_interview': total_interview,
        'total_deliberation': total_deliberation,
        'total_appointed': total_appointed,
        'total_hired': total_hired,
        'total_reject': total_reject,
    })


@login_required
@permission_required("auth.recruitment")
def vacancy_detail(request, pk):
    job_app = JobApplication.objects.filter(id=pk).first()

    context = {
        'vacancy': job_app.vacancy,
    }
    return render(request, 'backend/recruitment/vacancy_view.html', context)


@csrf_exempt
@login_required
@permission_required('auth.recruitment')
def approve_application(request):
    if request.method == "POST":
        job_app = JobApplication.objects.filter(id=request.POST.get('id')).first()
        next_status_order = job_app.app_status.order + 1
        new_status = AppStatus.objects.filter(order=next_status_order).first()

        job_app.app_status_id = new_status.id
        job_app.save()

        if new_status.id == 9:
            total_hired_app = JobApplication.objects.filter(vacancy_id=job_app.vacancy_id, app_status_id=9).count()
            if job_app.vacancy.quantity == total_hired_app:
                PositionVacancy.objects.filter(id=job_app.vacancy_id).update(status=2)

        return JsonResponse({'data': 'success', 'status': new_status.name})


@csrf_exempt
@login_required
@permission_required('auth.recruitment')
def reject_application(request):
    if request.method == "POST":
        JobApplication.objects.filter(id=request.POST.get('id')).update(is_rejected=1)

        return JsonResponse({'data': 'success'})


@login_required
@permission_required("auth.recruitment")
def remarks(request, pk):

    if request.method == "POST":
        JobApplication.objects.filter(id=pk).update(remarks=request.POST.get('remarks'))

        return JsonResponse({'data': 'success'})

    context = {
        'application': JobApplication.objects.filter(id=pk).first(),
    }
    return render(request, 'backend/recruitment/remarks.html', context)
