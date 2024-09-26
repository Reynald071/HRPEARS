import hashlib
import math
import os
import re
import threading
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1
from dotenv import load_dotenv

from api.wiserv import send_notification
from backend.models import Division, Designation, Empprofile, Section
from frontend.lds.forms import UploadAttachmentFormLDS
from frontend.lds.models import LdsRso, LdsParticipants, LdsFacilitator, LdsCertificateType, LdsIDP, LdsIDPType, \
    LdsIDPContent
from frontend.models import Trainingtitle, PortalConfiguration

load_dotenv()


def lds_rrso(request):
    if request.method == "POST":
        with transaction.atomic():
            check = LdsRso.objects.filter(id=request.POST.get('rso_id'))
            if check:
                Trainingtitle.objects.filter(id=check.first().training_id).update(
                    tt_name=request.POST.get('title')
                )

                check.update(
                    venue=request.POST.get('venue'),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date'),
                    is_online_platform=1 if request.POST.get('is_online_platform') else 0
                )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the training'})
            else:
                training = Trainingtitle(
                    tt_name=request.POST.get('title'),
                    tt_status=0,
                    pi_id=request.session['pi_id']
                )

                training.save()

                LdsRso.objects.create(
                    training_id=training.id,
                    venue=request.POST.get('venue'),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date'),
                    rrso_status=0,
                    rso_status=0,
                    date_approved=None,
                    attachment=None,
                    created_by_id=request.session['emp_id'],
                    is_online_platform=1 if request.POST.get('is_online_platform') else 0
                )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully created an training'})
        return JsonResponse({'error': True, 'msg': 'Unauthorized transaction'})
    context = {
        'tab_parent': 'Learning and Development Management',
        'tab_title': 'Training Requests',
        'title': 'learning_and_development',
        'sub_title': 'lds_rrso'
    }
    return render(request, 'frontend/lds/rrso.html', context)


def training_details(request, pk):
    obj = get_object_or_404(LdsRso, pk=pk)
    context = {
        'attachment_form': UploadAttachmentFormLDS(instance=obj),
        'training': LdsRso.objects.filter(id=pk).first(),
        'participants': LdsParticipants.objects.filter(rso_id=pk).order_by('emp__pi__user__last_name'),
        'facilitators': LdsFacilitator.objects.filter(rso_id=pk).order_by('emp__pi__user__last_name'),
    }
    return render(request, 'frontend/lds/training_details.html', context)


@login_required
def upload_ld_attachment(request, pk):
    obj = get_object_or_404(LdsRso, pk=pk)
    form = UploadAttachmentFormLDS(request.POST, request.FILES, instance=obj)
    if request.method == "POST":
        if form.is_valid():
            rso = form.save(commit=False)
            rso.rso_status = 1
            rso.save()
    return JsonResponse({'data': 'success', 'msg': 'Attachment uploaded successfully.'})


@login_required
def print_ld_attendance(request, pk):
    data = LdsRso.objects.filter(id=pk).first()
    dates = []
    delta = timedelta(days=1)
    while data.start_date <= data.end_date:
        dates.append(data.start_date)
        data.start_date += delta

    facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=0).order_by('emp__pi__user__last_name')
    ex_facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=1)
    participant = LdsParticipants.objects.filter(rso_id=pk, type=0).order_by('emp__pi__user__last_name')
    ex_participant = LdsParticipants.objects.filter(rso_id=pk, type=1)
    participants_and_facilitators = []

    for row in facilitator:
        participants_and_facilitators.append({
            'employee_name': row.emp.pi.user.get_fullname,
            'section': row.emp.section.sec_acronym if row.emp.section_id else "",
            'position': row.emp.position.acronym if row.emp.position.acronym else "",
            'sex': "Male" if row.emp.pi.gender == 1 else "Female",
            'email': row.emp.pi.user.email if row.emp.pi.user.email else "",
            'contact_number': row.emp.pi.mobile_no if row.emp.pi.mobile_no else ""
        })

    for row in ex_facilitator:
        participants_and_facilitators.append({
            'employee_name': row.rp_name,
            'section': "",
            'position': "",
            'sex': "",
            'email': "",
            'contact_number': ""
        })

    for row in participant:
        participants_and_facilitators.append({
            'employee_name': row.emp.pi.user.get_fullname,
            'section': row.emp.section.sec_acronym if row.emp.section_id else "",
            'position': row.emp.position.acronym if row.emp.position.acronym else "",
            'sex': "Male" if row.emp.pi.gender == 1 else "Female",
            'email': row.emp.pi.user.email if row.emp.pi.user.email else "",
            'contact_number': row.emp.pi.mobile_no if row.emp.pi.mobile_no else ""
        })

    for row in ex_participant:
        participants_and_facilitators.append({
            'employee_name': row.participants_name,
            'section': "",
            'position': "",
            'sex': "",
            'email': "",
            'contact_number': ""
        })

    for row in range(40):
        participants_and_facilitators.append({
            'employee_name': "",
            'section': "",
            'position': "",
            'sex': "",
            'email': "",
            'contact_number': ""
        })

    pagination = len(participants_and_facilitators)
    context = {
        'training': data,
        'dates': dates,
        'pagination': math.ceil(float(pagination) / 20),
        'participants_and_facilitators': participants_and_facilitators,
        'ld_head': Section.objects.filter(id=3).first()
    }
    return render(request, 'frontend/lds/print_attendance.html', context)


def print_rrso(request, pk):
    facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=0).order_by('-order', 'emp__pi__user__last_name')
    ex_facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=1).order_by('-order', 'rp_name')
    internal_participants = LdsParticipants.objects.filter(rso_id=pk, type=0).order_by('-order',
                                                                                       'emp__pi__user__last_name')
    external_participants = LdsParticipants.objects.filter(rso_id=pk, type=1).order_by('-order', 'participants_name')

    context = {
        'training': LdsRso.objects.filter(id=pk).first(),
        'facilitator': facilitator,
        'ex_facilitator': ex_facilitator,
        'internal_participants': internal_participants,
        'external_participants': external_participants,
        'hrmdd_dc': Division.objects.filter(div_acronym='HRMDD').first(),
        'rd': Designation.objects.filter(id=1).first(),
    }
    return render(request, 'frontend/lds/print_rrso.html', context)


def add_training_participant(request, pk, type):
    if request.method == "POST":
        if type == 0:
            id_number = re.split('\[|\]', request.POST.get('employee'))
            emp = Empprofile.objects.values('id', 'pi__mobile_no').filter(id_number=id_number[1]).first()
            check = LdsParticipants.objects.filter(emp_id=emp['id'], rso_id=pk)
            if not check:
                participant = LdsParticipants(
                    emp_id=emp['id'],
                    rso_id=pk,
                    type=type
                )

                detail = LdsRso.objects.filter(id=pk).first()
                url = '{}/email-confirmation/{}/{}'.format(os.getenv("SERVER_URL"),
                                                           hashlib.sha1(str(pk).encode('utf-8')).hexdigest(),
                                                           hashlib.sha1(str(emp['id']).encode('utf-8')).hexdigest())

                message = """<p>Greetings! 
                        <br><br>
                        Please be informed that you are one of the participants to join the <strong>{}</strong> on
                        <strong>{}</strong> to be held {} <strong>{}</strong>. <br><br> To confirm your attendance, kindly click this link: <br>
                        <a href='{}'>{}</a><br><br>
                        {} 
                        </p>    
                    """.format(
                    detail.training.tt_name,
                    detail.get_inclusive_dates,
                    'via' if detail.is_online_platform else 'at',
                    detail.venue,
                    url,
                    url,
                    " - " + detail.created_by.section.sec_name if detail.created_by.section_id else ""
                )
                t = threading.Thread(target=send_notification,
                                     args=(message, emp['pi__mobile_no'], request.session['emp_id'], emp['id']))
                t.start()

                participant.save()

                return JsonResponse(
                    {'data': 'success', 'msg': 'You have successfully added the participant in the training'})
            else:
                return JsonResponse({'error': True, 'msg': 'Participant already existed in the training.'})
        else:
            participant = LdsParticipants(
                participants_name=request.POST.get('employee').upper(),
                rso_id=pk,
                type=type
            )

            participant.save()

            return JsonResponse(
                {'data': 'success', 'msg': 'You have successfully added the participant in the training'})


def email_confirmation_participants(request, rso_pk, emp_pk):
    check = LdsParticipants.objects.annotate(rso_pk=SHA1('rso_id'), emp_pk=SHA1('emp_id')).filter(
        rso_pk=rso_pk,
        emp_pk=emp_pk
    )

    check.update(
        is_present=1
    )

    if check:
        context = {
            'data': check.first()
        }
        return render(request, 'frontend/lds/email_confirmation.html', context)
    else:
        raise Http404("You are not authorized to access this page.")


def add_training_facilitator(request, pk, type):
    if request.method == "POST":
        try:
            if type == 0:
                id_number = re.split('\[|\]', request.POST.get('employee'))
                emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()
                check_participant = LdsParticipants.objects.filter(emp_id=emp['id'], rso_id=pk)
                check_facilitator = LdsFacilitator.objects.filter(emp_id=emp['id'], rso_id=pk)
                if check_participant:
                    return JsonResponse({'error': True,
                                         'msg': "You can't add this employee as a facilitator because it already existed in the participant."})
                else:
                    if not check_facilitator:
                        facilitator = LdsFacilitator(
                            emp_id=emp['id'],
                            rso_id=pk,
                            is_external=0,
                            is_resource_person=0,
                            is_group=0
                        )

                        facilitator.save()

                        return JsonResponse(
                            {'data': 'success', 'msg': 'You have successfully added the facilitator in the training',
                             'employee_name': facilitator.emp.pi.user.get_fullname,
                             'position': facilitator.emp.position.name})

                    else:
                        return JsonResponse({'error': True, 'msg': 'Facilitator already existed in the training.'})
            else:
                LdsFacilitator.objects.create(
                    is_external=1,
                    rp_name=request.POST.get('employee'),
                    rso_id=pk,
                    is_resource_person=0,
                    is_group=0
                )

                return JsonResponse(
                    {'data': 'success', 'msg': 'You have successfully added the external facilitator in the training'})
        except Exception as e:
            return JsonResponse({'error': True, 'msg': 'It seems that you inputted an invalid employee name.'})


@login_required
def generate_certificate_participants(request, pk):
    context = {
        'certificate_type': LdsCertificateType.objects.filter(type=0).order_by('keyword'),
        'rd': Designation.objects.filter(id=1).first(),
        'training': LdsRso.objects.filter(id=pk).first(),
        'participants': LdsParticipants.objects.filter(rso_id=pk)
    }
    # return render(request, 'frontend/lds/print_certificates_participants.html', context)
    return render(request, 'frontend/lds/print_cert_participants_new.html', context)


@login_required
def generate_certificate_facilitators(request, pk):
    context = {
        'certificate_type': LdsCertificateType.objects.filter(type=1).order_by('keyword'),
        'rd': Designation.objects.filter(id=1).first(),
        'training': LdsRso.objects.filter(id=pk).first(),
        'facilitators': LdsFacilitator.objects.filter(rso_id=pk)
    }
    # return render(request, 'frontend/lds/print_certificates_facilitators.html', context)
    return render(request, 'frontend/lds/print_cert_facilitators_new.html', context)


@login_required
def generate_certificate_of_appearance(request, pk):
    facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=0).order_by('emp__pi__user__last_name')
    ex_facilitator = LdsFacilitator.objects.filter(rso_id=pk, is_external=1)
    participant = LdsParticipants.objects.filter(rso_id=pk, type=0).order_by('emp__pi__user__last_name')
    ex_participant = LdsParticipants.objects.filter(rso_id=pk, type=1)
    participants_and_facilitators = []

    for row in facilitator:
        participants_and_facilitators.append({
            'employee_name': row.emp.pi.user.get_fullname,
            'section': row.emp.section.sec_acronym if row.emp.section.sec_acronym else "",
            'position': row.emp.position.name if row.emp.position.name else "",
            'sex': "Male" if row.emp.pi.gender == 1 else "Female",
            'email': row.emp.pi.user.email if row.emp.pi.user.email else "",
            'contact_number': row.emp.pi.mobile_no if row.emp.pi.mobile_no else ""
        })

    for row in ex_facilitator:
        participants_and_facilitators.append({
            'employee_name': row.rp_name,
            'section': "",
            'position': "",
            'sex': "",
            'email': "",
            'contact_number': ""
        })

    for row in participant:
        participants_and_facilitators.append({
            'employee_name': row.emp.pi.user.get_fullname,
            'section': row.emp.section.sec_acronym if row.emp.section.sec_acronym else "",
            'position': row.emp.position.name if row.emp.position.name else "",
            'sex': "Male" if row.emp.pi.gender == 1 else "Female",
            'email': row.emp.pi.user.email if row.emp.pi.user.email else "",
            'contact_number': row.emp.pi.mobile_no if row.emp.pi.mobile_no else ""
        })

    for row in ex_participant:
        participants_and_facilitators.append({
            'employee_name': row.participants_name,
            'section': "",
            'position': "",
            'sex': "",
            'email': "",
            'contact_number': ""
        })

    pagination = len(participants_and_facilitators)
    context = {
        'training': LdsRso.objects.filter(id=pk).first(),
        'pagination': math.ceil(float(pagination) / 2),
        'participants_and_facilitators': participants_and_facilitators,
        'rd': Designation.objects.filter(id=1).first(),
    }
    return render(request, 'frontend/lds/print_ca.html', context)


@login_required
@csrf_exempt
def tag_as_resource_person(request):
    if request.method == "POST":
        lds = LdsFacilitator.objects.filter(id=request.POST.get('id'))
        lds.update(
            is_resource_person=1
        )

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully tagged {} as resource person in this training.'.format(
                lds.first().rp_name if lds.first().rp_name else lds.first().emp.pi.user.get_fullname.upper()
            )})


@login_required
@csrf_exempt
def tag_as_group(request):
    if request.method == "POST":
        lds = LdsFacilitator.objects.filter(id=request.POST.get('id'))
        lds.update(
            is_group=1
        )

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully tagged {} as a group in this training.'.format(
                lds.first().rp_name if lds.first().rp_name else lds.first().emp.pi.user.get_fullname.upper()
            )})


@login_required
@csrf_exempt
def remove_tag_as_group(request):
    if request.method == "POST":
        lds = LdsFacilitator.objects.filter(id=request.POST.get('id'))
        lds.update(
            is_group=0
        )

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully remove the tag {} as a group in this training.'.format(
                lds.first().rp_name if lds.first().rp_name else lds.first().emp.pi.user.get_fullname.upper()
            )})


@login_required
@csrf_exempt
def delete_participants(request):
    if request.method == "POST":
        lds = LdsParticipants.objects.filter(id=request.POST.get('pk'))
        name = lds.first().participants_name if lds.first().participants_name else lds.first().emp.pi.user.get_fullname.upper()
        lds.delete()

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully deleted {} as participants in this training.'.format(
                name
            )})


@login_required
@csrf_exempt
def delete_facilitator(request):
    if request.method == "POST":
        LdsFacilitator.objects.filter(id=request.POST.get('pk')).delete()

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully deleted the facilitator / resource person.'})


@login_required
@csrf_exempt
def remove_tag_as_resource_person(request):
    if request.method == "POST":
        LdsFacilitator.objects.filter(id=request.POST.get('id')).update(
            is_resource_person=0
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully remove the tag as resource person'})


def certificate_authenticity(request, pk_training, pk_id):
    context = {
        'training': LdsRso.objects.annotate(hash_training_id=SHA1('id')).filter(
            hash_training_id=pk_training
        ).first(),
        'employee': Empprofile.objects.annotate(hash_id=SHA1('id')).filter(
            hash_id=pk_id
        ).first()
    }
    return render(request, 'frontend/lds/certificate_authenticity.html', context)


@login_required
def idp(request):
    if request.method == "POST":
        check = LdsIDP.objects.filter(emp=request.session['emp_id'], year=request.POST.get('year'))
        if not check:
            LdsIDP.objects.create(
                emp_id=request.session['emp_id'],
                year=request.POST.get('year'),
                aim=request.POST.get('aim')
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully created an Individual'
                                                           ' Development Plan for the year {}. You can now update'
                                                           ' the contents of your Individual Development Plan by'
                                                           ' clicking the details on the table.'.format(
                request.POST.get('year'))})
        else:
            return JsonResponse({'error': True,
                                 'msg': 'You have already created an Individual Development Plan for the year {}'.format(
                                     request.POST.get('year'))})
    context = {
        'title': 'learning_and_development',
        'sub_title': 'lds_idp',
        'year': datetime.today().year + 1
    }
    return render(request, 'frontend/lds/idp/idp.html', context)


@login_required
def update_idp_details(request, pk):
    if request.method == "POST":
        LdsIDP.objects.filter(id=pk).update(
            year=request.POST.get('year'),
            aim=request.POST.get('aim')
        )

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully updated your Individual Development Plan'})
    context = {
        'idp': LdsIDP.objects.filter(id=pk).first(),
    }
    return render(request, 'frontend/lds/idp/update_idp_details.html', context)


@login_required
def print_idp(request, pk):
    context = {
        'idp': LdsIDP.objects.filter(id=pk).first(),
        'job_requirements': LdsIDPContent.objects.filter(idp_id=pk, type_id=1),
        'core_leadership': LdsIDPContent.objects.filter(idp_id=pk, type_id=2),
        'functional_tasks': LdsIDPContent.objects.filter(idp_id=pk, type_id=3),
        'managerial_leadership': LdsIDPContent.objects.filter(idp_id=pk, type_id=4),
    }
    return render(request, 'frontend/lds/idp/print_idp.html', context)


@login_required
@csrf_exempt
def duplicate_idp_contents(request):
    if request.method == "POST":
        idp = LdsIDP.objects.filter(id=request.POST.get('pk')).first()
        idp_data = LdsIDP(
            emp_id=request.session['emp_id'],
            year="{} (Copy)".format(idp.year),
            aim=idp.aim,
        )

        idp_data.save()
        contents = LdsIDPContent.objects.filter(idp_id=request.POST.get('pk'))

        for row in contents:
            LdsIDPContent.objects.create(
                type_id=row.type_id,
                title=row.title,
                cc_level=row.cc_level,
                target_level=row.target_level,
                intervention=row.intervention,
                target_date=row.target_date,
                results=row.results,
                remarks=row.remarks,
                idp_id=idp_data.id
            )

        return JsonResponse(
            {'data': 'success', 'msg': 'You have successfully duplicated your Individual Development Plan'})


@login_required
def update_idp_contents(request, pk):
    idp = LdsIDP.objects.filter(id=pk).first()
    if request.method == "POST":
        jr_title = request.POST.getlist('jr_title[]')
        jr_cc_level = request.POST.getlist('jr_cc_level[]')
        jr_target_level = request.POST.getlist('jr_target_level[]')
        jr_intervention = request.POST.getlist('jr_intervention[]')
        jr_target_date = request.POST.getlist('jr_target_date[]')
        jr_results = request.POST.getlist('jr_results[]')
        jr_remarks = request.POST.getlist('jr_remarks[]')

        jr_data = [
            {'title': t, 'cc_level': cl, 'target_level': tl, 'intervention': i, 'target_date': td,
             'results': r, 'remarks': rem
             }
            for t, cl, tl, i, td, r, rem in zip(
                jr_title, jr_cc_level, jr_target_level, jr_intervention, jr_target_date, jr_results, jr_remarks
            )
        ]

        jr_check = LdsIDPContent.objects.filter(idp_id=pk, type_id=1)
        jr_store = [row.id for row in jr_check]
        if jr_check:
            y = 1
            x = 0
            for row in jr_data:
                if y > len(jr_check):
                    LdsIDPContent.objects.create(
                        type_id=1,
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                        idp_id=pk
                    )
                else:
                    LdsIDPContent.objects.filter(id=jr_store[x]).update(
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                    )
                    y += 1
                    x += 1
        else:
            for row in jr_data:
                LdsIDPContent.objects.create(
                    type_id=1,
                    title=row['title'],
                    cc_level=row['cc_level'],
                    target_level=row['target_level'],
                    intervention=row['intervention'],
                    target_date=row['target_date'],
                    results=row['results'],
                    remarks=row['remarks'],
                    idp_id=pk
                )

        # CMC IDP CONTENTS
        cmc_title = request.POST.getlist('cmc_title[]')
        cmc_cc_level = request.POST.getlist('cmc_cc_level[]')
        cmc_target_level = request.POST.getlist('cmc_target_level[]')
        cmc_intervention = request.POST.getlist('cmc_intervention[]')
        cmc_target_date = request.POST.getlist('cmc_target_date[]')
        cmc_results = request.POST.getlist('cmc_results[]')
        cmc_remarks = request.POST.getlist('cmc_remarks[]')

        cmc_data = [
            {'title': t, 'cc_level': cl, 'target_level': tl, 'intervention': i, 'target_date': td,
             'results': r, 'remarks': rem
             }
            for t, cl, tl, i, td, r, rem in zip(
                cmc_title, cmc_cc_level, cmc_target_level, cmc_intervention, cmc_target_date, cmc_results, cmc_remarks
            )
        ]

        cmc_check = LdsIDPContent.objects.filter(idp_id=pk, type_id=2)
        cmc_store = [row.id for row in cmc_check]
        if cmc_check:
            y = 1
            x = 0
            for row in cmc_data:
                if y > len(cmc_check):
                    LdsIDPContent.objects.create(
                        type_id=2,
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                        idp_id=pk
                    )
                else:
                    LdsIDPContent.objects.filter(id=cmc_store[x]).update(
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                    )
                    y += 1
                    x += 1
        else:
            for row in cmc_data:
                LdsIDPContent.objects.create(
                    type_id=2,
                    title=row['title'],
                    cc_level=row['cc_level'],
                    target_level=row['target_level'],
                    intervention=row['intervention'],
                    target_date=row['target_date'],
                    results=row['results'],
                    remarks=row['remarks'],
                    idp_id=pk
                )

        # MLS IDP CONTENTS
        mls_title = request.POST.getlist('mls_title[]')
        mls_cc_level = request.POST.getlist('mls_cc_level[]')
        mls_target_level = request.POST.getlist('mls_target_level[]')
        mls_intervention = request.POST.getlist('mls_intervention[]')
        mls_target_date = request.POST.getlist('mls_target_date[]')
        mls_results = request.POST.getlist('mls_results[]')
        mls_remarks = request.POST.getlist('mls_remarks[]')

        mls_data = [
            {'title': t, 'cc_level': cl, 'target_level': tl, 'intervention': i, 'target_date': td,
             'results': r, 'remarks': rem
             }
            for t, cl, tl, i, td, r, rem in zip(
                mls_title, mls_cc_level, mls_target_level, mls_intervention, mls_target_date, mls_results,
                mls_remarks
            )
        ]

        mls_check = LdsIDPContent.objects.filter(idp_id=pk, type_id=4)
        mls_store = [row.id for row in mls_check]
        if mls_check:
            y = 1
            x = 0
            for row in mls_data:
                if y > len(mls_check):
                    LdsIDPContent.objects.create(
                        type_id=4,
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                        idp_id=pk
                    )
                else:
                    LdsIDPContent.objects.filter(id=mls_store[x]).update(
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                    )
                    y += 1
                    x += 1
        else:
            for row in mls_data:
                LdsIDPContent.objects.create(
                    type_id=4,
                    title=row['title'],
                    cc_level=row['cc_level'],
                    target_level=row['target_level'],
                    intervention=row['intervention'],
                    target_date=row['target_date'],
                    results=row['results'],
                    remarks=row['remarks'],
                    idp_id=pk
                )

        # FT IDP CONTENTS
        ft_title = request.POST.getlist('ft_title[]')
        ft_cc_level = request.POST.getlist('ft_cc_level[]')
        ft_target_level = request.POST.getlist('ft_target_level[]')
        ft_intervention = request.POST.getlist('ft_intervention[]')
        ft_target_date = request.POST.getlist('ft_target_date[]')
        ft_results = request.POST.getlist('ft_results[]')
        ft_remarks = request.POST.getlist('ft_remarks[]')

        ft_data = [
            {'title': t, 'cc_level': cl, 'target_level': tl, 'intervention': i, 'target_date': td,
             'results': r, 'remarks': rem
             }
            for t, cl, tl, i, td, r, rem in zip(
                ft_title, ft_cc_level, ft_target_level, ft_intervention, ft_target_date, ft_results,
                ft_remarks
            )
        ]

        ft_check = LdsIDPContent.objects.filter(idp_id=pk, type_id=3)
        ft_store = [row.id for row in ft_check]
        if ft_check:
            y = 1
            x = 0
            for row in ft_data:
                if y > len(ft_check):
                    LdsIDPContent.objects.create(
                        type_id=3,
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                        idp_id=pk
                    )
                else:
                    LdsIDPContent.objects.filter(id=ft_store[x]).update(
                        title=row['title'],
                        cc_level=row['cc_level'],
                        target_level=row['target_level'],
                        intervention=row['intervention'],
                        target_date=row['target_date'],
                        results=row['results'],
                        remarks=row['remarks'],
                    )
                    y += 1
                    x += 1
        else:
            for row in ft_data:
                LdsIDPContent.objects.create(
                    type_id=3,
                    title=row['title'],
                    cc_level=row['cc_level'],
                    target_level=row['target_level'],
                    intervention=row['intervention'],
                    target_date=row['target_date'],
                    results=row['results'],
                    remarks=row['remarks'],
                    idp_id=pk
                )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated your Individual Development Plan'
                                                       ' for the year {}'.format(idp.year)})

    jr = PortalConfiguration.objects.filter(key_name='Job Requirements').first()
    job_requirements = [row.strip() for row in jr.key_acronym.split(',')]

    cc = PortalConfiguration.objects.filter(key_name='Core Competencies').first()
    core_competencies = [row.strip() for row in cc.key_acronym.split(',')]

    mls = PortalConfiguration.objects.filter(key_name='Managerial / Leadership Competencies').first()
    managerial_leadership = [row.strip() for row in mls.key_acronym.split(',')]

    for row in job_requirements:
        check = LdsIDPContent.objects.filter(idp_id=pk, type_id=1, title=row)
        if not check:
            LdsIDPContent.objects.create(
                title=row,
                type_id=1,
                idp_id=pk
            )

    for row in core_competencies:
        check = LdsIDPContent.objects.filter(idp_id=pk, type_id=2, title=row)
        if not check:
            LdsIDPContent.objects.create(
                title=row,
                type_id=2,
                idp_id=pk
            )

    for row in managerial_leadership:
        check = LdsIDPContent.objects.filter(idp_id=pk, type_id=4, title=row)
        if not check:
            LdsIDPContent.objects.create(
                title=row,
                type_id=4,
                idp_id=pk
            )

    context = {
        'title': 'learning_and_development',
        'sub_title': 'lds_idp',
        'idp': idp,
        'type': LdsIDPType.objects.order_by('order'),
    }
    return render(request, 'frontend/lds/idp/update_idp_contents.html', context)


@login_required
def view_idp_contents(request, pk):
    idp = LdsIDP.objects.filter(id=pk).first()

    context = {
        'idp': idp,
        'type': LdsIDPType.objects.order_by('order'),
        'job_requirements': LdsIDPContent.objects.filter(idp_id=pk, type_id=1),
        'core_leadership': LdsIDPContent.objects.filter(idp_id=pk, type_id=2),
        'managerial_leadership': LdsIDPContent.objects.filter(idp_id=pk, type_id=4),
        'functional_tasks': LdsIDPContent.objects.filter(idp_id=pk, type_id=3)
    }
    return render(request, 'frontend/lds/idp/load_idp_contents.html', context)


@login_required
@csrf_exempt
def remove_idp(request):
    LdsIDPContent.objects.filter(id=request.POST.get('pk')).delete()
    return JsonResponse(
        {'data': 'success', 'msg': 'You have successfully remove the content of your Individual Development Plan.'})
