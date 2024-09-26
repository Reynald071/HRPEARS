import re
import json
import requests
from datetime import datetime, date

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, F
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1

from backend.models import Empprofile
from frontend.models import Rito, Ritodetails, Ritopeople, Claims, Mot, PortalConfiguration, RitoAttachment
from frontend.templatetags.tags import gamify


def check_rito_confirmation_function(inclusive_from, emp_id):
    ritodetail = Ritodetails.objects.filter(Q(rito__status=1) & Q(rito__emp_id=emp_id)).first()
    for_confirm_rito = False
    not_for_confirm_rito = False
    inclusive_from = datetime.strptime(inclusive_from, '%Y-%m-%d')

    if ritodetail:
        if date.today() > ritodetail.inclusive_from:
            for_confirm_rito = True
        else:
            not_for_confirm_rito = True

    if date.today() > inclusive_from.date():
        for_confirm_rito = True
    else:
        not_for_confirm_rito = True

    return True if for_confirm_rito and not_for_confirm_rito else False


@login_required
@permission_required('auth.rito')
def get_travel_totals(request):
    total_requests = Rito.objects.filter(emp_id=request.session['emp_id'], status__in=[2, 3, 5]).count()
    total_drafts = Rito.objects.filter(emp_id=request.session['emp_id'], status=4).count()
    init_requests = Rito.objects.filter(emp_id=request.session['emp_id'], status=1).first()
    if init_requests:
        total_init_requests = Ritodetails.objects.filter(rito_id=init_requests.id).count()
    else:
        total_init_requests = 0
    return JsonResponse({'drafts': total_drafts, 'requests': total_requests, 'init_requests': total_init_requests})


def interval_rito_date_conflict(start_date, end_date, emp_id, rito_pk=None):
    conflict_query = Ritopeople.objects.filter(
        Q(detail__inclusive_from__lte=end_date, detail__inclusive_to__gte=start_date),
        Q(name_id=emp_id),
        ~Q(detail__rito__status=5)
    )

    # If rito_pk is provided, exclude it from the conflict check
    if rito_pk:
        conflict_query = conflict_query.exclude(detail_id=rito_pk)

    return conflict_query


@login_required
@permission_required('auth.rito')
def rito(request):
    if request.method == "POST":
        id = request.POST.get('draftid')
        if id == '' or id is None:
            check = Rito.objects.filter(Q(status=1) & Q(emp_id=request.session['emp_id'])).first()
        else:
            check = Rito.objects.filter(Q(id=id)).first()

        employee = request.POST.getlist('employee[]')

        employee_list = []
        for row in employee:
            id_number = re.split('\[|\]', row)
            emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
            check_conflict = interval_rito_date_conflict(request.POST.get('from'), request.POST.get('to'), emp['id'])

            if check_conflict:
                employee_list.append({
                    'name': check_conflict.first().name.pi.user.first_name.upper(),
                    'text_date': 'specified dates' if request.POST.get('from') != request.POST.get(
                        'to') else 'specified date',
                    'to_number': [row.detail.rito.tracking_no if row.detail.rito.tracking_no else "drafted by {}".format(row.detail.rito.emp.pi.user.get_fullname.upper())
                                      for row in check_conflict],
                    'text_to': 'Travel Orders' if check_conflict.count() > 1 else 'Travel Order'
                })

        if employee_list:
            return JsonResponse({'error': True, 'conflict': employee_list})
        else:
            if check:
                check_confirmation = check_rito_confirmation_function(request.POST.get('from'), request.session['emp_id'])

                if check_confirmation:
                    return JsonResponse({'error': True, 'confirmation': True})

                details = Ritodetails(
                    rito_id=check.id,
                    place=request.POST.get('places'),
                    inclusive_from=request.POST.get('from'),
                    inclusive_to=request.POST.get('to'),
                    purpose=request.POST.get('purpose'),
                    expected_output=request.POST.get('expected_output'),
                    claims_id=request.POST.get('claims'),
                    mot_id=request.POST.get('mot'))

                details.save()

                employee = request.POST.getlist('employee[]')

                for row in employee:
                    id_number = re.split('\[|\]', row)
                    name = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
                    Ritopeople.objects.create(
                        detail_id=details.id,
                        name_id=name['id'])
            else:
                config = PortalConfiguration.objects.filter(key_name='TRAVEL').first()

                current_counter = config.counter + 1
                current_year = datetime.now().year
                current_month = datetime.now().month

                tracking_no = 'TO-{}-{}-{}'.format(
                    str(current_year).zfill(4),
                    str(current_month).zfill(2),
                    '%04d' % int(current_counter)
                )

                to = Rito(
                    tracking_no=tracking_no,
                    status=1,
                    emp_id=request.session['emp_id'])

                to.save()

                PortalConfiguration.objects.filter(key_name='TRAVEL').update(
                    counter=F('counter') + 1
                )

                details = Ritodetails(
                    rito_id=to.id,
                    place=request.POST.get('places'),
                    inclusive_from=request.POST.get('from'),
                    inclusive_to=request.POST.get('to'),
                    purpose=request.POST.get('purpose'),
                    expected_output=request.POST.get('expected_output'),
                    claims_id=request.POST.get('claims'),
                    mot_id=request.POST.get('mot'))

                check_confirmation = check_rito_confirmation_function(details.inclusive_from.strftime('%Y-%m-%d'), request.session['emp_id'])

                if check_confirmation:
                    return JsonResponse({'error': True, 'confirmation':  True})

                details.save()

                employee = request.POST.getlist('employee[]')
                for row in employee:
                    id_number = re.split('\[|\]', row)
                    name = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
                    Ritopeople.objects.create(
                        detail_id=details.id,
                        name_id=name['id'])

            return JsonResponse({'data': "success"})

    context = {
        'claims': Claims.objects.filter(status=1).order_by('name'),
        'mot': Mot.objects.filter(status=1).order_by('name'),
        'tab_parent': 'Travel Management',
        'tab_title': 'Travel Requests',
        'title': 'travel_management',
        'sub_title': 'travel',
    }
    return render(request, 'frontend/pas/rito/rito.html', context)


@login_required
@permission_required('auth.rito')
def edit_rito(request, pk):
    if request.method == "POST":
        employee = request.POST.getlist('employee[]')
        employee_list = []
        employee_list_not = []
        for row in employee:
            id_number = re.split('\[|\]', row)
            emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
            check = Ritopeople.objects.filter(detail__inclusive_from=request.POST.get('from'),
                                              detail__inclusive_to=request.POST.get('to'), name_id=emp['id']).first()

            if not check:
                check_conflict = interval_rito_date_conflict(request.POST.get('from'), request.POST.get('to'),
                                                             emp['id'])
                if check_conflict:
                    employee_list.append({
                        'name': check_conflict.first().name.pi.user.first_name.upper(),
                        'text_date': 'specified dates' if request.POST.get('from') != request.POST.get(
                            'to') else 'specified date',
                        'to_number': [row.detail.rito.tracking_no if row.detail.rito.tracking_no else "drafted by {}".format(row.detail.rito.emp.pi.user.get_fullname.upper())
                                      for row in check_conflict],
                        'text_to': 'Travel Orders' if check_conflict.count() > 1 else 'Travel Order'
                    })
                else:
                    employee_list_not.append(emp['id'])

        if employee_list_not:
            for row in employee_list_not:
                check_conflict = interval_rito_date_conflict(request.POST.get('from'), request.POST.get('to'),
                                                             emp['id'])
                if check_conflict:
                    employee_list.append({
                        'name': check_conflict.first().name.pi.user.first_name.upper(),
                        'text_date': 'specified dates' if request.POST.get('from') != request.POST.get(
                            'to') else 'specified date',
                        'to_number': [row.detail.rito.tracking_no for row in check_conflict],
                        'text_to': 'Travel Orders' if check_conflict.count() > 1 else 'Travel Order'
                    })
                else:
                    Ritopeople.objects.create(
                        detail_id=pk,
                        name_id=row
                    )

        if not employee_list:
            Ritodetails.objects.filter(id=pk).update(
                place=request.POST.get('places'),
                inclusive_from=request.POST.get('from'),
                inclusive_to=request.POST.get('to'),
                purpose=request.POST.get('purpose'),
                expected_output=request.POST.get('expected_output'),
                claims_id=request.POST.get('claims'),
                mot_id=request.POST.get('mot')
            )

            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'error': True, 'conflict': employee_list})

    context = {
        'rito': Ritodetails.objects.filter(id=pk).first(),
        'ritopeople': Ritopeople.objects.filter(detail_id=pk),
        'claims': Claims.objects.filter(status=1).order_by('name'),
        'mot': Mot.objects.filter(status=1).order_by('name'),
    }
    return render(request, 'frontend/pas/rito/edit_rito.html', context)


@csrf_exempt
@login_required
@permission_required('auth.rito')
def travel_undraft(request):
    Rito.objects.filter(emp_id=request.session['emp_id'], status=1).update(status=4)

    Rito.objects.annotate(hash=SHA1('id')).filter(hash=request.POST.get('pk')).update(
        status=1
    )
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@permission_required('auth.rito')
def delete_rito(request):
    Ritodetails.objects.filter(id=request.POST.get('id')).delete()
    Ritopeople.objects.filter(detail_id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.rito')
def delete_drafts(request, id):
    ritodetails = Ritodetails.objects.filter(rito_id=id)
    for row in ritodetails:
        Ritopeople.objects.filter(detail_id=row.id).delete()
    Ritodetails.objects.filter(rito_id=id).delete()
    Rito.objects.filter(id=id).delete()
    return redirect('rito')


@login_required
@permission_required('auth.rito')
def submit_rito(request):
    if request.POST.get('draftid2') == '':
        rito = Rito.objects.filter(Q(status=1) & Q(emp_id=request.session['emp_id']))
    else:
        rito = Rito.objects.filter(Q(id=request.POST.get('draftid2')))

    if rito:
        tracking_no = ''
        if not rito.first().tracking_no:
            config = PortalConfiguration.objects.filter(key_name='TRAVEL').first()

            current_counter = config.counter + 1
            current_year = datetime.now().year
            current_month = datetime.now().month

            tracking_no = 'TO-{}-{}-{}'.format(
                str(current_year).zfill(4),
                str(current_month).zfill(2),
                '%04d' % int(current_counter)
            )

            rito.update(
                tracking_no=tracking_no,
                status=2,
                date=datetime.now())

            PortalConfiguration.objects.filter(key_name='TRAVEL').update(
                counter=F('counter') + 1
            )

            tracking_no = tracking_no
        else:
            tracking_no = rito.first().tracking_no

            rito.update(
                status=2,
                date=datetime.now())
        # Save points for RITO
        gamify(14, request.session['emp_id'])

        return JsonResponse({'data': tracking_no})
    else:
        return JsonResponse({'error': "Sorry, it seems like you have empty RITO's."})


@login_required
@csrf_exempt
@permission_required('auth.rito')
def draft_rito(request):
    if request.POST.get('id') == '' or request.POST.get('id') is None:
        rito = Rito.objects.filter(Q(status=1) & Q(emp_id=request.session['emp_id']))
    else:
        rito = Rito.objects.filter(id=request.POST.get('id'))

    if rito:
        rito.update(
            status=4,
            date=datetime.now())
        return JsonResponse({'data': "success"})
    else:
        return JsonResponse({'error': "Sorry, it seems like you have empty RITO's."})


@login_required
@permission_required('auth.rito')
def print_rito(request, pk):
    rito = Rito.objects.filter(id=pk).first()
    config = PortalConfiguration.objects.filter(key_name='TR INCHARGE').first()

#     url = "https://crg-finance-svr.entdswd.local/gstracking/api/v2/printrequest"
#     body = {'id': rito.tracking_no }
#     headers = {'KEY': 'aee465aff8944cce528d297b601b273f871f65b75d9f3bdface0bfa284953851',
#                'content-type': 'application/json'}

#     r = requests.post(url, data=json.dumps(body), headers=headers, verify=False)

    isok = False
    if rito:
        if rito.emp.id == request.session['emp_id']:
            isok = True

    if isok:
        context = {
            'rito': Ritodetails.objects.filter(rito_id=rito.id) if rito else None,
            'officer_in_charge': config.key_acronym.split(', '),
            'name': rito,
            'date': datetime.now()
        }
        return render(request, 'frontend/pas/rito/print_rito.html', context)
    else:
        raise Http404("You are not authorized to print this request.")


@login_required
@csrf_exempt
@permission_required('auth.rito')
def get_vehicle_request_token(request):
    url = "https://crg-finance-svr.entdswd.local/gstracking/api/v2/printrequest"
    body = {'id': request.POST.get('id') }
    headers = {'KEY': 'aee465aff8944cce528d297b601b273f871f65b75d9f3bdface0bfa284953851',
               'content-type': 'application/json'}

    r = requests.post(url, data=json.dumps(body), headers=headers, verify=False)
    return JsonResponse({'data': r.text.replace('"', '')})


@login_required
@csrf_exempt
@permission_required('auth.rito')
def cancel_travel_request(request):
    if request.method == 'POST':
        Rito.objects.filter(id=request.POST.get('id')).update(status=5)
        return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.rito')
def attachment_update(request, tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    rito = Rito.objects.filter(tracking_no=tracking_no).first()

    if check_merge:
        rito_attachment = RitoAttachment.objects.filter(rito_id=check_merge.first().id)
    else:
        rito_attachment = RitoAttachment.objects.filter(rito_id=rito.id)

    if request.method == "POST":
        file = request.FILES.get('file')
        attachment_type = request.POST.get('attachment_type')
        if check_merge:
            rito_id = check_merge.first().id
        else:
            rito_id = rito.id

        if rito_attachment.count() > 0:
            rito_attachment.update(file=file, type=attachment_type)
        else:
            RitoAttachment.objects.create(rito_id=rito_id, file=file, type=attachment_type)

        return JsonResponse({'data': 'success', 'tracking_no': tracking_no})

    context = {
        'rito': check_merge.first() if check_merge else rito,
        'attachment': rito_attachment.first(),
        'management': True,
        'title': 'to',
        'sub_title': 'rito'
    }
    return render(request, 'frontend/pas/rito/attachment.html', context)


@login_required
@permission_required('auth.rito')
def view_tracking_details(request, pk):
    rito = Rito.objects.filter(id=pk).first()
    context = {
        'tracking': rito
    }
    return render(request, 'frontend/pas/rito/tracking_details.html', context)

