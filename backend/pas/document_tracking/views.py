import re
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from backend.models import Empprofile
from backend.pas.document_tracking.models import DocsType, DocsTrackingInfo, DocsTrackingStatus, DocsTrail, DocsCopy
from backend.views import generate_serial_string


def document_tracking(request):
    if request.method == "POST":
        employee = request.POST.getlist('employee[]')

        lasttrack = DocsTrackingInfo.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'DT')

        docs = DocsTrackingInfo(
            tracking_no=track_num,
            from_field=request.POST.get('from'),
            origin=request.POST.get('origin'),
            document_type_id=request.POST.get('doc_type'),
            subject=request.POST.get('subject'),
            purpose=request.POST.get('purpose'),
            details=request.POST.get('details'),
            date_received=request.POST.get('date_received'),
            date_added=datetime.now(),
            emp_id=request.session['emp_id']
        )

        docs.save()
        DocsTrackingStatus.objects.create(
            doc_info_id=docs.id,
            trail_id=2,
            date=datetime.now(),
            id_number=request.session['emp_id'],
        )

        DocsTrackingStatus.objects.create(
            doc_info_id=docs.id,
            trail_id=1,
            date=datetime.now(),
            id_number=re.split('\[|\]', request.POST.get('to'))[1],
        )

        if employee[0] != '':
            for row in employee:
                DocsCopy.objects.create(
                    id_number=re.split('\[|\]', row)[1],
                    doc_track_id=docs.id,
                )

        return JsonResponse({'data': 'success'})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    current_year = request.GET.get('current_year', datetime.now().year)

    context = {
        'data': Paginator(DocsTrackingInfo.objects.filter(Q(date_added__year__icontains=current_year))
                          .order_by('-date_added'), rows).page(page),
        'doc_type': DocsType.objects.filter(is_active=1),
        'doc_trail': DocsTrail.objects.order_by('name'),
        'management': True,
        'title': 'documents',
        'sub_sub_title': 'tracking',
        'current_year': current_year
    }
    return render(request, 'backend/documents/document_tracking.html', context)


def document_details(request, pk):
    if request.method == "POST":
        if request.POST.get('to'):
            DocsTrackingStatus.objects.create(
                doc_info_id=pk,
                trail_id=2,
                date=datetime.now(),
                id_number=re.split('\[|\]', request.POST.get('to'))[1]
            )
        else:
            DocsTrackingStatus.objects.filter(id=request.POST.get('id')).update(
                trail_id=request.POST.get('status'),
                remarks=request.POST.get('remarks'),
                date=datetime.now()
            )
    emp = Empprofile.objects.filter(id=request.session['emp_id']).first()
    check = DocsTrackingStatus.objects.filter(doc_info_id=pk, id_number=emp.id_number).last()

    context = {
        'data': DocsTrackingInfo.objects.filter(id=pk).first(),
        'trail': DocsTrackingStatus.objects.filter(doc_info_id=pk),
        'doc_trail': DocsTrail.objects.order_by('name'),
        'check': check
    }
    return render(request, 'backend/documents/document_details.html', context)