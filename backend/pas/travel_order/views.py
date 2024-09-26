import json
import os
import re
import threading
from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from api.wiserv import send_notification
from backend.forms import TOClaimsForm, TOMotForm
from backend.models import Empprofile, Designation
from backend.views import AjaxableResponseMixin
from frontend.models import Rito, Ritodetails, TravelOrder, Claims, Mot, Ritopeople, PortalConfiguration, RitoAttachment
from frontend.pas.rito.views import interval_rito_date_conflict
from portal.global_variables import any_permission_required
from approve_rito.models import ApprovedRito


def permission_required_any(permissions):
    """
    Decorator to require at least one of the specified permissions.
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if any(request.user.has_perm(permission) for permission in permissions):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse('home'))

        return wrapped_view

    return decorator


@login_required
@permission_required('auth.travel_order')
def filter_tracking_no(request):
    results = list(Rito.objects.filter(Q(status=2) | Q(status=3))
                   .values_list('tracking_no', flat=True).order_by('tracking_no'))

    data = json.dumps(results)
    return HttpResponse(data, 'application/json')


@login_required
@permission_required('auth.travel_order')
def rito_request(request):
    current_year = request.GET.get('current_year', datetime.now().year)

    context = {
        'current_year': current_year,
        'management': True,
        'title': 'to',
        'sub_title': 'rito'
    }
    return render(request, 'backend/pas/travel_order/rito_request.html', context)


@login_required
@permission_required('auth.travel_order')
def admin_travel_total(request, year):
    total_tr_requests_today = ApprovedRito.objects.filter(date__date=date.today(), date__year__icontains=year, status=1).count()
    total_tr_pending = Rito.objects.filter(date__year__icontains=year, status=2).count()
    total_tr_approved = Rito.objects.filter(date__year__icontains=year, status=3).count()
    total_tr_cancelled = Rito.objects.filter(date__year__icontains=year, status=5).count()
    total_tr_pending_for_generation = Rito.objects.filter(Q(approvedrito__status=1) &
                                                          Q(date__year__icontains=year) &
                                                          Q(date_administered=None)).count()

    total_tos_approved_today = TravelOrder.objects.filter(date__date=date.today(), date__year__icontains=year).count()
    total_tos_ongoing = TravelOrder.objects.filter(date__year__icontains=year, status=1).count()
    total_tos_approved = TravelOrder.objects.filter(date__year__icontains=year, status=2).count()
    total_tos_cancelled = TravelOrder.objects.filter(date__year__icontains=year, status=3).count()

    return JsonResponse({
        'total_tr_requests_today': total_tr_requests_today,
        'total_tr_pending': total_tr_pending,
        'total_tr_approved': total_tr_approved,
        'total_tr_cancelled': total_tr_cancelled,
        'total_tr_pending_for_generation': total_tr_pending_for_generation,
        'total_tos_approved_today': total_tos_approved_today,
        'total_tos_ongoing': total_tos_ongoing,
        'total_tos_approved': total_tos_approved,
        'total_tos_cancelled': total_tos_cancelled
    })


@login_required
@permission_required('auth.travel_order')
def merge_travel(request):
    if request.method == "POST":
        tracking_no = request.POST.getlist('tracking_no[]')

        Rito.objects.filter(tracking_no=request.POST.get('merge_in')).update(
            tracking_merge=request.POST.get('merge_in')
        )

        for row in tracking_no:
            Rito.objects.filter(tracking_no=row).update(
                tracking_merge=request.POST.get('merge_in'),
                status=3,
                approved_date=datetime.now()
            )

            check = TravelOrder.objects.filter(rito__tracking_no=row).first()
            
            if check:
                TravelOrder.objects.filter(rito__tracking_no=row).update(
                    status=1,
                    approved_by_id=request.session['emp_id']
                )
            else:
                travel_request = Rito.objects.filter(tracking_no=row).first()
                TravelOrder.objects.create(
                    rito_id=travel_request.id,
                    status=1,
                    approved_by_id=request.session['emp_id']
                )

            people = Ritopeople.objects.filter(detail__rito__tracking_no=row)
            for p in people:
                message = "Good day, {}! Your request for travel to {} on {} - {}, with tracking number {} has been approved. Your travel order is now being processed. - The My PORTAL Team".format(
                    p.name.pi.user.first_name,
                    p.detail.place,
                    p.detail.inclusive_from,
                    p.detail.inclusive_to,
                    p.detail.rito.tracking_no)

                if p.name.pi.mobile_no:
                    t = threading.Thread(target=send_notification,
                                         args=(message, p.name.pi.mobile_no, request.session['emp_id'], p.name.id))
                    t.start()

        return JsonResponse({'data': "success"})


@login_required
@permission_required('auth.travel_order')
def undo_merge_travel_all(request):
    if request.method == "POST":
        tracking_no = request.POST.get('undo_tracking_no')
        rito = Rito.objects.filter(tracking_merge=tracking_no)

        for row in rito:
            check = TravelOrder.objects.filter(rito_id=row.id).first()
            if check:
                TravelOrder.objects.filter(rito_id=row.id).delete()

        rito.update(
           tracking_merge='',
           status=2,
           approved_date=datetime.now()
        )

        return JsonResponse({'data': "success", 'tracking_no': tracking_no})


@login_required
@permission_required('auth.travel_order')
def undo_merge_travel(request, tracking_no):
    if request.GET.get('unmerge') == "yes":
        rito = Rito.objects.filter(tracking_no=tracking_no)
        tracking_merge = rito.first().tracking_merge
        rito.update(tracking_merge='')
        return JsonResponse({'data': "success", 'tracking_no': tracking_merge})
    rito = Rito.objects.filter(tracking_merge=tracking_no)
    context = {
        'rito': rito,
        'tracking_no': tracking_no
    }
    return render(request, 'backend/pas/travel_order/view_merge.html', context)


@login_required
@permission_required_any(['auth.travel_order', 'auth.supervisor'])
def view_rito(request, tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    config = PortalConfiguration.objects.filter(key_name='TR INCHARGE').first()
    context = {
        'rito': Ritodetails.objects.filter(rito_id__in=check_merge.values_list('id') if check_merge else [Rito.objects.filter(tracking_no=tracking_no).first().id]),
        'officer_in_charge': config.key_acronym.split(', '),
        'name': check_merge.first() if check_merge else Rito.objects.filter(tracking_no=tracking_no).first(),
        'user_id': request.session['pi_id']
    }
    return render(request, 'backend/pas/travel_order/view_rito.html', context)


@login_required
def view_rito_details(request, tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    rito = Rito.objects.filter(tracking_no=tracking_no).first()
    context = {
        'ritodetails': Ritodetails.objects.filter(rito_id__in=check_merge.values_list('id') if check_merge else [rito.id]),
        'rito': check_merge.first() if check_merge else rito
    }
    return render(request, 'backend/pas/travel_order/view_rito_details.html', context)


@login_required
def add_rito_details(request, tracking_no):
    if request.method == "POST":
        employee = request.POST.getlist('employee[]')
        employee_list = []
        for row in employee:
            id_number = re.split('\[|\]', row)
            emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
            check_conflict = interval_rito_date_conflict(request.POST.get('from'), request.POST.get('to'), emp['id'])

            if check_conflict:
                employee_list.append({
                    'name': check_conflict.first().name.pi.user.first_name.upper(),
                    'text_date': 'specified dates' if request.POST.get('from') != request.POST.get('to') else 'specified date',
                    'to_number': [row.detail.rito.tracking_no if row.detail.rito.tracking_no else "drafted by {}".format(row.detail.rito.emp.pi.user.get_fullname.upper())
                                      for row in check_conflict],
                    'text_to': 'Travel Orders' if check_conflict.count() > 1 else 'Travel Order'
                })

        if employee_list:
            return JsonResponse({'error': True, 'conflict': employee_list})
        else:
            check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()

            details = Ritodetails(
                rito_id=check_merge.id if check_merge else Rito.objects.filter(tracking_no=tracking_no).first().id,
                place=request.POST.get('places'),
                inclusive_from=request.POST.get('from'),
                inclusive_to=request.POST.get('to'),
                purpose=request.POST.get('purpose'),
                expected_output=request.POST.get('expected_output'),
                claims_id=request.POST.get('claims'),
                mot_id=request.POST.get('mot')
            )

            details.save()

            Ritopeople.objects.create(
                detail_id=details.id,
                name_id=emp['id']
            )

            return JsonResponse({'data': 'success'})

    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    context = {
        'rito': check_merge.first() if check_merge else Rito.objects.filter(tracking_no=tracking_no).first(),
        'claims': Claims.objects.filter(status=1).order_by('name'),
        'mot': Mot.objects.filter(status=1).order_by('name'),
    }
    return render(request, 'backend/pas/travel_order/add_rito_details.html', context)


@login_required
def edit_rito_details(request, pk):
    if request.method == "POST":
        employee = request.POST.getlist('employee[]')
        employee_list = []
        for row in employee:
            id_number = re.split('\[|\]', row)
            emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
            check = Ritopeople.objects.filter(detail__inclusive_from=request.POST.get('from'),
                                              detail__inclusive_to=request.POST.get('to'), name_id=emp['id']).first()
            if not check:
                check_conflict = interval_rito_date_conflict(request.POST.get('from'), request.POST.get('to'), emp['id'])
                if check_conflict:
                    employee_list.append({
                        'name': check_conflict.first().name.pi.user.first_name.upper(),
                        'text_date': 'specified dates' if request.POST.get('from') != request.POST.get(
                            'to') else 'specified date',
                        'to_number': [row.detail.rito.tracking_no for row in check_conflict],
                        'text_to': 'Travel Orders' if check_conflict.count() > 1 else 'Travel Order'
                    })
                else:
                    Ritopeople.objects.create(detail_id=pk, name_id=emp['id'])

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

    rito = Ritodetails.objects.filter(id=pk).first()
    context = {
        'rito': Ritodetails.objects.filter(id=pk).first(),
        'ritopeople': Ritopeople.objects.filter(detail_id=pk),
        'claims': Claims.objects.filter(status=1).order_by('name'),
        'mot': Mot.objects.filter(status=1).order_by('name'),
        'rito_id': rito.rito_id
    }
    return render(request, 'backend/pas/travel_order/edit_rito_details.html', context)


@csrf_exempt
@login_required
@permission_required('auth.travel_order')
def delete_ritopeople(request):
    Ritopeople.objects.filter(detail_id=request.POST.get('detail_id'), name_id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@any_permission_required('auth.supervisor', 'auth.travel_order', 'admin.superadmin')
def approved_rito(request):
    rito = Rito.objects.filter(tracking_no=request.POST.get('id')).first()
    approved_rito_obj = ApprovedRito(
        rito=rito,
        supervisor_id=request.session['emp_id'],
        date=datetime.now()
    )
    approved_rito_obj.save()

    check_merge = Rito.objects.filter(tracking_merge=request.POST.get('id'))
    if not check_merge:
        check = TravelOrder.objects.filter(rito__tracking_no=request.POST.get('id')).first()
        if check:
            TravelOrder.objects.filter(rito__tracking_no=request.POST.get('id')).update(
                status=1)
        else:
            to = TravelOrder(
                rito_id=rito.id,
                status=1,
                approved_by_id=request.session['emp_id'])
            to.save()

    people = Ritopeople.objects.filter(detail__rito__tracking_no=request.POST.get('id'))
    checker = []

    for row in people:
        if row.name.pi.mobile_no:
            message = "Good day, {}! Your request for travel to {} on {} - {}, with tracking number {} has been approved. Your travel order is now being processed. - The My PORTAL Team".format(
                row.name.pi.user.first_name.title(),
                row.detail.place,
                row.detail.inclusive_from,
                row.detail.inclusive_to,
                row.detail.rito.tracking_no)

            if "{}-{}".format(row.name.pi.mobile_no, row.detail.place) not in checker:
                t = threading.Thread(target=send_notification,
                                     args=(message, row.name.pi.mobile_no, request.session['emp_id'], row.name.id))
                t.start()

    # message = "Good day, Sir Greg! You have a pending Travel Order to approve, with tracking number {}. - The My PORTAL Team".format(
    #     rito.tracking_no,)
    # sms_thread = threading.Thread(target=send_sms_notification,
    #                      args=(message, '09563888870', request.session['emp_id']))
    # sms_thread.start()

    Rito.objects.filter(tracking_no=request.POST.get('id')).update(status=3, approved_date=datetime.now())
    return JsonResponse({'tracking_no': request.POST.get('id'), 'data': 'success'})


@login_required
@permission_required_any(['auth.travel_order', 'auth.supervisor'])
def generate_to(request, tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    if check_merge:
        rito = check_merge.first()
    else:
        rito = Rito.objects.filter(tracking_no=tracking_no).first()
    isok = False
    if rito:
        isok = True

    if isok:
        context = {
            'rito': Ritodetails.objects.filter(rito_id__in=check_merge.values_list('id') if check_merge else [rito.id]) if rito else None,
            'attachment': RitoAttachment.objects.filter(rito_id=rito.id).first(),
            'name': rito,
            'pk': rito,
            'date': datetime.now(),
            'year': datetime.now().year,
            'designation': Designation.objects.all(),
            'tracking_no': tracking_no
        }
        return render(request, 'backend/pas/travel_order/generate_to.html', context)
    else:
        raise Http404("You are not authorized to print this request.")


@csrf_exempt
@permission_required('auth.travel_order')
def update_rito(request):
    if request.method == "POST":
        mot = request.POST.get('mot')
        claims = request.POST.get('claims')

        if mot == "NaN":
            Ritodetails.objects.filter(id=request.POST.get('id')).update(
                claims=claims)
        elif claims == "NaN":
            Ritodetails.objects.filter(id=request.POST.get('id')).update(
                mot=mot)
        else:
            Ritodetails.objects.filter(id=request.POST.get('id')).update(
                mot=mot,
                claims=claims)
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def delete_travel_request(request):
    Ritopeople.objects.filter(detail_id=request.POST.get('detail_id')).delete()
    Ritodetails.objects.filter(id=request.POST.get('detail_id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def delete_backend_rito(request, tracking_no):
    Rito.objects.filter(tracking_no=tracking_no).delete()
    return redirect('rito-request')


@csrf_exempt
@login_required
@permission_required('auth.travel_order')
def approved_to(request):
    tracking_no = request.POST.get('id')

    rito = Rito.objects.filter(tracking_no=tracking_no).first()
    if not rito:
        return JsonResponse({'error': 'Rito not found'}, status=404)

    # Function to update TravelOrder
    def update_travel_order(tracking_no, rito_id):
        to = TravelOrder.objects.filter(rito__tracking_merge=tracking_no) if check_merge else TravelOrder.objects.filter(rito__tracking_no=tracking_no)

        if to.exists():
            to.update(
                status=2,
                approved_by_id=request.session['emp_id']
            )
        else:
            TravelOrder.objects.create(
                rito_id=rito_id,
                status=2,
                approved_by_id=request.session['emp_id']
            )

    check_merge = Rito.objects.filter(tracking_merge=tracking_no).exists()
    rito.status = 3
    rito.save()

    update_travel_order(tracking_no, rito.id)

    ApprovedRito.objects.filter(rito_id=rito.id).update(status=0)
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@permission_required('auth.travel_order')
def unapproved_to(request):
    tracking_no = request.POST.get('id')
    check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()
    if check_merge:
        Rito.objects.filter(tracking_merge=tracking_no).update(
            status=2
        )

        TravelOrder.objects.filter(rito__tracking_merge=tracking_no).update(
            status=1,
            date=datetime.now(),
            approved_by_id=request.session['emp_id']
        )
    else:
        Rito.objects.filter(tracking_no=tracking_no).update(
            status=2
        )

        TravelOrder.objects.filter(rito__tracking_no=tracking_no).update(
            status=1,
            date=datetime.now(),
            approved_by_id=request.session['emp_id']
        )

    rito = Rito.objects.filter(tracking_no=tracking_no).first()

    ApprovedRito.objects.filter(rito=rito).update(
        status=1,
        date=datetime.now()
    )
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.travel_order')
def attachment_to_update(request, tracking_no):
    if request.method == "POST":
        check_merge = Rito.objects.filter(tracking_merge=tracking_no)
        myfile = request.FILES.get('file')
        fs = FileSystemStorage("/opt/apps/portal/media/attachment/")
        filename = fs.save("Merge_In_{}.pdf".format(tracking_no) if check_merge else "{}.pdf".format(tracking_no), myfile)

        if check_merge:
            to = TravelOrder.objects.filter(rito__tracking_merge=tracking_no).first()
            if to.attachment:
                if os.path.isfile('/opt/apps/portal/media/attachment/media/' + str(to.attachment)):
                    os.remove('/opt/apps/portal/media/attachment/media/' + str(to.attachment))

            for row in check_merge:
                TravelOrder.objects.filter(rito_id=row.id).update(
                    attachment='attachment/{}'.format(filename),
                    date_uploaded=datetime.now()
                )

            people = Ritopeople.objects.filter(detail__rito__tracking_merge=tracking_no)

            list_employee = []
            for row in people:
                if row not in list_employee:
                    message = "Good day, {}! Your approved/signed travel order {} has been transmitted to PAS (Date of Transmission: {}) and is now ready for download. - The My PORTAL Team".format(
                        row.name.pi.user.first_name,
                        row.detail.rito.tracking_no,
                        datetime.now())

                    if row.name.pi.mobile_no:
                        t = threading.Thread(target=send_notification,
                                             args=(
                                             message, row.name.pi.mobile_no, request.session['emp_id'], row.name.id))
                        t.start()
                        list_employee.append(row.name.pi.mobile_no)
        else:
            to = TravelOrder.objects.filter(rito__tracking_no=tracking_no).first()

            if to.attachment:
                if os.path.isfile('/opt/apps/portal/media/attachment/media/' + str(to.attachment)):
                    os.remove('/opt/apps/portal/media/attachment/media/' + str(to.attachment))

            rito = Rito.objects.filter(tracking_no=tracking_no).first()
            TravelOrder.objects.filter(rito_id=rito.id).update(
                attachment='attachment/{}'.format(filename),
                date_uploaded=datetime.now()
            )

            people = Ritopeople.objects.filter(detail__rito__tracking_no=tracking_no)
            list_employee = []
            for row in people:
                if row.name.pi.mobile_no not in list_employee:
                    message = "Good day, {}! Your travel order {} has been approved and is now ready for download. - The My PORTAL Team".format(
                        row.name.pi.user.first_name,
                        row.detail.rito.tracking_no)

                    if row.name.pi.mobile_no:
                        t = threading.Thread(target=send_notification,
                                             args=(message, row.name.pi.mobile_no, request.session['emp_id'], row.name.id))
                        t.start()
                        list_employee.append(row.name.pi.mobile_no)

        return JsonResponse({'data': 'success', 'tracking_no': tracking_no})

    check_merge = Rito.objects.filter(tracking_merge=tracking_no)

    context = {
        'rito': check_merge.first() if check_merge else Rito.objects.filter(tracking_no=tracking_no).first(),
        'management': True,
        'title': 'to',
        'sub_title': 'rito'
    }
    return render(request, 'backend/pas/travel_order/attachment_to.html', context)


@login_required
@permission_required('auth.travel_order')
def to_claims(request):
    form = TOClaimsForm()
    if request.method == "POST":
        form = TOClaimsForm(request.POST)
        if form.is_valid():
            claims = form.save(commit=False)
            claims.upload_by_id = request.user.id
            messages.success(request,
                             'The travel order claims {} was added successfully.'.format(form.cleaned_data['name']))
            claims.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'claims': Paginator(Claims.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'travel_order',
        'sub_sub_title': 'to_claims'
    }
    return render(request, 'backend/pas/travel_order/to_claims.html', context)


class TOClaimsUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView, PermissionRequiredMixin):
    login_url = 'backend-login'
    template_name = 'backend/pas/travel_order/to_claims_update.html'
    model = Claims
    form_class = TOClaimsForm
    success_url = reverse_lazy('to_claims')
    permission_required = 'auth.travel_order'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('auth.travel_order')
def to_mot(request):
    form = TOMotForm()
    if request.method == "POST":
        form = TOMotForm(request.POST)
        if form.is_valid():
            mot = form.save(commit=False)
            mot.upload_by_id = request.user.id
            messages.success(request, 'The travel order means of transportation {} was added successfully.'.format(
                form.cleaned_data['name']))
            mot.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'mot': Paginator(Mot.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'travel_order',
        'sub_sub_title': 'to_mot'
    }
    return render(request, 'backend/pas/travel_order/to_mot.html', context)


class TOMotUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView, PermissionRequiredMixin):
    login_url = 'backend-login'
    template_name = 'backend/pas/travel_order/to_mot_update.html'
    model = Mot
    form_class = TOMotForm
    success_url = reverse_lazy('to_mot')
    permission_required = 'auth.travel_order'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def cancel_travel_order(request):
    if request.method == 'POST':
        check_merge = Rito.objects.filter(tracking_merge=request.POST.get('id'))

        if check_merge:
            for row in check_merge:
                TravelOrder.objects.filter(rito_id=row.id).update(status=3)
                Rito.objects.filter(id=row.id).update(status=5)
            return JsonResponse({'data': 'success', 'tracking_no': check_merge.first().tracking_merge})
        else:
            rito = Rito.objects.filter(tracking_no=request.POST.get('id')).first()
            TravelOrder.objects.filter(rito_id=rito.id).update(status=3)
            Rito.objects.filter(id=rito.id).update(status=5)
            return JsonResponse({'data': 'success', 'tracking_no': rito.tracking_no})


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def uncancel_travel_order(request):
    if request.method == 'POST':
        check_merge = Rito.objects.filter(tracking_merge=request.POST.get('id'))
        if check_merge:
            for row in check_merge:
                TravelOrder.objects.filter(rito_id=row.id).update(status=1)
                Rito.objects.filter(id=row.id).update(status=2, tracking_merge=None)
            return JsonResponse({'data': 'success', 'tracking_no': check_merge.first().tracking_merge})
        else:
            rito = Rito.objects.filter(tracking_no=request.POST.get('id')).first()
            TravelOrder.objects.filter(rito_id=rito.id).update(status=1)
            Rito.objects.filter(id=rito.id).update(status=2)
            return JsonResponse({'data': 'success', 'tracking_no': rito.tracking_no})


@login_required
@permission_required('auth.travel_order')
def travel_remark(request, tracking_no):
    if request.method == "POST":
        check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()

        if check_merge:
            Rito.objects.filter(tracking_merge=tracking_no).update(remarks=request.POST.get('pending_remarks'))
        else:
            Rito.objects.filter(tracking_no=tracking_no).update(remarks=request.POST.get('pending_remarks'))

        return JsonResponse({'data': 'success'})

    check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()

    context = {
        'rito': Rito.objects.filter(tracking_merge=check_merge.tracking_merge).first() if check_merge else Rito.objects.filter(tracking_no=tracking_no).first()
    }
    return render(request, 'backend/pas/travel_order/travel_remark.html', context)


@login_required
@permission_required('auth.travel_order')
def travel_order_report(request):
    if request.method == "POST":
        rito = Ritodetails.objects.filter((Q(place__icontains=request.POST.get('keyword')) | Q(purpose__icontains=request.POST.get('keyword'))) &
                Q(inclusive_from__gte=request.POST.get('inclusive_from')) &
                Q(inclusive_to__lte=request.POST.get('inclusive_to')))
        context = {
            'rito': rito,
            'keyword': request.POST.get('keyword'),
            'inclusive_from': request.POST.get('inclusive_from'),
            'inclusive_to': request.POST.get('inclusive_to'),
            'title': 'to',
            'management': True,
            'sub_title': 'travel_report'
        }
        return render(request, 'backend/pas/travel_order/travel_order_report.html', context)

    context = {
        'title': 'to',
        'management': True,
        'sub_title': 'travel_report'
    }
    return render(request, 'backend/pas/travel_order/travel_order_report.html', context)


@login_required
@permission_required('auth.travel_order')
def travel_order_summary(request):
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    elif request.method == "GET":
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
    else:
        return HttpResponseBadRequest()

    context = {
        'to': Rito.objects.filter(date__date__range=[start_date, end_date]).order_by('-date'),
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'backend/pas/travel_order/travel_summary.html', context)


@login_required
@permission_required('auth.travel_order')
def generate_travel_order(request):
    if request.method == "POST":
        context = {
            'rito': Ritodetails.objects.filter((Q(place__icontains=request.POST.get('generate_keyword')) | Q(purpose__icontains=request.POST.get('generate_keyword'))) &
                                   Q(inclusive_from__gte=request.POST.get('generate_inclusive_from')) &
                                   Q(inclusive_to__lte=request.POST.get('generate_inclusive_to'))),
            'keyword': request.POST.get('generate_keyword'),
            'inclusive_from': request.POST.get('generate_inclusive_from'),
            'inclusive_to': request.POST.get('generate_inclusive_to'),
            'user': Empprofile.objects.filter(id=request.session['emp_id']).first()

        }
        return render(request, 'backend/pas/travel_order/generate_travel_report.html', context)


class AttachmentTOUpdate(object):
    pass


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def update_travel_remarks(request, tracking_no):
    if request.method == "POST":
        check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()

        remarks = "Approved by: {}, {}; Subject: {}".format(request.POST.get('designation_name'), request.POST.get('designation'), request.POST.get('subject'))
        if check_merge:
            Rito.objects.filter(tracking_merge=tracking_no).update(remarks=remarks)
        else:
            Rito.objects.filter(tracking_no=tracking_no).update(remarks=remarks)

        return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.travel_order')
def view_tr_tracking(request, pk):
    rito = Rito.objects.filter(id=pk).first()
    if request.method == "POST":
        Rito.objects.filter(id=pk).update(
            tracking_no=request.POST.get('tracking_no'),
            date_received=request.POST.get('date_received') if request.POST.get('date_received') else None,
            date_administered=request.POST.get('date_administered') if request.POST.get('date_administered') else None,
            date_forwarded=request.POST.get('date_forwarded') if request.POST.get('date_forwarded') else None,
            date_returned=request.POST.get('date_returned') if request.POST.get('date_returned') else None,
            remarks=request.POST.get('remarks')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the tracking.'})

    check = ApprovedRito.objects.filter(rito_id=rito.id)
    date_approved_dc = None

    if check:
        if check.first().status == 1:
            date_approved_dc = check.first().date
        else:
            date_approved_dc = None
    else:
        date_approved_dc = None

    print(f"CHECK DATE APPROVED: {date_approved_dc}")

    context = {
        'tracking': rito,
        'approved_rito': date_approved_dc
    }
    return render(request, 'backend/pas/travel_order/tracking_details.html', context)


@login_required
@csrf_exempt
@permission_required('auth.travel_order')
def mark_as_received_tr(request):
    if request.method == "POST":
        Rito.objects.filter(tracking_no=request.POST.get('tracking_no')).update(
            date_received=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully marked as received the travel request.'})
