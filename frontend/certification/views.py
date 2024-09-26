from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from backend.certificates.models import CertTemplate, CertRequest
from backend.models import Empprofile
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration


@login_required
def certification(request):
    if request.method == "POST":
        now = datetime.now()
        config = PortalConfiguration.objects.filter(key_name='CERTIFICATION').first()

        lasttrack = CertRequest.objects.order_by('-tracking_no').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'CF')

        certificate = CertRequest(
            tracking_no=track_num,
            template_id=request.POST.get('template'),
            purpose=request.POST.get('purpose'),
            date_of_filing=datetime.now(),
            status=0,
            emp=Empprofile.objects.get(id=request.session['emp_id']),
        )

        certificate.save()

        PortalConfiguration.objects.filter(key_name='CERTIFICATION').update(counter=config.counter + 1)
        return JsonResponse(
            {'data': track_num})

    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    context = {
        'data': Paginator(
            CertRequest.objects.filter(Q(emp_id=request.session['emp_id']), (Q(tracking_no__icontains=search) |
                                       Q(template__name__icontains=search)),
                                       Q(status__icontains=status)).order_by('status', '-date_of_filing'), 10).page(
            page),
        'date': datetime.now(),
        'templates': CertTemplate.objects.all(),
        'tab_title': 'Certification Requests',
        'title': 'personnel_transactions',
        'sub_title': 'certification_request'
    }
    return render(request, 'frontend/certification/certification.html', context)


@login_required
def cancel_certificate_request(request, pk):
    cert = CertRequest.objects.filter(id=pk).first()
    CertRequest.objects.filter(id=pk).update(status=2)
    return JsonResponse({'data': cert.tracking_no})
