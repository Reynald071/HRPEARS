import asyncio
import queue
import re
import threading
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from backend.models import Empprofile, Division, Designation
from frontend.models import PasAccomplishmentOutputs
from frontend.templatetags.tags import get_signatory, gamify, check_if_weekend


@login_required
@csrf_exempt
def accomplishment(request):
    if request.method == "POST":
        checked = request.POST.getlist('checked[]')
        op_id = request.POST.getlist('op_id[]')
        date_per = request.POST.getlist('date_per[]')
        place_vis = request.POST.getlist('place_vis[]')
        output = request.POST.getlist('output[]')
        data = [{'checked': t, 'op_id': i, 'date_per': d, 'place_vis': p, 'output': o}
                for t, i, d, p, o in zip(checked, op_id, date_per, place_vis, output)]

        to_create = []
        to_update = []
        to_delete = []
        for row in data:
            if row['op_id'] == '':
                if row['checked'] == 'checked':
                    to_create.append(PasAccomplishmentOutputs(
                        emp_id=request.session['emp_id'],
                        date_period=row['date_per'],
                        place_visited=row['place_vis'],
                        output=row['output'],
                        remarks=''))
            else:
                if row['checked'] == 'checked':
                    to_update.append(PasAccomplishmentOutputs(
                        id=row['op_id'],
                        place_visited=row['place_vis'],
                        output=row['output'],
                        remarks=''))
                elif row['checked'] == 'skip':
                    pass
                else:
                    to_delete.append(row['op_id'])

        # Perform database operations
        if to_create:
            PasAccomplishmentOutputs.objects.bulk_create(to_create)
        if to_update:
            PasAccomplishmentOutputs.objects.bulk_update(to_update, ['place_visited', 'output', 'remarks'])
        if to_delete:
            PasAccomplishmentOutputs.objects.filter(id__in=to_delete).delete()

        return JsonResponse({'data': 'success'})

    context = {
        'data': Empprofile.objects.filter(pi_id=request.session['pi_id']).first(),
        'start_date': 's',
        'end_date': 'e',
    }
    return render(request, 'frontend/pas/accomplishment/accomplishment.html', context)


@login_required
def set_signature_accomplishment(request):
    first_signature = re.split('\[|\]', request.POST.get('approved_by'))
    first_signature_emp = Empprofile.objects.filter(id_number=first_signature[1]).first()

    second_signature = re.split('\[|\]', request.POST.get('noted_by'))
    second_signature_emp = Empprofile.objects.filter(id_number=second_signature[1]).first()

    first_division = Division.objects.filter(Q(div_chief_id=first_signature_emp.id))

    fs_designation = Designation.objects.filter(emp_id=first_signature_emp.id).first()
    ss_designation = Designation.objects.filter(emp_id=second_signature_emp.id).first()

    first_pos = ''
    second_pos = ''

    if ss_designation or fs_designation:
        first_pos = '{}'.format(fs_designation.name)
        second_pos = '{}'.format(ss_designation.name)
    else:
        if first_division:
            first_pos = 'Chief, {}'.format(first_signature_emp.section.div.div_name)
            check = Division.objects.filter(Q(div_chief_id=second_signature_emp.id))
            if check:
                second_pos = 'Chief, {}'.format(second_signature_emp.section.div.div_name)
            else:
                second_pos = 'Head, {}'.format(second_signature_emp.section.sec_name)
        else:
            first_pos = 'Head, {}'.format(first_signature_emp.section.sec_name)

            check = Division.objects.filter(Q(div_chief_id=second_signature_emp.id))
            if check:
                second_pos = 'Chief, {}'.format(second_signature_emp.section.div.div_name)
            else:
                second_pos = 'Head, {}'.format(second_signature_emp.section.sec_name)

    return JsonResponse({
        'first_signature': '{}, {}'.format(first_signature_emp.pi.user.get_fullname.upper(), first_signature_emp.position.acronym),
        'first_signature_pos': first_pos,
        'second_signature': '{}, {}'.format(second_signature_emp.pi.user.get_fullname.upper(),
                                           second_signature_emp.position.acronym),
        'second_signature_pos': second_pos
    })


@login_required()
def print_accomplishment(request, sd, ed):
    sdd = datetime.strptime(sd, '%Y-%m-%d')
    edd = datetime.strptime(ed, '%Y-%m-%d')

    emp = Empprofile.objects.get(id=request.session['emp_id'])

    # Save points for printing accomplishment
    gamify(18, request.session['emp_id'])

    delta = edd - sdd

    alldays = list()
    for i in range(delta.days + 1):
        alldays.append(sdd + timedelta(days=i))

    context = {
        'signatory': get_signatory(request.session['emp_id'])['signatory'],
        'signatory_pos': get_signatory(request.session['emp_id'])['signatory_pos'],
        'signatory_sl': get_signatory(request.session['emp_id'])['signatory_sl'],
        'signatory_sl_pos': get_signatory(request.session['emp_id'])['signatory_sl_pos'],
        'user': emp,
        'start_date': sdd,
        'end_date': edd,
        'data': PasAccomplishmentOutputs.objects.filter(Q(emp_id=request.session['emp_id']),
                                                        Q(date_period__gte=sdd),
                                                        Q(date_period__lte=edd)).order_by('date_period'),
        'all_days': alldays,
    }
    return render(request, 'frontend/pas/accomplishment/print_accomplishment.html', context)


@login_required()
def print_dtr(request):
    if request.method == "POST":
        sdd = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
        edd = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')

        employee = Empprofile.objects.get(id=request.session['emp_id'])

        # Save points for printing DTR
        gamify(19, request.session['emp_id'])

        delta = edd - sdd

        alldays = list()
        for i in range(delta.days + 1):
            alldays.append(sdd + timedelta(days=i))

        context = {
            'employee': employee,
            'signatory': get_signatory(request.session['emp_id'])['signatory'],
            'signatory_pos': get_signatory(request.session['emp_id'])['signatory_pos'],
            'start_date': sdd,
            'end_date': edd,
            'all_days': alldays,
        }
        return render(request, 'frontend/pas/accomplishment/print_dtr.html', context)


@login_required
@csrf_exempt
def generateform(request):
    if request.method == 'POST':
        sdate = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
        edate = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")

        delta = edate - sdate  # as timedelta
        alldates = []

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            alldates.append(day)

        return JsonResponse({'data': alldates})


@login_required
def accomplishment_report(request):
    if request.method == "POST":
        dates = request.POST.getlist('dates[]')
        places = request.POST.getlist('places[]')
        outputs = request.POST.getlist('outputs[]')

        # Parse dates once to avoid parsing them repeatedly later
        parsed_dates = [datetime.strptime(date, '%B %d, %Y').date() for date in dates]

        data = list(zip(parsed_dates, places, outputs))

        emp_id = request.session['emp_id']
        existing_entries = PasAccomplishmentOutputs.objects.filter(emp_id=emp_id, date_period__in=parsed_dates)
        existing_entries_dict = {entry.date_period: entry for entry in existing_entries}

        to_create = []
        for date, place, output in data:
            if date in existing_entries_dict:
                # Update existing entries in place
                existing_entry = existing_entries_dict[date]
                existing_entry.place_visited = place
                existing_entry.output = output
                existing_entry.save()
            else:
                # Collect new entries to create them all at once later
                to_create.append(PasAccomplishmentOutputs(
                    emp_id=emp_id,
                    date_period=date,
                    place_visited=place,
                    output=output
                ))

        if to_create:
            PasAccomplishmentOutputs.objects.bulk_create(to_create)

        return JsonResponse({'data': 'success'})

    context = {
        'title': 'profile',
        'sub_title': 'activities',
        'sub_sub_title': 'accomplishment',
    }
    return render(request, 'frontend/pas/accomplishment/accomplishment_report.html', context)


@login_required
@csrf_exempt
def async_get_accomplishment_outputs(request):
    if request.method == "POST":
        data = PasAccomplishmentOutputs.objects.values('place_visited', 'output').filter(emp_id=request.POST.get('emp_id'),
                                                                                  date_period=request.POST.get('date')).first()
        convert_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()

        weekend = check_if_weekend(convert_date)
        day = convert_date.strftime("%d")
        date = convert_date.strftime("%Y-%m-%d")
        date_formatted = convert_date.strftime("%B %d, %Y")
        date_formatted_two = convert_date.strftime("%B %d")
        return JsonResponse({'place_visited': data['place_visited'] if data else '', 'output': data['output'] if data else '',
                             'day': day, 'date': date, 'date_formatted': date_formatted,
                             'date_formatted_two': date_formatted_two,
                             'weekend': weekend})


@login_required
def get_accomplishment_report(request, start_date, end_date):
    date = []
    orig_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    delta = timedelta(days=1)

    while start_date <= end_date:
        date.append(start_date)
        start_date += delta

    context = {
        'start_date': orig_start_date,
        'end_date': end_date,
        'date': date
    }
    return render(request, 'frontend/pas/accomplishment/view_accomplishment_report.html', context)


@login_required
@csrf_exempt
def clear_accomplishment_report(request):
    PasAccomplishmentOutputs.objects.filter(date_period=request.POST.get('date'),
                                            emp_id=request.POST.get('emp_id')).delete()

    return JsonResponse({'data': 'success'})


@login_required
def fetchaccomplishment(request, date):
    acc = PasAccomplishmentOutputs.objects.filter(emp_id=request.session['emp_id'], date_period=date).first()
    return JsonResponse({'data': {'pv': acc.place_visited, 'op': acc.output, 'id': acc.id, 'rm': acc.remarks}}) if acc else JsonResponse(
        {'data': {'pv': '', 'op': '', 'id': '', 'rm': ''}})
