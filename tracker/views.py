import re
import math
import threading
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_sms_notification
from backend.libraries.leave.models import LeaveApplication, CTDORequests
from backend.models import Empprofile, Empstatus, Aoa
from backend.templatetags.tags import getemployeebyempid, force_token_decryption, get_color_coding
from backend.views import generate_serial_string
from tracker.models import TrackerStatus, TrackerPackage, TrackerPackageItem, TrackerPackageItemHistory, generate_token, \
    TrackerPackageCC, TrackerDraft, TrackerAnnouncements, TrackerSMSType


@login_required
def tracker(request):
    return render(request, 'tracker/home.html')


@login_required
def tracker_item(request):
    context = {
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first()
    }
    return render(request, 'tracker/track_item.html', context)


@login_required
def ship_documents(request):
    return render(request, 'tracker/ship_documents.html')


@login_required
def ctdo_tracker(request):
    if request.method == "POST":
        tracking_no = request.POST.getlist('tracking_no[]')
        with transaction.atomic():
            lasttrack = TrackerPackage.objects.order_by('-id').first()

            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'TT')

            forwarded = Empprofile.objects.filter(
                id_number=re.split('\[|\]', request.POST.get('forward_to'))[1]).first()

            package = TrackerPackage(
                doctype_id=2,
                createdby_id=request.session['emp_id'],
                tracking_no=track_num,
                latest_status_id=request.POST.get('tracker_status'),
                latest_docholder_id=forwarded.id
            )

            package.save()

            for row in tracking_no:
                ctdo = CTDORequests.objects.filter(tracking_no=row).first()

                TrackerPackageItem.objects.create(
                    emp_id=ctdo.emp_id,
                    document_date=ctdo.date_filed,
                    other_info="{}".format(ctdo.get_inclusive()),
                    leave_tracking_no=ctdo.tracking_no,
                    package_id=package.id
                )

            TrackerPackageItemHistory.objects.create(
                package_id=package.id,
                emp_id=request.session['emp_id'],
                forwarded_id=forwarded.id,
                status_id=request.POST.get('tracker_status'),
                notes=request.POST.get('remarks'),
                viewed=0
            )

            return JsonResponse({'data': 'success',
                                 'msg': 'Please take note of the Tracking No. {} for your reference as you transmit the following documents.'.format(
                                     track_num
                                 )})
        return JsonResponse({'error': True, 'msg': 'Unauthorized transaction.'})

    employee = getemployeebyempid(request.session['emp_id'])
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month + 1, 1)

    ctdo_list = []
    ctdo_within_month = CTDORequests.objects.filter(
        Q(date_filed__date__gte=month_start) &
        Q(date_filed__date__lt=month_end) &
        Q(emp__pi__user__is_active=1) &
        Q(emp__section_id=employee.section_id) &
        Q(emp__aoa_id=employee.aoa_id) &
        ~Q(emp__position__name__icontains='OJT')
    )

    for row in ctdo_within_month:
        latest_status = row.get_latest_tracker_status() if row.get_latest_tracker_status() == 'Pending' else ""
        if latest_status == 'Pending':
            ctdo_list.append(
                {'tracking_no': row.tracking_no,
                 'id_number': row.emp.id_number,
                 'full_name': row.emp.pi.user.get_fullname,
                 'position': row.emp.position.name,
                 'ctdo_dates': row.get_inclusive(),
                 }
            )


    context = {
        'drafts': TrackerDraft.objects.filter(created_by_id=request.session['emp_id'], type=2),
        'tracker_status': TrackerStatus.objects.filter(status=1).order_by('name'),
        'aoa': Aoa.objects.filter(status=1).order_by('name'),
        'ctdo_within_month': ctdo_list
    }
    return render(request, 'tracker/ctdo_tracker.html', context)


@login_required
def add_ctdo_employee(request):
    if request.method == "POST":
        employee_name = request.POST.get('employee_name')
        match = re.search(r'\[CTDO-\d{4}-\d{2}-\d{4}\]', employee_name)
        if match:
            tracking_number = match.group(0)[1:-1]
            ctdo = CTDORequests.objects.filter(tracking_no=tracking_number).first()

            TrackerDraft.objects.create(
                emp_id=ctdo.emp_id,
                tracking_number=ctdo.tracking_no,
                created_by_id=request.session['emp_id'],
                type=2
            )

            return JsonResponse({'full_name': ctdo.emp.pi.user.get_fullname.upper(),
                                 'position': ctdo.emp.position.name.upper(),
                                 'ctdo_dates': ctdo.get_inclusive(),
                                 'pk': generate_token(ctdo.tracking_no),
                                 'id': ctdo.tracking_no})


@login_required
@csrf_exempt
def add_ctdo_employee_within_month(request):
    if request.method == "POST":
        tracking_no = request.POST.get('tracking_no')
        ctdo = CTDORequests.objects.filter(tracking_no=tracking_no).first()

        return JsonResponse({'full_name': ctdo.emp.pi.user.get_fullname.upper(),
                             'position': ctdo.emp.position.name.upper(),
                             'ctdo_dates': ctdo.get_inclusive(),
                             'pk': generate_token(ctdo.tracking_no),
                             'id': ctdo.tracking_no})


@login_required
def dtr_tracker(request):
    if request.method == "POST":
        employee_id = request.POST.getlist('employee_id[]')
        with transaction.atomic():
            lasttrack = TrackerPackage.objects.order_by('-id').first()

            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'TT')

            forwarded = Empprofile.objects.filter(
                id_number=re.split('\[|\]', request.POST.get('forward_to'))[1]).first()

            package = TrackerPackage(
                doctype_id=3,
                createdby_id=request.session['emp_id'],
                tracking_no=track_num,
                latest_status_id=1,
                latest_docholder_id=forwarded.id
            )

            package.save()

            for row in employee_id:
                TrackerPackageItem.objects.create(
                    emp_id=row,
                    document_date=request.POST.get('document_date'),
                    other_info=request.POST.get('document_info'),
                    leave_tracking_no=None,
                    package_id=package.id
                )

            TrackerPackageItemHistory.objects.create(
                package_id=package.id,
                emp_id=request.session['emp_id'],
                forwarded_id=forwarded.id,
                status_id=1,
                notes=request.POST.get('note'),
                viewed=0
            )

            return JsonResponse({'data': 'success',
                                 'msg': 'Please take note of the Tracking No. {} for your reference as you transmit the following documents.'.format(
                                     track_num
                                 )})
        return JsonResponse({'error': True, 'msg': 'Unauthorized transaction.'})

    employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
    context = {
        'drafts': TrackerDraft.objects.filter(created_by_id=request.session['emp_id'], type=3),
        'employee': Empprofile.objects.filter(Q(pi__user__is_active=1) &
                                                Q(aoa_id=employee.aoa_id) &
                                              Q(section_id=employee.section_id) &
                                              ~Q(position__name__icontains='OJT'))
    }
    return render(request, 'tracker/dtr_tracker.html', context)


@login_required
def leave_tracker(request):
    if request.method == "POST":
        tracking_no = request.POST.getlist('tracking_no[]')
        with transaction.atomic():
            lasttrack = TrackerPackage.objects.order_by('-id').first()

            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'TT')

            forwarded = Empprofile.objects.filter(
                id_number=re.split('\[|\]', request.POST.get('forward_to'))[1]).first()

            package = TrackerPackage(
                doctype_id=4,
                createdby_id=request.session['emp_id'],
                tracking_no=track_num,
                latest_status_id=request.POST.get('tracker_status'),
                latest_docholder_id=forwarded.id
            )

            package.save()

            for row in tracking_no:
                leave = LeaveApplication.objects.filter(tracking_no=row).first()

                TrackerPackageItem.objects.create(
                    emp_id=leave.emp_id,
                    document_date=leave.date_of_filing,
                    other_info="{}; {}".format(leave.leavesubtype.name, leave.get_inclusive()),
                    leave_tracking_no=leave.tracking_no,
                    package_id=package.id
                )

            TrackerPackageItemHistory.objects.create(
                package_id=package.id,
                emp_id=request.session['emp_id'],
                forwarded_id=forwarded.id,
                status_id=request.POST.get('tracker_status'),
                notes=request.POST.get('remarks'),
                viewed=0
            )

            return JsonResponse({'data': 'success',
                                 'msg': 'Please take note of the Tracking No. {} for your reference as you transmit the following documents.'.format(
                                     track_num
                                 )})
        return JsonResponse({'error': True, 'msg': 'Unauthorized transaction.'})
    employee = getemployeebyempid(request.session['emp_id'])
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month + 1, 1)

    leave_list = []
    leave_within_month = LeaveApplication.objects.filter(
        Q(date_of_filing__date__gte=month_start) &
        Q(date_of_filing__date__lt=month_end) &
        Q(emp__pi__user__is_active=1) &
        Q(emp__aoa_id=employee.aoa_id) &
        Q(emp__section_id=employee.section_id) &
        ~Q(emp__position__name__icontains='OJT')
    )

    for row in leave_within_month:
        latest_status = row.get_latest_tracker_status() if row.get_latest_tracker_status() == 'Pending' else ""
        if latest_status == 'Pending':
            leave_list.append(
                {'tracking_no': row.tracking_no,
                 'id_number': row.emp.id_number,
                'full_name': row.emp.pi.user.get_fullname,
                'position': row.emp.position.name,
                'leave_dates': row.get_inclusive(),
                'leave_type': row.leavesubtype.name}
            )

    context = {
        'drafts': TrackerDraft.objects.filter(created_by_id=request.session['emp_id'], type=1),
        'tracker_status': TrackerStatus.objects.filter(status=1).order_by('name'),
        'leave_within_month': leave_list,
        'aoa': Aoa.objects.filter(status=1).order_by('name')
    }
    return render(request, 'tracker/leave_tracker.html', context)


@login_required
def add_leave_employee(request):
    if request.method == "POST":
        employee_name = request.POST.get('employee_name')
        match = re.search(r'\[LV-\d{4}-\d{2}-\d{4}\]', employee_name)
        if match:
            tracking_number = match.group(0)[1:-1]
            leave = LeaveApplication.objects.filter(tracking_no=tracking_number).first()

            TrackerDraft.objects.create(
                emp_id=leave.emp_id,
                tracking_number=leave.tracking_no,
                created_by_id=request.session['emp_id'],
                type=1
            )

            return JsonResponse({'full_name': leave.emp.pi.user.get_fullname.upper(),
                                 'position': leave.emp.position.name.upper(),
                                 'leave_dates': leave.get_inclusive(),
                                 'leave_type': leave.leavesubtype.name,
                                 'pk': generate_token(leave.tracking_no),
                                 'id': leave.tracking_no})


@login_required
@csrf_exempt
def remove_draft(request):
    if request.POST.get('tracking_no'):
        tracking_no = force_token_decryption(request.POST.get('tracking_no'))
        TrackerDraft.objects.filter(created_by_id=request.session['emp_id'],
                                    tracking_number=tracking_no,
                                    type=request.POST.get('docu_type')).delete()
    else:
        employee_id = force_token_decryption(request.POST.get('employee_id'))
        TrackerDraft.objects.filter(created_by_id=request.session['emp_id'],
                                    emp_id=employee_id,
                                    type=request.POST.get('docu_type')).delete()

    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
def add_leave_employee_within_month(request):
    if request.method == "POST":
        tracking_no = request.POST.get('tracking_no')
        leave = LeaveApplication.objects.filter(tracking_no=tracking_no).first()

        return JsonResponse({'full_name': leave.emp.pi.user.get_fullname.upper(),
                             'position': leave.emp.position.name.upper(),
                             'leave_dates': leave.get_inclusive(),
                             'leave_type': leave.leavesubtype.name,
                             'pk': generate_token(leave.tracking_no),
                             'id': leave.tracking_no})


@login_required
def print_transmittal(request, pk):
    data = []
    job_order = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk), emp__empstatus_id=1)
    cos = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk), emp__empstatus_id=2)
    contractual = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk), emp__empstatus_id=3)
    permanent = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk), emp__empstatus_id=4)
    regcon = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk), emp__empstatus_id=6)

    j_counter = 1
    for row in job_order:
        if j_counter == 1:
            data.append({
                'full_name': 'Job Order',
                'other_info': 1
            })

            data.append({
                'id': j_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })
        else:
            data.append({
                'id': j_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })

        j_counter = j_counter + 1

    c_counter = 1
    for row in cos:
        if c_counter == 1:
            data.append({
                'full_name': 'Contract of Service',
                'other_info': 1
            })

            data.append({
                'id': c_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })
        else:
            data.append({
                'id': c_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })

        c_counter = c_counter + 1

    cc_counter = 1
    for row in contractual:
        if cc_counter == 1:
            data.append({
                'full_name': 'Contractual',
                'other_info': 1
            })

            data.append({
                'id': cc_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })
        else:
            data.append({
                'id': cc_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })

        cc_counter = cc_counter + 1

    p_counter = 1
    for row in permanent:
        if p_counter == 1:
            data.append({
                'full_name': 'Permanent',
                'other_info': 1
            })

            data.append({
                'id': p_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })
        else:
            data.append({
                'id': p_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })

        p_counter = p_counter + 1

    rc_counter = 1
    for row in regcon:
        if rc_counter == 1:
            data.append({
                'full_name': 'Regular-Contractual',
                'other_info': 1
            })

            data.append({
                'id': rc_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })
        else:
            data.append({
                'id': rc_counter,
                'full_name': row.emp.pi.user.get_fullname,
                'empstatus': row.emp.empstatus.name,
                'other_info': row.other_info,
                'color': get_color_coding(row.emp.id)
            })

        rc_counter = rc_counter + 1

    first_page = data[:18]
    pages = data[18:]
    total_pages = len(first_page) + len(pages)

    context = {
        'first_page': first_page,
        'pagination': math.ceil(float(len(pages)) / 27) + 1 if total_pages > 18 else math.ceil(
            float(len(first_page)) / 18),
        'actual_pagination': math.ceil(float(len(pages)) / 27),
        'pages': pages,
        'employee_status': Empstatus.objects.filter(status=1),
        'package': TrackerPackage.objects.filter(id=force_token_decryption(pk)).first(),
    }
    return render(request, 'tracker/print_transmittal.html', context)


@login_required
def track_inbox(request):
    return render(request, 'tracker/inbox.html')


@login_required
def track_package(request):
    return render(request, 'tracker/track_package.html')


@login_required
def track_package_details(request, pk):
    package_history = TrackerPackageItemHistory.objects.filter(package_id=force_token_decryption(pk)).order_by('-datetime')

    TrackerPackageItemHistory.objects.filter(package_id=force_token_decryption(pk), forwarded_id=request.session['emp_id']).update(
        viewed=1
    )

    unique_empstatus = TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk)).values('emp__empstatus_id').distinct()
    empstatus = Empstatus.objects.filter(status=1, id__in=[row['emp__empstatus_id'] for row in unique_empstatus]).order_by('name')

    context = {
        'empstatus': empstatus,
        'package': TrackerPackage.objects.filter(id=force_token_decryption(pk)).first(),
        'package_item': TrackerPackageItem.objects.filter(package_id=force_token_decryption(pk)),
        'package_cc': TrackerPackageCC.objects.filter(package_id=force_token_decryption(pk)),
        'package_history': package_history,
        'tracker_status': TrackerStatus.objects.filter(id=6).order_by('name'),
    }
    return render(request, 'tracker/track_package_details.html', context)


@login_required
@csrf_exempt
def track_package_for_file(request):
    if request.method == "POST":
        if request.POST.get('type') == '4':
            TrackerPackageItemHistory.objects.create(
                package_id=request.POST.get('package_id'),
                emp_id=request.POST.get('emp_id'),
                forwarded_id=None,
                status_id=request.POST.get('type'),
                notes=None,
                viewed=0
            )

            TrackerPackage.objects.filter(id=request.POST.get('package_id')).update(
                latest_status_id=request.POST.get('type'),
                latest_docholder_id=request.session['emp_id']
            )

            # ADD TO TRANSMITTAL DATABASE

            return JsonResponse({'data': 'success',
                                 "msg": "You have successfully designated this package as ready for filing."
                                        " Please be aware that once this action is taken, the transaction cannot "
                                        "be undone or reversed."})


@login_required
@csrf_exempt
def track_package_received(request):
    if request.method == "POST":
        if request.POST.get('type') == '3':
            TrackerPackageItemHistory.objects.create(
                package_id=request.POST.get('package_id'),
                emp_id=request.POST.get('emp_id'),
                forwarded_id=request.POST.get('emp_id'),
                status_id=request.POST.get('type'),
                notes=None,
                viewed=0
            )

            return JsonResponse({'data': 'success',
                                 "msg": "You have successfully received this package. it's important to note that the transaction cannot be undone or reversed."})


@login_required
def track_carbon_copy(request):
    return render(request, 'tracker/track_cc.html')


@login_required
def track_package_cc(request, pk):
    if request.method == "POST":
        employee = request.POST.getlist('cc_to[]')
        package_id = force_token_decryption(pk)

        verify = []
        for row in employee:
            cc_id = re.split('\[|\]', row)[1]
            cc = Empprofile.objects.filter(id_number=cc_id).first()

            check = TrackerPackageCC.objects.filter(cc_id=cc.id, package_id=package_id)
            if not check:
                TrackerPackageCC.objects.create(
                    package_id=package_id,
                    cc_id=cc.id,
                    datetime=datetime.now()
                )
            else:
                verify.append(cc.pi.user.get_fullname)

        if verify:
            return JsonResponse({'error': True, 'msg': '{} have already been carbon copied on this package.'.
                                format(", ".join(row for row in verify))
                                 })
        else:
            return JsonResponse({'data': 'success', 'msg': 'You have successfully carbon copied this package.'})


@login_required
def track_package_forwarded(request, pk):
    if request.method == "POST":
        forwarded = Empprofile.objects.filter(
            id_number=re.split('\[|\]', request.POST.get('forward_to'))[1]).first()

        package_id = force_token_decryption(pk)

        TrackerPackageItemHistory.objects.create(
            package_id=package_id,
            emp_id=request.session['emp_id'],
            forwarded_id=forwarded.id,
            status_id=request.POST.get('tracker_status'),
            notes=request.POST.get('remarks'),
            viewed=0
        )

        TrackerPackage.objects.filter(id=package_id).update(
            latest_status_id=request.POST.get('tracker_status'),
            latest_docholder_id=forwarded.id
        )

        return JsonResponse({'data': 'success',
                             "msg": "You have successfully forwarded this package. it's important to note that the transaction cannot be undone or reversed."})


@login_required
def track_for_return(request, pk):
    package_id = force_token_decryption(pk)
    context = {
        'package': TrackerPackage.objects.filter(id=package_id).first(),
        'package_item': TrackerPackageItem.objects.filter(package_id=package_id),
    }
    return render(request, 'tracker/track_package_return.html', context)


@login_required
def return_document_package(request):
    if request.method == "POST":
        with transaction.atomic():
            item = request.POST.getlist('item_no[]')
            lasttrack = TrackerPackage.objects.order_by('-id').first()

            track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                generate_serial_string(None, 'TT')

            return_to = Empprofile.objects.filter(
                id_number=re.split('\[|\]', request.POST.get('return_to'))[1]).first()

            package = TrackerPackage(
                tracking_no=track_num,
                createdby_id=request.session['emp_id'],
                latest_status_id=5,
                latest_docholder_id=return_to.id,
                doctype_id=request.POST.get('doctype_id')
            )

            package.save()

            for row in item:
                TrackerPackageItem.objects.filter(id=row).update(
                    package_id=package.id
                )

            TrackerPackageItemHistory.objects.create(
                package_id=package.id,
                emp_id=request.session['emp_id'],
                forwarded_id=return_to.id,
                status_id=5,
                notes=request.POST.get('remarks'),
                viewed=0
            )

        return JsonResponse({'data': 'success',
                             'msg': 'The document is currently under processing and is slated for return. Please keep in mind that this action is irreversible and cannot be undone.'})


@login_required
def tracker_announcements(request):
    if request.method == "POST":
        emp = re.split('\[|\]', request.POST.get('employee'))
        employee = Empprofile.objects.values('id', 'pi__mobile_no').filter(id_number=emp[1]).first()

        details = "{}".format(", ".join(row for row in request.POST.getlist('details[]')))
        TrackerAnnouncements.objects.create(
            emp_id=employee['id'],
            dates=request.POST.get('dates'),
            details=details,
            status=0,
            created_by_id=request.session['emp_id'],
            date_created=datetime.now()
        )

        if employee['pi__mobile_no']:
            message = """Based on Personnel Administration Section records please be informed that you have not submitted
             the following documents: {} - {}. Note: As per COA Memorandum Circular No. 2012-01 dated June 14, 2021 under item 1.2.1,
             non-submission of said documents, shall mean exclusion in the next payroll preparation.
             For you information and compliance - The My PORTAL Team""".format(request.POST.get('dates'), details)

            t = threading.Thread(target=send_sms_notification,
                                 args=(message, employee['pi__mobile_no'], request.session['emp_id'], employee['id']))
            t.start()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully added it to the tracker announcements'})
    context = {
        'sms_type': TrackerSMSType.objects.order_by('type')
    }
    return render(request, 'tracker/announcements.html', context)


@login_required
def edit_tracker_announcements(request, pk):
    if request.method == "POST":
        announcement = TrackerAnnouncements.objects.filter(id=pk)

        announcement.update(
            dates=request.POST.get('dates'),
            details=request.POST.getlist('details'),
            status=request.POST.get('status'),
        )

        if request.POST.get('status') == 1:
            employee = Empprofile.objects.values('id', 'pi__mobile_no').filter(id=announcement.first().emp_id).first()
            if employee['pi__mobile_no']:
                message = """
                According to the records of the Personnel Administration Section, we would like to inform 
                you that you have already submitted the following documents: {} - {}. Please note that according to COA 
                Memorandum Circular No. 2012-01, issued on June 14, 2021, under section 1.2.1, any failure to submit 
                these necessary documents will result in exclusion from the next payroll cycle. We appreciate your 
                understanding and cooperation. Best regards, The My PORTAL Team
                """.format(request.POST.get('dates'), request.POST.getlist('details'))

                t = threading.Thread(target=send_sms_notification,
                                     args=(message, employee['pi__mobile_no'], request.session['emp_id'], employee['id']))
                t.start()

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the tracker announcements'})

    context = {
        'data': TrackerAnnouncements.objects.filter(id=pk).first()
    }
    return render(request, 'tracker/update_announcements.html', context)