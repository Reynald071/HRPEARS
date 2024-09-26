from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.documents.models import DtsDocument, DtsDrn, DtsTransaction, DtsDivisionCc
from backend.models import Empprofile
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration
from frontend.rsp.models import RspIntroLetter
from frontend.templatetags.tags import generateDRN


@login_required
def intro_letter(request):
    return render(request, 'frontend/rsp/intro_letter.html')


@login_required
def intro_letter_data(request, employee_id):
    context = {
        'employee': Empprofile.objects.filter(id_number=employee_id).first()
    }
    return render(request, 'frontend/rsp/intro_letter_data.html', context)


@login_required
def intro_letter_layout(request, employee_id):
    employee = Empprofile.objects.filter(id_number=employee_id).first()
    if request.method == "POST":
        check = RspIntroLetter.objects.filter(emp_id=employee.id, status=0)
        if check.first().generated_drn:
            check.update(
                content=request.POST.get('content').strip(),
                status=1,
                date_created=datetime.now()
            )
            return JsonResponse({'data': 'success', 'msg': 'You have successfully save the intro letter.'})
        else:
            return JsonResponse({'error': True, 'msg': 'You forgot to generate the DRN before saving.'})
    check = RspIntroLetter.objects.filter(emp_id=employee.id, status=0)
    if not check:
        RspIntroLetter.objects.create(
            emp_id=employee.id,
            status=0,
            created_by_id=request.session['emp_id']
        )

    context = {
        'data': RspIntroLetter.objects.filter(emp_id=employee.id, status=0).first(),
        'employee': employee
    }
    return render(request, 'frontend/rsp/intro_letter_layout.html', context)


@login_required
def intro_letter_print(request, io_id):
    context = {
        'data': RspIntroLetter.objects.filter(id=io_id).first(),
    }
    return render(request, 'frontend/rsp/intro_letter_print.html', context)


@login_required
@csrf_exempt
def generate_drn_for_intro_letter(request, io_id):
    if request.method == "POST":
        lasttrack = DtsDocument.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'DT')

        sender = Empprofile.objects.filter(id=request.session['emp_id']).first()
        document = DtsDocument(
            doctype_id=40,
            docorigin_id=2,
            sender=sender.pi.user.get_fullname,
            subject="Intro Letter",
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
            category_id=1,
            doctype_id=7,
            division_id=1,
            section_id=1
        )

        drn_data.save()

        generated_drn = generateDRN(document.id, drn_data.id, True)
        config = PortalConfiguration.objects.filter(id=16).first()

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

        RspIntroLetter.objects.filter(id=io_id).update(
            generated_drn=generated_drn
        )

        return JsonResponse({'data': 'success', 'drn': generated_drn})


@login_required
def rso_for_assignment(request):
    context = {
        'tab_title': 'Regional Special Order for Assignment',
        'title': 'rsp',
        'sub_title': 'so_for_assignment'
    }
    return render(request, 'frontend/rsp/rso_for_assignment.html', context)


@login_required
def rso_for_assignment_layout(request, employee_id):
    context = {
        'employee': Empprofile.objects.filter(id_number=employee_id).first()
    }
    return render(request, 'frontend/rsp/rso_for_assignment_layout.html', context)