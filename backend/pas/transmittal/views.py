import re
import threading
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.wiserv import send_sms_notification
from backend.models import Division, Empprofile, PortalErrorLogs
from backend.pas.transmittal.models import TransmittalNew, TransmittalTransaction, TransmittalType
from backend.views import generate_serial_string


@login_required
def transmittal(request):
    if request.method == "POST":
        emp = request.POST.getlist('emp_id[]')
        if emp:
            with transaction.atomic():
                status = ['Incoming', 'Outgoing', 'has been approved ', 'has been disapproved due to ',
                          'is subject for return due to ']
                lasttrack = TransmittalNew.objects.order_by('-id').first()
                track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                    generate_serial_string(None, 'PAS')

                for row in emp:
                    data = TransmittalNew(
                        tracking_no=track_num,
                        document_name_id=request.POST.get('document_type'),
                        document_date=request.POST.get('date_document'),
                        details=request.POST.get('other_info') if request.POST.get('other_info') else None,
                        emp_id=row
                    )

                    data.save()

                    TransmittalTransaction.objects.create(
                        trans_id=data.id,
                        status=request.POST.get('status'),
                        date=request.POST.get('date_received'),
                        forwarded_to_id=request.POST.get('forward_to') if request.POST.get('forward_to') else None,
                        emp_id=request.session['emp_id']
                    )

                    document = TransmittalType.objects.filter(id=request.POST.get('document_type')).first()
                    employee = Empprofile.objects.filter(id=row).first()

                    if request.POST.get('status') == "0":
                        t = threading.Thread(target=send_sms_notification,
                                             args=("Mr./Ms. {}, we are pleased to inform you that your {} {} has been received by the Personnel Administration Section and ready for processing. - The My PORTAL Team".
                                      format(employee.pi.user.last_name, document.name, request.POST.get('other_info')), employee.pi.mobile_no, request.session['emp_id']))
                        t.start()
                    elif request.POST.get('status') != "1":
                        t = threading.Thread(target=send_sms_notification,
                                             args=("Mr./Ms. {}, we are pleased to inform you that your {} {} {}{} by the Personnel Administration Section. - The My PORTAL Team".
                            format(employee.pi.user.last_name,
                                   data.document_name.name,
                                   data.details,
                                   status[int(request.POST.get('status'))].lower(),
                                   request.POST.get('remarks')) + " " if request.POST.get('remarks') else "",
                            employee.pi.mobile_no,
                            request.session['emp_id']
                        ))

                        t.start()

                return JsonResponse({'data': 'success'})
            return JsonResponse({'error': True, 'msg': 'Unauthorized Transaction.'})
        else:
            return JsonResponse({'error': True, 'msg': 'There is no selected employee. Please select atleast one employee to proceed.'})

    context = {
        'division': Division.objects.all().order_by('div_name'),
        'type': TransmittalType.objects.filter(status=1).order_by('name'),
        'management': True,
        'title': 'transmittal',
        'tab_title': 'Transmittal'
    }
    return render(request, 'backend/transmittal/transmittal.html', context)


@login_required
def update_transmittal(request):
    context = {

    }
    return render(request, 'backend/transmittal/update_transmittal.html')


@login_required
@csrf_exempt
def delete_transmittal(request):
    if request.method == "POST":
        TransmittalNew.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
def view_transmittal(request, pk):
    context = {
        'employee': Empprofile.objects.filter(id_number=pk).first()
    }
    return render(request, 'backend/transmittal/view_transmittal.html', context)


@login_required
def view_transmittal_details(request, pk):
    if request.method == "POST":
        try:
            status = ['Incoming', 'Outgoing', 'has been approved ', 'has been disapproved due to ', 'is subject for return due to ']
            transmittal = TransmittalNew.objects.filter(id=pk).first()

            TransmittalTransaction.objects.create(
                trans_id=pk,
                status=request.POST.get('status'),
                remarks=request.POST.get('remarks') if request.POST.get('remarks') else None,
                emp_id=request.session['emp_id'],
                date_approved=datetime.now()
            )

            message = "Mr./Ms. {}, we are pleased to inform you that your {} {} {}{} by the Personnel Administration Section. - The My PORTAL Team".\
                          format(transmittal.emp.pi.user.last_name,
                           transmittal.document_name.name,
                           transmittal.details,
                           status[int(request.POST.get('status'))].lower(),
                           request.POST.get('remarks')) + " " if request.POST.get('remarks') else ""

            t = threading.Thread(target=send_sms_notification,
                                 args=(message, transmittal.emp.pi.mobile_no, request.session['emp_id'], transmittal.emp.id))
            t.start()

            return JsonResponse({'data': 'success', 'msg': 'Transmittal status have been updated successfully.'})
        except Exception as e:
            PortalErrorLogs.objects.create(
                logs='Transmittal Update Status: {}'.format(e),
                date_created=datetime.now(),
                emp=request.session['emp_id']
            )

    context = {
        'transmittal': TransmittalNew.objects.filter(id=pk).first(),
        'type': TransmittalType.objects.filter(status=1).order_by('name'),
    }
    return render(request, 'backend/transmittal/view_transmittal_details.html', context)


@login_required
@csrf_exempt
def update_transmittal_details(request, pk):
    if request.method == "POST":
        try:
            TransmittalNew.objects.filter(id=pk).update(
                document_name_id=request.POST.get('document_name'),
                document_date=request.POST.get('document_date'),
                details=request.POST.get('details')
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the transmittal details.'})
        except Exception as e:
            PortalErrorLogs.objects.create(
                logs='Transmittal Update Details: {}'.format(e),
                date_created=datetime.now(),
                emp=request.session['emp_id']
            )

