import json
import re
import threading
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Func, F, Value, CharField
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_notification
from backend.calendar.models import CalendarType, CalendarEvent, CalendarEventApproval, CalendarPermission, \
    CalendarShared
from backend.forms import CalendarTypeFormPrivate
from backend.models import Empprofile
from frontend.templatetags.tags import transform_to_duration_date, gamify


def get_approval_id(request, event_id):
    ev_approval = CalendarEventApproval.objects.filter(event_id=event_id).first()
    return JsonResponse({'data': ev_approval.event_id if ev_approval else 0})


def get_has_permission_for_calendar(request, type_id):
    cal_permission = CalendarPermission.objects.filter(type_id=type_id, emp_id=request.user.id)
    return JsonResponse({'data': cal_permission.count()})


@login_required
def events(request, status=1):
    form = CalendarTypeFormPrivate
    if request.method == "POST":
        return JsonResponse({'data': [m for m in CalendarEvent.objects.filter(Q(type_id=request.POST.get('type')),
                                                                              Q(status=status),
                                                                              (Q(start_datetime__gte=datetime.datetime
                                                                                  .fromtimestamp(
                                                                                  float(request.POST.get(
                                                                                      'start')) - 28800)) |
                                                                               Q(end_datetime__lt=datetime.datetime
                                                                                   .fromtimestamp(
                                                                                   float(
                                                                                       request.POST.get('end')) - 28800)
                                                                               ))).values()]}) if status == 1 else \
            (JsonResponse({'data': [m for m in CalendarEvent.objects.filter(Q(type_id=request.POST.get('type')),
                                                                            Q(status=status),
                                                                            Q(upload_by_id=request.user.id),
                                                                            (Q(start_datetime__gte=datetime.datetime
                                                                                .fromtimestamp(
                                                                                float(request.POST.get(
                                                                                    'start')) - 28800)) |
                                                                             Q(end_datetime__lt=datetime.datetime
                                                                                 .fromtimestamp(
                                                                                 float(
                                                                                     request.POST.get('end')) - 28800)
                                                                             ))).values()]}) if status == 0 else
             JsonResponse({'data': [m for m in CalendarEvent.objects.filter(Q(type_id=request.POST.get('type')),
                                                                            Q(status=0),
                                                                            ~Q(upload_by_id=request.user.id),
                                                                            (Q(start_datetime__gte=datetime.datetime
                                                                                .fromtimestamp(
                                                                                float(request.POST.get(
                                                                                    'start')) - 28800)) |
                                                                             Q(end_datetime__lt=datetime.datetime
                                                                                 .fromtimestamp(
                                                                                 float(
                                                                                     request.POST.get('end')) - 28800)
                                                                             ))).values()]}))

    public_calendars = CalendarType.objects.filter(scope=0, status=True).order_by('id')
    private_calendars = CalendarType.objects.filter(scope=1, status=True, upload_by=request.user.id).order_by('id')
    shared = CalendarShared.objects.filter(type__scope=1, type__status=True, emp_id=request.user.id) \
        .values_list('type__id', flat=True)
    shared_calendars = CalendarType.objects.filter(id__in=shared).order_by('id')
    public_private = public_calendars.union(private_calendars, shared_calendars)

    context = {
        'form': form,
        'tab_title': 'Events',
        'title': 'events',
        'public_calendars': public_calendars,
        'private_calendars': private_calendars,
        'shared_calendars': shared_calendars,
        'public_private': public_private,
        'user_id': request.user.id
    }
    return render(request, 'frontend/events/events.html', context)


@login_required
def events_v2(request):
    form = CalendarTypeFormPrivate

    public_calendars = CalendarType.objects.filter(scope=0, status=True).order_by('id')
    private_calendars = CalendarType.objects.filter(scope=1, status=True, upload_by=request.user.id).order_by('id')
    shared = CalendarShared.objects.filter(type__scope=1, type__status=True, emp_id=request.user.id) \
        .values_list('type__id', flat=True)
    shared_calendars = CalendarType.objects.filter(id__in=shared).order_by('id')
    public_private = public_calendars.union(private_calendars, shared_calendars)

    context = {
        'tab_title': 'Events',
        'title': 'events',
        'form': form,
        'public_calendars': public_calendars,
        'private_calendars': private_calendars,
        'shared_calendars': shared_calendars,
        'public_private': public_private
    }
    return render(request, 'frontend/events/events_v2.html', context)


@login_required
def get_all_events(request, status):
    if status == 1:
        event = CalendarEvent.objects.annotate(
            start=Func(
                F('start_datetime'),
                Value('%Y-%m-%d %h:%i:%s'),
                function='DATE_FORMAT',
                output_field=CharField()
            ),
            end=Func(
                F('end_datetime_real'),
                Value('%Y-%m-%d %h:%i:%s'),
                function='DATE_FORMAT',
                output_field=CharField()
            ),
            color=F('type__color'),
        ).values('id', 'title', 'start', 'end', 'description', 'color', 'type_id', 'upload_by_id').filter(
            status=status
        )
    else:
        event = CalendarEvent.objects.annotate(
            start=Func(
                F('start_datetime'),
                Value('%Y-%m-%d %h:%i:%s'),
                function='DATE_FORMAT',
                output_field=CharField()
            ),
            end=Func(
                F('end_datetime_real'),
                Value('%Y-%m-%d %h:%i:%s'),
                function='DATE_FORMAT',
                output_field=CharField()
            ),
            colors=F('type__color')
        ).values('id', 'title', 'start', 'end', 'description', 'type_id', 'colors', 'upload_by_id').filter(
            status=status
        )

    return HttpResponse(json.dumps(list(event)), content_type='application/json')


@login_required
def add_private_calendar(request):
    if request.method == "POST":
        form = CalendarTypeFormPrivate(request.POST)
        if form.is_valid():
            with transaction.atomic():
                calendartype = form.save(commit=False)
                calendartype.scope = True
                calendartype.status = True
                calendartype.upload_by_id = request.user.id
                calendartype.save()

                CalendarPermission.objects.create(
                    type_id=calendartype.id,
                    emp_id=request.user.id
                )
                return JsonResponse({'data': 'success'})
        return JsonResponse({'data': 'error', 'errors': form.errors})
    return JsonResponse({'data': 'error', 'errors': 'You are not authorized to access this content. Please contact '
                                                    'your administrator.'})


@login_required
def update_private_calendar(request):
    if request.method == "POST":
        try:
            pk = request.POST.get('id_update')
            calendar = CalendarType.objects.filter(id=pk, upload_by_id=request.user.id).first()
            if calendar:
                with transaction.atomic():
                    calendar.name = request.POST.get('name_update')
                    calendar.color = request.POST.get('color_update')
                    calendar.save()
                    return JsonResponse({'data': 'success'})
            return JsonResponse(
                {'data': 'error', 'errors': 'You are not authorized to access this content. Please contact '
                                            'your administrator.'})
        except Exception as e:
            return JsonResponse({'data': 'error', 'errors': e})
    return JsonResponse({'data': 'error', 'errors': 'You are not authorized to access this content. Please contact '
                                                    'your administrator.'})


@login_required
@csrf_exempt
def delete_event(request):
    if request.method == "POST":
        with transaction.atomic():
            CalendarEventApproval.objects.filter(event_id=request.POST.get('id')).delete()
            CalendarEvent.objects.filter(id=request.POST.get('id')).delete()
            return JsonResponse({'data': 'success'})
    return JsonResponse({'data': 'error', 'errors': 'Unauthorized transaction.'})


@login_required
def view_event(request, id):
    public_calendars = CalendarType.objects.filter(scope=0, status=True).order_by('id')
    private_calendars = CalendarType.objects.filter(scope=1, status=True, upload_by=request.user.id).order_by('id')
    public_private = public_calendars.union(private_calendars)

    data = CalendarEvent.objects.filter(id=id).first()
    context = {
        'data': data,
        'user_id': request.user.id,
        'public_calendars': public_calendars,
        'private_calendars': private_calendars,
        'public_private': public_private,
        'is_approver': True if request.user.id in data.get_users_for_calendar_type else False,
        'is_owner': True if request.user.id == data.upload_by_id else False
    }
    return render(request, 'frontend/events/view_event.html', context)


def interval_date_conflict(start_date, end_date, type_id):
    check = CalendarEvent.objects.filter(
        Q(
            Q(
                Q(end_datetime_real__gte=start_date),
                Q(end_datetime_real__lte=end_date),
                Q(start_datetime__lte=start_date),
                Q(start_datetime__lte=end_date)
            ) |
            Q(
                Q(end_datetime_real__gte=start_date),
                Q(end_datetime_real__gte=end_date),
                Q(start_datetime__lte=start_date),
                Q(start_datetime__lte=end_date)
            ) |
            Q(
                Q(end_datetime_real__gte=start_date),
                Q(end_datetime_real__gte=end_date),
                Q(start_datetime__gte=start_date),
                Q(start_datetime__lte=end_date)
            ) |
            Q(
                Q(end_datetime_real__gte=start_date),
                Q(end_datetime_real__lte=end_date),
                Q(start_datetime__gte=start_date),
                Q(start_datetime__lte=end_date)
            )
        ) & Q(type_id=type_id) & Q(type__scope=0))

    approval = CalendarEventApproval.objects.filter(Q(event_id__in=[row.id for row in check]) &
                                                    ~Q(Q(status_from=0) & Q(status_to=0)))
    return approval


@login_required
def add_event(request):
    if request.method == "POST":
        try:
            start_datetime = "{} {}".format(request.POST.get('date'), request.POST.get('start_time'))
            end_datetime = "{} {}".format(request.POST.get('date'), request.POST.get('end_time'))

            if start_datetime < end_datetime:
                check = interval_date_conflict(
                        start_datetime, end_datetime,
                        request.POST.get('type_id')
                ) # if not request.user.is_superuser else None

                if not check:
                    end_date = datetime.strptime("{} {}".format(request.POST.get('date'), request.POST.get('end_time')),
                                                 '%Y-%m-%d %H:%M') + timedelta(days=1)
                    cal_event = CalendarEvent(
                        start_datetime=start_datetime,
                        end_datetime=end_date,
                        end_datetime_real=end_datetime,
                        title=request.POST.get('title'),
                        description=request.POST.get('description'),
                        status=0 if CalendarType.objects.filter(id=request.POST.get('type_id'), scope=0,
                                                                status=True) else 1,
                        type_id=request.POST.get('type_id'),
                        upload_by_id=request.user.id,
                        remarks=request.POST.get('remarks')
                    )

                    cal_event.save()

                    # Save points for booking of event in calendar
                    gamify(9, request.session['emp_id'])

                    if cal_event.type.scope == 0:
                        calendar_admins = CalendarPermission.objects.filter(type_id=cal_event.type.id)
                        for admin in calendar_admins:
                            if admin.emp.mobile_no:
                                admin_message = "An event entitled {} on {} is being " \
                                                "requested for {} by {}, and is pending for review. " \
                                                "You may accept or decline it as a calendar administrator. " \
                                                "- The My PORTAL Team" \
                                    .format(cal_event.title,
                                            '{} {} - {}'.format(
                                                request.POST.get('date'), request.POST.get('start_time'),
                                                request.POST.get('end_time')
                                            ), cal_event.type.name,
                                            cal_event.upload_by.get_fullname)
                                t = threading.Thread(target=send_notification,
                                                     args=(
                                                         admin_message, admin.emp.mobile_no, request.session['emp_id'],
                                                         admin.emp.employee_id))
                                t.start()
                    return JsonResponse({'data': 'success'})
                else:
                    return JsonResponse({'data': 'error', 'errors': 'Specified schedule has already been booked.'
                                                                ' Please select another schedule. Thank you.'})
            return JsonResponse({'data': 'error', 'errors': 'Start date must always be less than the end date.'})
        except Exception as e:
            return JsonResponse({'data': 'error', 'errors': 'Adding of new event failed with error {}.'.format(e)})
    return JsonResponse({'data': 'error', 'errors': 'Unauthorized transaction.'})


@login_required
def save_event_approval(request):
    if request.method == "POST":
        with transaction.atomic():
            cal_event = CalendarEvent.objects.filter(id=request.POST.get('event-id-remarks')).first()
            cal_event.status = request.POST.get('status-remarks')
            cal_event.save()
            CalendarEventApproval.objects.create(
                remarks=request.POST.get('approver-remarks'),
                status_from=0,
                status_to=request.POST.get('status-remarks'),
                event_id=request.POST.get('event-id-remarks'),
                emp_id=request.user.id
            )

            message = "Good day, {}! Your event request entitled {} has been {} by the administrator. - The Caraga " \
                      "PORTAL Team".format(
                cal_event.upload_by.first_name,
                cal_event.title, "approved" if request.POST.get('status-remarks') == 1 or
                                               request.POST.get('status-remarks') == "1" else "declined")
            if cal_event.upload_by.mobile_no:
                t = threading.Thread(target=send_notification,
                                     args=(message, cal_event.upload_by.mobile_no, request.session['emp_id'],
                                  cal_event.upload_by.employee_id))
                t.start()

            return JsonResponse({'data': 'success'})
    return JsonResponse({'data': 'error', 'errors': 'Unauthorized transaction.'})


@login_required
def revert_event_approval(request):
    if request.method == "POST":
        with transaction.atomic():
            CalendarEventApproval.objects.filter(event_id=request.POST.get('id')).delete()
            cal_event = CalendarEvent.objects.filter(id=request.POST.get('id')).first()
            cal_event.status = False
            cal_event.save()
            return JsonResponse({'data': 'success'})
    return JsonResponse({'data': 'error', 'errors': 'Unauthorized transaction.'})


@login_required
def update_event(request):
    if request.method == "POST":
        with transaction.atomic():
            start_datetime = "{} {}".format(request.POST.get('date'), request.POST.get('start_time'))
            end_datetime = "{} {}".format(request.POST.get('date'), request.POST.get('end_time'))

            if start_datetime < end_datetime:
                end_date = datetime.strptime("{} {}".format(request.POST.get('date'), request.POST.get('end_time')),
                                             '%Y-%m-%d %H:%M') + timedelta(days=1)
                calevent = CalendarEvent.objects.filter(id=request.POST.get('id')).first()
                calevent.start_datetime = start_datetime
                calevent.end_datetime = end_date
                calevent.end_datetime_real = end_datetime
                calevent.title = request.POST.get('title')
                calevent.description = request.POST.get('description')
                calevent.status = 0 if CalendarType.objects.filter(id=request.POST.get('type_id'), scope=0,
                                                                   status=True) and calevent.status == 0 else 1
                calevent.type_id = request.POST.get('type_id')
                calevent.remarks = request.POST.get('remarks')
                calevent.save()
                return JsonResponse({'data': 'success'})
            return JsonResponse({'data': 'error', 'errors': 'Start date must always be less than the end date.'})
    return JsonResponse({'data': 'error', 'errors': 'Unauthorized transaction.'})


@login_required
def calendar_sharing(request, type_id):
    context = {
        'data': CalendarShared.objects.filter(type_id=type_id),
        'type_id': type_id,
        'user_id': request.user.id,
    }
    return render(request, 'frontend/events/shared.html', context)


@login_required
def share_calendar(request):
    if request.method == "POST":
        user_id = re.split('\[|\]', request.POST.get('emp'))
        emp = Empprofile.objects.filter(id_number=user_id[1]).first()
        check = CalendarShared.objects.filter(emp_id=emp.id, type_id=request.POST.get('type_id'))

        if check:
            pass
        else:
            x = CalendarShared.objects.create(
                type_id=request.POST.get('type_id'),
                emp_id=emp.pi.user.id
            )

            message = "Good day, {}! Calendar {} has been shared to you by {}. - The My PORTAL Team".format(
                x.emp.first_name, x.type.name, x.type.upload_by.get_fullname)
            if x.emp.mobile_no:
                send_notification(message, x.emp.mobile_no, request.session['emp_id'], x.emp.employee_id)

        return JsonResponse({'data': 'success', 'type_id': request.POST.get('type_id')})

    context = {
        'data': CalendarShared.objects.filter(type_id=id),
        'type_id': id,
    }
    return render(request, 'frontend/events/shared.html', context)


@login_required
@csrf_exempt
def unshare_calendar(request, id):
    if request.method == "POST":
        x = CalendarShared.objects.filter(id=id).first()
        type_id = x.type_id
        CalendarShared.objects.filter(id=id).delete()
        return JsonResponse({'data': 'success', 'type_id': type_id})
    return JsonResponse({'data': 'error'})
