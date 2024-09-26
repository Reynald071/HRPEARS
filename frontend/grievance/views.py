import re
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from api.wiserv import send_notification
from backend.forms import GrievanceRoaAttachmentsForm
from backend.libraries.grievance.models import GrievanceMedia, GrievanceClassification, GrievanceStatus, GrievanceQuery, \
    GrievanceRecordsOfAction, GrievanceRoaAttachments

from backend.models import Empprofile, ExtensionName
from backend.views import generate_serial_string

from frontend.models import Province


@login_required
@permission_required('auth.grievance_officer')
def grievances(request):
    data = GrievanceQuery.objects.all().order_by('-datetime')
    if request.method == 'POST':
        fn = request.POST.get('first_name')
        mn = request.POST.get('middle_name')
        ln = request.POST.get('last_name')
        en = request.POST.get('ext_name')
        contact = request.POST.get('contact_number')
        date_received = request.POST.get('date_received')
        media = request.POST.get('media')
        prov = request.POST.get('ra_prov_code') if (request.POST.get('ra_prov_code')).strip() != '' else None
        citymun = request.POST.get('ra_city')
        brgy = request.POST.get('ra_brgy')
        detailed_address = request.POST.get('detailed_address')
        details_of_query = request.POST.get('details_of_query')
        status = request.POST.get('status')
        classification = request.POST.get('classification')
        is_confidential = request.POST.get('is_confidential')
        name = None
        files = request.FILES.getlist('attachment')

        if request.POST.get('grievance_officer'):
            nominee = re.split('\[|\]', request.POST.get('grievance_officer'))
            name = Empprofile.objects.filter(id_number=nominee[1]).first()

        grievance_officer = name if name else Empprofile.objects.filter(id=request.session['emp_id']).first()
        date_resolved = request.POST.get('date_resolved') if request.POST.get('date_resolved') else None
        action_taken = request.POST.get('action_taken')

        lasttrack = GrievanceQuery.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'GR')

        x = GrievanceQuery.objects.create(
            tracking_no=track_num,
            client_fname=fn,
            client_mname=mn,
            client_lname=ln,
            client_ext_id=en,
            client_contactnumber=contact,
            client_prov_id=prov,
            client_citymun_id=citymun,
            client_brgy_id=brgy,
            client_message=details_of_query,
            date_received=date_received,
            gmedia_id=media,
            client_address=detailed_address,
            is_confidential=True if is_confidential else False
        )

        if x:
            w = None
            if not (grievance_officer.id == request.session['emp_id']):
                w = GrievanceRecordsOfAction.objects.create(
                    gclassification_id=classification,
                    gquery_id=x.id,
                    gstatus_id=status,
                    emp_id=request.session['emp_id'],
                    date_started=date_received,
                    date_completed=date_resolved if date_resolved else timezone.now(),
                    action_taken_or_answer_to_query='<em>(This query is forwarded to or for follow-up of {}'
                                                    ' {})</em>'.format(grievance_officer.pi.user.first_name,
                                                                       grievance_officer.pi.user.last_name),
                )
                if grievance_officer.pi.mobile_no:
                    message = 'Good day, {}! Grievance query with reference number {} has been assigned to you. - The My PORTAL Team'.format(
                        grievance_officer.pi.user.first_name, x.tracking_no,
                        grievance_officer.pi.mobile_no
                    )
                    send_notification(message, grievance_officer.pi.mobile_no, request.session['emp_id'], grievance_officer.id)

            y = GrievanceRecordsOfAction.objects.create(
                gclassification_id=classification,
                gquery_id=x.id,
                gstatus_id=status,
                emp_id=grievance_officer.id,
                date_started=None if w else date_received,
                date_completed=None if w else date_resolved,
                action_taken_or_answer_to_query=None if w else action_taken,
                datetime=timezone.now() + timezone.timedelta(seconds=10)
            )

        if x and y:
            if y:
                for f in files:
                    file_instance = GrievanceRoaAttachments(attachment=f, roa=w if w else y)
                    file_instance.save()
            return JsonResponse({'data': 'success'})
        else:
            if w:
                z = GrievanceRecordsOfAction.objects.get(pk=w.id)
                z.delete()
            if x:
                z = GrievanceQuery.objects.get(pk=x.id)
                z.delete()
            if y:
                z = GrievanceRecordsOfAction.objects.get(pk=y.id)
                z.delete()
            return JsonResponse({'error': 'failed', 'error': 'Saving of grievance query failed. Please try again.'})

    context = {
        'tab_title': 'Grievances',
        'title': 'grievances',
        'provs': Province.objects.all().order_by('name'),
        'media': GrievanceMedia.objects.filter(is_active=True).order_by('name'),
        'classification': GrievanceClassification.objects.filter(is_active=True).order_by('name'),
        'status': GrievanceStatus.objects.filter(is_active=True).order_by('name'),
        'attachment': GrievanceRoaAttachmentsForm(),
        'extension': ExtensionName.objects.all().order_by('name'),
    }
    return render(request, 'frontend/grievances/grievances.html', context)


@login_required
@permission_required('auth.grievance_officer')
def update_grievance(request):
    if request.method == 'POST':
        status = request.POST.get('update_status')
        classification = request.POST.get('update_classification')
        files = request.FILES.getlist('attachment')
        name = None

        if request.POST.get('update_grievance_officer'):
            nominee = re.split('\[|\]', request.POST.get('update_grievance_officer'))
            name = Empprofile.objects.filter(id_number=nominee[1]).first()
        grievance_officer = name if name else Empprofile.objects.filter(id=request.session['emp_id']).first()
        date_resolved = request.POST.get('update_date_resolved') if request.POST.get('update_date_resolved') else None
        action_taken = request.POST.get('action_taken')

        x = GrievanceQuery.objects.filter(id=request.POST.get('gr_id')).first()
        if x:
            y = x.get_latest_status
            if not (grievance_officer.id == request.session['emp_id']):
                y.gclassification_id = classification
                y.gstatus_id = status
                y.date_completed = date_resolved if date_resolved else timezone.now()
                y.action_taken_or_answer_to_query = '{}<br><em>(This query is forwarded to or for ' \
                                                    'follow-up of {} {})</em>' \
                    .format(action_taken, grievance_officer.pi.user.first_name,
                            grievance_officer.pi.user.last_name)
                y.datetime = timezone.now()
                y.save()

                if grievance_officer.pi.mobile_no:
                    message = 'Good day, {}! Grievance query with reference number {} has been forwarded to you. - The My PORTAL Team'.format(
                        grievance_officer.pi.user.first_name, x.tracking_no,
                        grievance_officer.pi.mobile_no
                    )

                    send_notification(message, grievance_officer.pi.mobile_no, request.session['emp_id'], grievance_officer.id)

                y = GrievanceRecordsOfAction.objects.create(
                    gclassification_id=classification,
                    gquery_id=request.POST.get('gr_id'),
                    gstatus_id=status,
                    emp_id=grievance_officer.id,
                    date_started=None,
                    date_completed=None,
                    action_taken_or_answer_to_query=None,
                    datetime=timezone.now() + timezone.timedelta(seconds=10)
                )
            else:
                y.gclassification_id = classification
                y.gstatus_id = status
                y.date_completed = date_resolved if date_resolved else timezone.now()
                y.action_taken_or_answer_to_query = '{}'.format(action_taken)
                y.datetime = timezone.now()
                y.save()

            if y:
                for f in files:
                    file_instance = GrievanceRoaAttachments(attachment=f, roa=y)
                    file_instance.save()
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'error': 'failed', 'error': 'Saving of grievance query failed. Please try again.'})
    else:
        return JsonResponse({'error': 'failed', 'error': 'You are not authorized to access this content. Please '
                                                         'contact your administrator.'})


@login_required
@permission_required('auth.grievance_officer')
def view_grievance(request, pk):
    data = GrievanceQuery.objects.filter(id=pk).first()
    status = data.get_latest_status
    if status.emp_id == request.session['emp_id'] and not status.date_started:
        x = GrievanceRecordsOfAction.objects.filter(id=status.id).update(
            date_started=timezone.now()
        )
    context = {
        'data': data,
    }
    return render(request, 'frontend/grievances/view_grievance.html', context)


@login_required
@permission_required('auth.grievance_officer')
def get_grievance_latest_status(request, pk):
    data = GrievanceRecordsOfAction.objects.filter(gquery_id=pk).order_by('-datetime', '-id').first()
    return JsonResponse({'employee_id': data.emp_id, 'gstatus_id': data.gstatus_id})


@login_required
def get_grievance_overview(request):
    if request.method == "POST":
        parameter = request.POST.get('parameter')
        dt_from = request.POST.get('dt_from')
        dt_to = request.POST.get('dt_to')
        qry = GrievanceQuery.objects.filter(Q(datetime__gte=dt_from), Q(datetime__lte=dt_to))

        if parameter == 'media':
            return JsonResponse({'data': list(qry.values('gmedia__name')
                                              .annotate(name=F('gmedia__name'), num=Count('gmedia__name')))})
        elif parameter == 'section':
            latest_statuses = []
            for q in qry:
                latest_statuses.append(q.get_latest_status.id)
            qry = GrievanceRecordsOfAction.objects.filter(id__in=latest_statuses)
            return JsonResponse({'data': list(qry.values('emp__section__sec_name')
                                              .annotate(name=F('emp__section__sec_name'),
                                                        num=Count('emp__section__sec_name')))})
        elif parameter == 'province':
            return JsonResponse({'data': list(qry.values('client_prov_id')
                                              .annotate(name=F('client_prov_id'), num=Count('client_prov_id')))})
        elif parameter == 'status':
            latest_statuses = []
            for q in qry:
                latest_statuses.append(q.get_latest_status.id)
            qry = GrievanceRecordsOfAction.objects.filter(id__in=latest_statuses)
            return JsonResponse({'data': list(qry.values('gstatus__name')
                                              .annotate(name=F('gstatus__name'),
                                                        num=Count('gstatus__name')))})

    else:
        return JsonResponse({'error': 'failed', 'error': 'You are not authorized to access this content. Please '
                                                         'contact your administrator.'})


@login_required
def get_province_name(request, id):
    try:
        x = Province.objects.filter(id=id).first()
        return JsonResponse({'data': x.name if x else id})
    except ValueError:
        return JsonResponse({'data': id})
