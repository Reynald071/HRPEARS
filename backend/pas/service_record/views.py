import math
from datetime import datetime, date, time

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.documents.models import DtsDocument, DtsDrn, DtsTransaction, DtsDivisionCc
from backend.models import Empprofile, Position, Empstatus, DRNTracker
from backend.pas.service_record.models import PasServiceRecord, PasServiceRecordData
from backend.views import generate_serial_string
from frontend.models import Workhistory, Workexperience, PortalConfiguration
from frontend.templatetags.tags import generateDRN


@login_required
def service_record(request):
    context = {
        'tab_title': 'Service Record',
        'title': 'employee',
        'sub_title': 'service_record',
    }
    return render(request, 'backend/pas/employee/service_record/service_record.html', context)


@login_required
def generate_service_record(request, employee_name):
    employee = Empprofile.objects.filter(id_number=employee_name).first()
    context = {
        'employee': employee,
    }
    return render(request, 'backend/pas/employee/service_record/sr_data.html', context)


@login_required
def generate_sr_template(request, employee_name):
    employee = Empprofile.objects.filter(id_number=employee_name).first()
    if request.method == "POST":
        check = PasServiceRecord.objects.filter(emp_id=employee.id, status=0)

        if check:
            check.update(
                maiden_name=request.POST.get('maiden_name').upper(),
                document_date=request.POST.get('document_date'),
                other_signature=request.POST.get('other_signature'),
                status=1
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully save the service record'})

    check = PasServiceRecord.objects.filter(emp_id=employee.id, status=0)
    if not check:
        sr = PasServiceRecord(
            emp_id=employee.id,
            created_by_id=request.session['emp_id'],
            status=0
        )

        sr.save()

    # Automation of Work History
    data = Workexperience.objects.filter(Q(
            Q(company__icontains='DSWD') | Q(
        company__icontains='Department of Social Welfare and Development, Field Office Caraga')
            | Q(company__icontains='Department of Social Welfare and Development')
    ) & Q(pi_id=employee.pi_id) & Q(empstatus_id__in=[3, 4, 6]))

    data.update(
        company='Department of Social Welfare and Development, Field Office Caraga'.upper()
    )

    for row in data:
        check = Workhistory.objects.filter(we_id=row.id).first()
        if check is None:
            Workhistory.objects.create(
                emp_id=employee.id,
                we_id=row.id
            )
    
    # Creation of Work History on Service Record Data
    sr_data = PasServiceRecord.objects.filter(emp_id=employee.id, status=0).first()

    check_previous = PasServiceRecord.objects.filter(emp_id=employee.id, status=1).order_by('-id').first()

    if check_previous:
        previous_data = PasServiceRecordData.objects.filter(sr_id=check_previous.id)
        for row in previous_data:
            check_sr_data = PasServiceRecordData.objects.filter(wh_id=row.wh_id, sr_id=sr_data.id)
            if not check_sr_data:
                PasServiceRecordData.objects.create(
                    wh_id=row.wh_id,
                    branch="National",
                    is_leave_wo_pay=row.is_leave_wo_pay,
                    date=row.date,
                    cause=row.cause,
                    poa="DSWD, Region XIII",
                    sr_id=sr_data.id
                )
    else:
        wh = Workhistory.objects.filter(emp_id=employee.id, we_id__in=[row.id for row in data],
                                        we__empstatus_id__in=[3, 4, 6]).order_by('we__we_to')
        for row in wh:
            check_sr_data = PasServiceRecordData.objects.filter(wh_id=row.id, sr_id=sr_data.id)
            if not check_sr_data:
                PasServiceRecordData.objects.create(
                    wh_id=row.id,
                    sr_id=sr_data.id
                )

    sr_data_list = []
    today = date.today()
    service_record_data = PasServiceRecordData.objects.filter(sr_id=sr_data.id, date=None).order_by('wh__we__we_from')

    for row in service_record_data:
        sr_data_list.append({
            'id': row.id,
            'start_date': row.wh.we.we_from,
            'end_date': "Present" if row.wh.we.we_from <= today <= row.wh.we.we_to else row.wh.we.we_to,
            'position': row.wh.we.position.name,
            'empstatus': row.wh.we.empstatus.name,
            'salary': row.wh.we.salary_rate,
            'poa': row.poa,
            'branch': row.branch,
            'is_leave_wo_pay': row.is_leave_wo_pay,
            'leave_w_pay_date': row.leave_w_pay_date,
            'date': row.wh.we.we_to,
            'cause': row.cause
        })

    service_record_other_data = PasServiceRecordData.objects.filter(Q(sr_id=sr_data.id), ~Q(date=None))
    for row in service_record_other_data:
        sr_data_list.append({
            'id': row.id,
            'start_date': row.wh.we.we_from if row.wh_id else row.date,
            'end_date': ("Present" if row.wh.we.we_from <= today <= row.wh.we.we_to else row.wh.we.we_to) if row.wh_id else None,
            'position': row.wh.we.position.name if row.wh_id else None,
            'empstatus': row.wh.we.empstatus.name if row.wh_id else None,
            'salary': row.wh.we.salary_rate if row.wh_id else None,
            'poa': row.poa if row.wh_id else None,
            'branch': row.branch if row.wh_id else None,
            'is_leave_wo_pay': row.is_leave_wo_pay if row.wh_id else None,
            'leave_w_pay_date': row.leave_w_pay_date if row.wh_id else None,
            'date': row.date,
            'cause': row.cause
        })


    context = {
        'employee': employee,
        'check': PasServiceRecord.objects.filter(emp_id=employee.id, status=0).first(),
        'data': sorted(sr_data_list, key=lambda e: (e['start_date'] or date.max)),
        'position': Position.objects.filter(status=1).order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1).order_by('name')
    }
    return render(request, 'backend/pas/employee/service_record/template.html', context)


@login_required
@csrf_exempt
def generate_drn_for_service_record(request, sr_id):
    if request.method == "POST":
        lasttrack = DtsDocument.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'DT')

        sender = Empprofile.objects.filter(id=request.session['emp_id']).first()
        document = DtsDocument(
            doctype_id=40,
            docorigin_id=2,
            sender=sender.pi.user.get_fullname,
            subject="Service Record",
            purpose="For Signature",
            document_date=datetime.now(),
            document_deadline=None,
            tracking_no=track_num,
            creator_id=request.session['emp_id'],
            drn=None
        )

        document.save()

        drn_data = DtsDrn(
            document_id=document.id,
            category_id=2,
            doctype_id=40,
            division_id=1,
            section_id=1
        )

        drn_data.save()

        generated_drn = generateDRN(document.id, drn_data.id, True)
        config = PortalConfiguration.objects.filter(id=19).first()

        if document:
            for x in range(2):
                DtsTransaction.objects.create(
                    action=x,
                    trans_from_id=request.session['emp_id'],
                    trans_to_id=config.key_acronym,
                    trans_datestarted=None,
                    trans_datecompleted=None,
                    action_taken=None,
                    document_id=document.id
                )

        DtsDivisionCc.objects.create(
            document_id=document.id,
            division_id=1
        )

        PasServiceRecord.objects.filter(id=sr_id).update(
            drn=generated_drn
        )

        return JsonResponse({'data': 'success', 'drn': generated_drn})


@login_required
def add_sr_workhistory(request, id_number):
    employee = Empprofile.objects.filter(id_number=id_number).first()
    if request.method == "POST":
        if request.POST.get('separation_date') and request.POST.get('cause'):
            PasServiceRecordData.objects.create(
                sr_id=request.POST.get('sr_id'),
                date=request.POST.get('separation_date'),
                cause=request.POST.get('cause')
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully added the service record.'})
        else:
            check = Workexperience.objects.filter(we_from=request.POST.get('from'), we_to=request.POST.get('to'), pi_id=employee.pi_id)

            if check:
                check.update(
                    company="DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT, FIELD OFFICE CARAGA",
                    position=request.POST.get('designation'),
                    empstatus=request.POST.get('empstatus'),
                    salary_rate=request.POST.get('salary_rate')
                )

                work_history = Workhistory.objects.filter(we_id=check.first().id, emp_id=employee.id)
                if not work_history:
                    Workhistory.objects.create(
                        emp_id=employee.id,
                        we_id=check.first().id
                    )

                sr_data = PasServiceRecordData.objects.filter(wh_id=work_history.first().id, sr_id=request.POST.get('sr_id'))
                if sr_data:
                    sr_data.update(
                        poa=request.POST.get('poa'),
                        branch=request.POST.get('branch'),
                        is_leave_wo_pay=1 if request.POST.get('is_leave_wo_pay') else 0
                    )
                else:
                    PasServiceRecordData.objects.create(
                        wh_id=work_history.first().id,
                        sr_id=request.POST.get('sr_id'),
                        poa=request.POST.get('poa'),
                        branch=request.POST.get('branch'),
                        is_leave_wo_pay=1 if request.POST.get('is_leave_wo_pay') else 0,
                    )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully added the service record.'})
            else:
                we = Workexperience(
                    we_from=request.POST.get('from'),
                    we_to=request.POST.get('to'),
                    position_id=request.POST.get('designation'),
                    empstatus_id=request.POST.get('empstatus'),
                    company="DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT, FIELD OFFICE CARAGA",
                    salary_rate=request.POST.get('salary_rate'),
                    govt_service=1,
                    pi_id=employee.pi_id
                )

                we.save()

                wh = Workhistory(
                    emp_id=employee.id,
                    we_id=we.id
                )

                wh.save()

                sr_data = PasServiceRecordData.objects.filter(wh_id=wh.id, sr_id=request.POST.get('sr_id'))
                if sr_data:
                    sr_data.update(
                        poa=request.POST.get('poa'),
                        branch=request.POST.get('branch'),
                        is_leave_wo_pay=1 if request.POST.get('is_leave_wo_pay') else 0
                    )
                else:
                    PasServiceRecordData.objects.create(
                        wh_id=wh.id,
                        sr_id=request.POST.get('sr_id'),
                        poa=request.POST.get('poa'),
                        branch=request.POST.get('branch'),
                        is_leave_wo_pay=1 if request.POST.get('is_leave_wo_pay') else 0
                    )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully added the service record.'})


@login_required
def edit_sr_workhistory(request, pk):
    if request.method == "POST":
        Workexperience.objects.filter(id=request.POST.get('we_id')).update(
            we_from=request.POST.get('from'),
            we_to=request.POST.get('to'),
            position=request.POST.get('designation'),
            empstatus=request.POST.get('empstatus'),
            salary_rate=request.POST.get('salary_rate')
        )

        PasServiceRecordData.objects.filter(id=pk).update(
            poa=request.POST.get('poa'),
            branch=request.POST.get('branch'),
            is_leave_wo_pay=1 if request.POST.get('is_leave_wo_pay') else 0,
            date=request.POST.get('separation_date') if request.POST.get('separation_date') else None,
            cause=request.POST.get('cause'),
            leave_w_pay_date=request.POST.get('leave_w_pay_date') if request.POST.get('leave_w_pay_date') else None
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the workhistory.'})

    context = {
        'data': PasServiceRecordData.objects.filter(id=pk).first(),
        'position': Position.objects.order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1).order_by('name')
    }
    return render(request, 'backend/pas/employee/service_record/edit_sr.html', context)


@login_required
@csrf_exempt
def delete_service_record_data(request, pk):
    if request.method == "POST":
        check = PasServiceRecordData.objects.filter(id=pk).delete()
        return JsonResponse({'data': 'success', 'msg': 'You have successfully deleted the service record data'})


@login_required
def print_service_record(request, pk):
    if request.method == "POST":
        PasServiceRecord.objects.filter(id=pk).update(
            drn=request.POST.get('drn')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the DRN.'})

    data = []
    today = date.today()
    service_record_data = PasServiceRecordData.objects.filter(Q(sr_id=pk) & Q(date=None)).order_by('wh__we__we_from')

    for row in service_record_data:
        data.append({
            'id': row.id,
            'start_date': row.wh.we.we_from,
            'end_date': "Present" if row.wh.we.we_from <= today <= row.wh.we.we_to else row.wh.we.we_to,
            'position': row.wh.we.position.name,
            'empstatus': row.wh.we.empstatus.name,
            'salary': row.wh.we.salary_rate,
            'poa': row.poa,
            'branch': row.branch,
            'is_leave_wo_pay': row.is_leave_wo_pay,
            'leave_w_pay_date': row.leave_w_pay_date,
            'date': row.wh.we.we_to,
            'cause': row.cause
        })

    service_record_other_data = PasServiceRecordData.objects.filter(Q(sr_id=pk), ~Q(date=None))
    for row in service_record_other_data:
        data.append({
            'id': row.id,
            'start_date': row.wh.we.we_from if row.wh_id else row.date,
            'end_date': ("Present" if row.wh.we.we_from <= today <= row.wh.we.we_to else row.wh.we.we_to) if row.wh_id else None,
            'position': row.wh.we.position.name if row.wh_id else None,
            'empstatus': row.wh.we.empstatus.name if row.wh_id else None,
            'salary': row.wh.we.salary_rate if row.wh_id else None,
            'poa': row.poa if row.wh_id else None,
            'branch': row.branch if row.wh_id else None,
            'is_leave_wo_pay': row.is_leave_wo_pay if row.wh_id else None,
            'leave_w_pay_date': row.leave_w_pay_date if row.wh_id else None,
            'date': row.date,
            'cause': row.cause
        })

    first_page = sorted(data, key=lambda e: (e['start_date'] or date.max))[:16]
    pages = sorted(data, key=lambda e: (e['start_date'] or date.max))[16:]
    total_pages = len(first_page) + len(pages)
    context = {
        'first_page': first_page,
        'pagination': math.ceil(float(len(pages)) / 24) + 1 if total_pages > 16 else math.ceil(float(len(first_page)) / 16),
        'actual_pagination': math.ceil(float(len(pages)) / 24),
        'footnote': PortalConfiguration.objects.filter(key_name='Service Record Footnote').first(),
        'data': PasServiceRecord.objects.filter(id=pk).first(),
        'sr_data': pages,
    }
    return render(request, 'backend/pas/employee/service_record/print_service_record.html', context)
