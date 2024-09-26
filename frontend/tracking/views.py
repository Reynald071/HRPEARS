import datetime
import json
import re
import pandas as pd
import matplotlib

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Value, Q, F
from django.db.models.functions import Concat, Upper
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from api.wiserv import send_notification
from backend.documents.models import DtsTransaction, DtsDoctype, DtsDocorigin, DtsDocument, DtsDivisionCc, DtsDrn, \
    DtsCategory, DtsDoctypeClass, DtsAttachment
from backend.models import Empprofile, Division, Section, AuthUserUserPermissions, Personalinfo, AuthUser
from backend.templatetags.tags import check_permission
from backend.views import generate_serial_string

from frontend.templatetags.tags import generateDRN, gamify


@login_required
def document_tracking(request):
    if request.method == 'POST':
        doctype_id = request.POST.get('doctype_id')
        docorigin_id = request.POST.get('docorigin_id')
        document_date = request.POST.get('document_date')
        document_deadline = request.POST.get('document_deadline')
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        purpose = request.POST.get('purpose')
        other_info = request.POST.get('other_info')
        trans_to_id = request.POST.get('trans_to_id')
        copy_to_divisions = request.POST.getlist('copy_to_divisions')
        carbon_copy = request.POST.getlist('carbon_copy')
        whattodo = request.POST.get('whattodo')
        whattodoc = request.POST.get('whattodo_c')
        transaction_id = request.POST.get('transaction_id')
        attachments = request.FILES.getlist('attachment')
        category = request.POST.get('category_id')
        forward_to = None

        drn = request.POST.get('drn_number')
        generated_drn = ''

        you = Empprofile.objects.get(id=request.session['emp_id'])
        division = you.section.div_id if you.section else None
        section = you.section.id if you.section else None

        with transaction.atomic():
            if trans_to_id:
                employee = re.split('\[|\]', trans_to_id)
                forward_to = Empprofile.objects.filter(id_number=employee[1]).first()
                forward_to_user = User.objects.filter(id=forward_to.pi.user.id).first()

            if whattodo:
                old = DtsTransaction.objects.filter(id=transaction_id)
                document = old.first().document
                if whattodo == "0":
                    # for file
                    old.update(
                        action_taken=request.POST.get('action_taken'),
                        trans_datecompleted=timezone.now(),
                        action=3
                    )
                    trans = DtsTransaction.objects.filter(id=transaction_id).first()
                else:
                    tds = old.order_by('-date_saved').first().trans_datestarted
                    # check if not document_custodian
                    if not check_permission(request.user, 'document_custodian'):
                        # if not, assign tracking number as the drn
                        generated_drn = old.first().document.tracking_no
                    else:
                        # if document_custodian, check if also document_custodian_pantawid
                        if check_permission(request.user, 'document_custodian_pantawid'):
                            # if user is also document_custodian_pantawid
                            if forward_to:
                                # check if recipient is also document_custodian_pantawid
                                if check_permission(forward_to_user, 'document_custodian_pantawid'):
                                    # if yes, do not generate drn and assign tracking number as drn
                                    generated_drn = old.first().document.tracking_no
                                else:
                                    # if no, generate drn and save
                                    generated_drn = old.first().document.drn
                            else:
                                generated_drn = old.first().document.tracking_no
                        # if not document_custodian_pantawid, generate drn and save
                        else:
                            generated_drn = old.first().document.drn

                    old.update(
                        action_taken=request.POST.get('action_taken'),
                        trans_datestarted=timezone.now() if not tds else tds,
                        trans_datecompleted=timezone.now()
                    )

                    trans = DtsTransaction.objects.create(
                        action=1,
                        trans_from_id=request.session['emp_id'],
                        trans_to_id=forward_to.id if forward_to else request.session['emp_id'],
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=old.first().document_id
                    )
                    message = "Good day, {}! A document with DRN {} has been forwarded to you. - The My PORTAL Team" \
                        .format(forward_to.pi.user.first_name, generateDRN(trans.document.id,
                                                                           trans.document.get_my_drn.id) if not generated_drn else generated_drn)
                    send_notification(message, forward_to.pi.mobile_no, request.session['emp_id'], forward_to.id)
            else:
                lasttrack = DtsDocument.objects.order_by('-id').first()
                track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                    generate_serial_string(None, 'DT')

                document = DtsDocument.objects.create(
                    doctype_id=doctype_id if doctype_id else None,
                    docorigin_id=docorigin_id,
                    sender=sender,
                    subject=subject,
                    purpose=purpose,
                    document_date=document_date,
                    document_deadline=document_deadline if document_deadline else None,
                    other_info=other_info,
                    tracking_no=track_num,
                    creator_id=request.session['emp_id'],
                    drn=drn if drn else None,
                )

                # Save points for creating DRN
                gamify(11, request.session['emp_id'])

                # check if not document_custodian
                if not check_permission(request.user, 'document_custodian'):
                    # if not, assign tracking number as the drn
                    generated_drn = track_num
                else:
                    # if document_custodian, check if also document_custodian_pantawid
                    if check_permission(request.user, 'document_custodian_pantawid'):
                        # if user is also document_custodian_pantawid
                        if forward_to:
                            # check if recipient is also document_custodian_pantawid
                            if check_permission(forward_to_user, 'document_custodian_pantawid'):
                                # if yes, do not generate drn and assign tracking number as drn
                                generated_drn = track_num
                            else:
                                # if no, generate drn and save
                                generated_drn = drn
                                if not generated_drn:
                                    c_drn = DtsDrn.objects.create(document=document, category_id=category,
                                                                  division_id=division,
                                                                  section_id=section, doctype_id=doctype_id)
                                    generated_drn = generateDRN(document.id, c_drn.id, True)
                        else:
                            generated_drn = track_num
                    # if not document_custodian_pantawid, generate drn and save
                    else:
                        generated_drn = drn
                        if not generated_drn:
                            c_drn = DtsDrn.objects.create(document=document, category_id=category, division_id=division,
                                                          section_id=section, doctype_id=doctype_id)
                            generated_drn = generateDRN(document.id, c_drn.id, True)

                if document:
                    for x in range(2):
                        trans = DtsTransaction.objects.create(
                            action=x,
                            trans_from_id=request.session['emp_id'],
                            trans_to_id=forward_to.id if forward_to else request.session['emp_id'],
                            trans_datestarted=None,
                            trans_datecompleted=None,
                            action_taken=None,
                            document_id=document.id
                        )
                    if whattodoc == "0":
                        old = document.get_latest_status
                        old.action = 3
                        old.action_taken = "For filing"
                        old.trans_datecompleted = timezone.now()
                        old.save()
                    if forward_to:
                        message = "Good day, {}! A document with DRN {} has been forwarded to you. - The Caraga " \
                                  "PORTAL Team".format(forward_to.pi.user.first_name,
                                                       generateDRN(trans.document.id,
                                                                   trans.document.get_my_drn.id) if not generated_drn else generated_drn)
                        send_notification(message, forward_to.pi.mobile_no, request.session['emp_id'], forward_to.id)

            for attachment in attachments:
                DtsAttachment.objects.create(
                    transaction_id=trans.id,
                    attachment=attachment,
                    uploaded_by_id=request.session['emp_id']
                )

            if copy_to_divisions:
                for div in copy_to_divisions:
                    DtsDivisionCc.objects.create(
                        document_id=document.id,
                        division_id=div
                    )

            if carbon_copy:
                for cc in carbon_copy:
                    DtsTransaction.objects.create(
                        action=4,
                        trans_from_id=request.session['emp_id'],
                        trans_to=Empprofile.objects.filter(id_number=cc).first(),
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=document.id
                    )
            return JsonResponse({'data': 'success', 'drn': drn if drn else generated_drn, 'id': document.id})

    if not check_permission(request.user, 'document_custodian'):
        permission = 'document_custodian_pantawid'
        divisions = Division.objects.all().filter(id=9).order_by('div_name')
    else:
        divisions = Division.objects.all().order_by('div_name')
        if check_permission(request.user, 'document_custodian_pantawid'):
            permission = 'document_custodian_pantawid,document_custodian'
        else:
            permission = 'document_custodian'
    permissions = AuthUserUserPermissions.objects.filter(permission__codename__in=permission.split(',')) \
        .values_list('user_id', flat=True)
    doc_controllers = Empprofile.objects.filter(Q(pi__user__is_active=1), Q(pi__user__id__in=permissions),
                                                ~Q(id=request.session['emp_id'])).annotate(
        fullname=Concat(Value('['), 'id_number', Value('] '), Upper('pi__user__first_name'), Value(' '),
                        Upper('pi__user__last_name'))).order_by('pi__user__last_name')

    context = {
        'tab_title': 'Document Tracking | Inbox',
        'title': 'document_tracking',
        'sub_title': 'inbox',
        'docclass': DtsDoctypeClass.objects.all().order_by('name'),
        'docorigin': DtsDocorigin.objects.all(),
        'doc_controllers': doc_controllers,
        'divisions': divisions,
        'category': DtsCategory.objects.all(),
        'current_user': (AuthUser.objects.get(id=request.user.id)).get_fullname
    }
    return render(request, 'frontend/tracking/document_tracking.html', context)


@login_required
def get_total_dt(request):
    queryset = list()
    queryset_count = list()
    inbox = DtsTransaction.objects.filter(trans_to=request.session['emp_id'], action__in=[1],
                                          document__is_blank=False)
    sentbox = DtsTransaction.objects.filter(trans_from=request.session['emp_id'], action__in=[0],
                                            document__is_blank=False)
    cc = DtsTransaction.objects.filter(trans_to=request.session['emp_id'], action__in=[4],
                                       document__is_blank=False)

    my_section_id = Empprofile.objects.filter(id=request.session['emp_id']).first().section_id
    sc = DtsTransaction.objects.filter(
        Q(trans_to__section_id=my_section_id), Q(action__in=[1, 2, 3]),
        ~Q(trans_to=request.session['emp_id']), ~Q(trans_from=request.session['emp_id']), Q(document__is_blank=False)
    )

    queryset.append(inbox)
    queryset.append(sentbox)
    queryset.append(cc)
    queryset.append(sc)
    total_archive = DtsDocument.objects.filter(is_blank=False).order_by('-date_saved').count()

    for q in queryset:
        uniquedata = list()
        uniquetransactions = list()
        for d in q:
            if check_permission(request.user, 'document_custodian'):
                if d.document_id not in uniquedata:
                    uniquedata.append(d.document_id)
                    uniquetransactions.append(d.id)
            else:
                if q == queryset[0]:
                    if d.document_id not in uniquedata:
                        uniquedata.append(d.document_id)
                        uniquetransactions.append(d.id)
                else:
                    if d.document_id not in uniquedata and not d.document.get_my_drn:
                        uniquedata.append(d.document_id)
                        uniquetransactions.append(d.id)
        queryset_count.append(DtsTransaction.objects.filter(Q(id__in=uniquetransactions)).count())

    return JsonResponse({'inbox': queryset_count[0], 'sentbox': queryset_count[1],
                         'cc': queryset_count[2], 'sc': queryset_count[3], 'archive': total_archive})


@login_required
def sentbox(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    data = DtsTransaction.objects.filter(
        Q(trans_from=request.session['emp_id']), Q(action__in=[0]), (
                Q(document__tracking_no__icontains=search) |
                Q(document__sender__icontains=search) |
                Q(document__subject__icontains=search) |
                Q(document__purpose__icontains=search)
        ), Q(document__is_blank=False)).order_by('-document__tracking_no')

    if status:
        latest_statuses = list()
        for d in data:
            if d.document.get_latest_status.action == int(status):
                latest_statuses.append(d.id)
        data = DtsTransaction.objects.filter(id__in=latest_statuses).order_by('-document__tracking_no')

    context = {
        'data': Paginator(data, rows).page(page),
        'tab_title': 'Document Tracking | Sentbox',
        'title': 'document_tracking',
        'sub_title': 'sentbox',
    }
    return render(request, 'frontend/tracking/sentbox.html', context)


@login_required
def carboncopy(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    division = Empprofile.objects.filter(id=request.session['emp_id']).first()
    if division.section:
        document_ids = list()
        data_division = DtsDivisionCc.objects.filter(division_id=division.section.div_id)
        for d in data_division:
            if d.document_id not in document_ids:
                document_ids.append(d.document_id)

        data = DtsTransaction.objects.filter(
            ((Q(trans_to=request.session['emp_id']) & Q(action__in=[4])) |
             (Q(document_id__in=document_ids) & Q(action__in=[0]))) & (
                    Q(document__tracking_no__icontains=search) |
                    Q(document__sender__icontains=search) |
                    Q(document__subject__icontains=search) |
                    Q(document__purpose__icontains=search)
            ), Q(document__is_blank=False)).order_by('-document__tracking_no')
        track_nums = list()
        for d in data:
            if d.document.tracking_no not in track_nums:
                track_nums.append(d.document.tracking_no)
        data = DtsTransaction.objects.filter(document__tracking_no__in=track_nums, action=0).order_by(
            '-document__tracking_no')
    else:
        data = DtsTransaction.objects.filter(
            Q(trans_to=request.session['emp_id']), Q(action__in=[4]), (
                    Q(document__tracking_no__icontains=search) |
                    Q(document__sender__icontains=search) |
                    Q(document__subject__icontains=search) |
                    Q(document__purpose__icontains=search)
            ), Q(document__is_blank=False)).order_by('-document__tracking_no')

    if status:
        latest_statuses = list()
        for d in data:
            if d.document.get_latest_status.action == int(status):
                latest_statuses.append(d.id)
        data = DtsTransaction.objects.filter(id__in=latest_statuses).order_by('-document__tracking_no')

    context = {
        'data': Paginator(data, rows).page(page),
        'tab_title': 'Document Tracking | Carbon Copy',
        'title': 'document_tracking',
        'sub_title': 'carbon_copy',
    }
    return render(request, 'frontend/tracking/carboncopy.html', context)


@login_required
def section_docs(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    my_section_id = Empprofile.objects.filter(id=request.session['emp_id']).first().section_id
    data = DtsTransaction.objects.filter(
        (Q(trans_to__section_id=my_section_id) | Q(trans_from__section_id=my_section_id)), Q(action__in=[1, 2, 3]), (
                Q(document__tracking_no__icontains=search) |
                Q(document__sender__icontains=search) |
                Q(document__subject__icontains=search) |
                Q(document__purpose__icontains=search)
        ), Q(document__is_blank=False)).order_by('-document__tracking_no')
    uniquedata = list()
    uniquetransactions = list()
    for d in data:
        if d.document_id not in uniquedata:
            uniquedata.append(d.document_id)
            uniquetransactions.append(d.id)
    data = DtsTransaction.objects.filter(
        (Q(trans_to__section_id=my_section_id) | Q(trans_from__section_id=my_section_id)),
        Q(action__in=[1, 2, 3]), Q(id__in=uniquetransactions), (
                Q(document__tracking_no__icontains=search) |
                Q(document__sender__icontains=search) |
                Q(document__subject__icontains=search) |
                Q(document__purpose__icontains=search)
        ), Q(document__is_blank=False)).order_by('-document__tracking_no')

    if status:
        latest_statuses = list()
        for d in data:
            if d.document.get_latest_status.action == int(status):
                latest_statuses.append(d.id)
        data = DtsTransaction.objects.filter(id__in=latest_statuses).order_by('-document__tracking_no')

    context = {
        'data': Paginator(data, rows).page(page),
        'tab_title': 'Document Tracking | Section Documents',
        'title': 'document_tracking',
        'sub_title': 'section_docs',
    }
    return render(request, 'frontend/tracking/section_docs.html', context)


@login_required
def view_document(request, pk, mark_as_received=1, received_in_behalf=0):
    data = DtsDocument.objects.filter(id=pk).first()
    if mark_as_received == 1:
        status = data.get_latest_status
        if status:
            # if status.trans_to_id == request.session['emp_id'] and not status.trans_datestarted:
            if received_in_behalf == 1:
                x = DtsTransaction.objects.filter(id=status.id)
                x.update(
                    trans_datestarted=timezone.now(),
                    action=2,
                    trans_to_id=request.session['emp_id'],
                    in_behalf_of=x.first().trans_to
                )
                message = "Good day, {}! Document {} was received by {} in your behalf. - The My PORTAL Team" \
                    .format(x.first().trans_to.pi.user.first_name,
                            generateDRN(x.first().document.id, x.first().document.get_my_drn.id))
                send_notification(message, x.first().trans_to.pi.mobile_no, request.session['emp_id'],
                                  x.first.trans_to.id)
            else:
                if status.trans_to_id == request.session['emp_id'] and not status.trans_datestarted:
                    DtsTransaction.objects.filter(id=status.id).update(
                        trans_datestarted=timezone.now(),
                        action=2
                    )

    # attachments = DtsAttachment.objects.filter(transaction__document_id=pk)
    # if not platform.system() == 'Linux':
    #     pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    #     file_path = "E:\\caraga-portal\\media\\document_tracking\\"
    # else:
    #     file_path = "opt/apps/portal/media/document_tracking/"
    # template = ""
    #
    # for attachment in attachments:
    #     extension = str(attachment.attachment).split(".")[-1]
    #
    #     if extension.lower() == "png" or extension.lower() == "jpeg" or extension.lower() == "jpg":
    #         text = pytesseract.image_to_string(Image.open(file_path + str(attachment.attachment).split("/")[1]), lang="eng").split()
    #         template += " ".join(text)
    #     elif extension.lower() == "pdf":
    #         pdf_path = attachment.attachment
    #
    #         pages = fitz.open(file_path + str(pdf_path).split("/")[1])
    #         for page in range(len(pages)):
    #             p = pages[page]
    #             for i, img in enumerate(p.get_images(), start = 1):
    #                 xref = img[0]
    #                 base_image = pages.extract_image(xref)
    #                 image_bytes = base_image["image"]
    #
    #                 image = Image.open(io.BytesIO(image_bytes))
    #                 text = pytesseract.image_to_string(image, lang="eng").split()
    #                 template += " ".join(text)
    #
    # DtsDocument.objects.filter(id=pk).update(extracted_text=template)

    context = {
        'data': data,
    }
    return render(request, 'frontend/tracking/view_document.html', context)


def get_section(request, pk):
    sections = Section.objects.filter(div_id=pk)
    json_list = []
    for row in sections:
        json_list.append({row.id: row.sec_name})
    return JsonResponse(json_list, safe=False)


def get_doctype(request, pk=None):
    doctypes = DtsDoctype.objects.filter(doctype_class_id=pk) if pk else None
    json_list = [] if pk else None
    if doctypes:
        for row in doctypes:
            json_list.append({row.id: row.name})
    return JsonResponse(json_list, safe=False)


@login_required
def my_drn(request):
    if request.method == 'POST':
        doctype_id = request.POST.get('doctype_id')
        document_date = request.POST.get('document_date')
        document_deadline = request.POST.get('document_deadline')
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        purpose = request.POST.get('purpose')
        other_info = request.POST.get('other_info')
        trans_to_id = request.POST.get('trans_to_id')
        copy_to_divisions = request.POST.getlist('copy_to_divisions')
        carbon_copy = request.POST.getlist('carbon_copy')
        whattodo = request.POST.get('whattodo')
        document_id = request.POST.get('document_id')
        category = request.POST.get('category_id')
        attachments = request.FILES.getlist('attachment')

        generated_drn = ''

        you = Empprofile.objects.get(id=request.session['emp_id'])
        division = you.section.div_id if you.section and not you.section.is_negligible else you.section.div_id
        section = you.section.id if you.section and not you.section.is_negligible else None

        with transaction.atomic():
            # get receiver id number
            if trans_to_id:
                employee = re.split('\[|\]', trans_to_id)
                forward_to = Empprofile.objects.filter(id_number=employee[1]).first()

            document = DtsDocument.objects.filter(id=document_id)
            # check what transaction the user is trying to do
            # this is a transaction to update a created DRN
            if whattodo:
                # update all the details of the document first
                document.update(
                    sender=sender,
                    subject=subject,
                    purpose=purpose,
                    document_date=document_date,
                    is_blank=False,
                    document_deadline=document_deadline if document_deadline else None,
                    other_info=other_info
                )

                if whattodo == "0":
                    # if the user is trying to file the document
                    trans = DtsTransaction.objects.create(
                        action=3,
                        trans_from_id=request.session['emp_id'],
                        trans_to_id=request.session['emp_id'],
                        trans_datestarted=timezone.now(),
                        trans_datecompleted=timezone.now(),
                        action_taken='For filing',
                        document_id=document.first().id
                    )
                else:
                    # if the user is trying to forward the document
                    DtsTransaction.objects.filter(action=0, document_id=document_id).update(
                        trans_to_id=forward_to.id,
                    )
                    trans = DtsTransaction.objects.create(
                        action=1,
                        trans_from_id=request.session['emp_id'],
                        trans_to_id=forward_to.id,
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=document.first().id
                    )
                    message = "Good day, {}! A document with DRN {} has been forwarded to you. - The My PORTAL Team" \
                        .format(forward_to.pi.user.first_name,
                                generateDRN(trans.document.id, trans.document.get_my_drn.id))
                    send_notification(message, forward_to.pi.mobile_no, request.session['emp_id'], forward_to.id)

                # save all attachments
                for attachment in attachments:
                    DtsAttachment.objects.create(
                        transaction_id=trans.id,
                        attachment=attachment,
                        uploaded_by_id=request.session['emp_id']
                    )

            # this is a transaction to create DRN only
            else:
                # generate tracking number
                lasttrack = DtsDocument.objects.order_by('-id').first()
                track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
                    generate_serial_string(None, 'DT')

                # create the blank document to be assigned the DRN to be created
                document = DtsDocument.objects.create(
                    doctype_id=doctype_id,
                    subject=subject,
                    docorigin_id=2,
                    tracking_no=track_num,
                    is_blank=True,
                    creator_id=request.session['emp_id'],
                )
                document = DtsDocument.objects.filter(id=document.id)

                # create DRN entries with blank series number
                c_drn = DtsDrn.objects.create(document=document.first(), category_id=category, division_id=division,
                                              section_id=section, doctype_id=doctype_id)

                # update created DRN with the correct series number
                generated_drn = generateDRN(document.first().id, c_drn.id, True)

                if document:
                    # add the transaction
                    trans = DtsTransaction.objects.create(
                        action=0,
                        trans_from_id=request.session['emp_id'],
                        trans_to_id=request.session['emp_id'],
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=document.first().id
                    )

            # execute this if copies to specified divisions are to be sent
            if copy_to_divisions:
                for div in copy_to_divisions:
                    DtsDivisionCc.objects.create(
                        document_id=document.first().id,
                        division_id=div
                    )

            # execute this if carbon copies are to be sent to selected document custodians
            if carbon_copy:
                for cc in carbon_copy:
                    DtsTransaction.objects.create(
                        action=4,
                        trans_from_id=request.session['emp_id'],
                        trans_to=Empprofile.objects.filter(id_number=cc).first(),
                        trans_datestarted=None,
                        trans_datecompleted=None,
                        action_taken=None,
                        document_id=document.first().id
                    )

            return JsonResponse({'data': 'success', 'id': document.first().id, 'drn': generated_drn})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    data = DtsTransaction.objects.filter(
        Q(trans_to=request.session['emp_id']),
        Q(document__subject__icontains=search),
        Q(document__is_blank=True)).order_by('-document__tracking_no')
    uniquedata = list()
    uniquetransactions = list()
    for d in data:
        if d.document_id not in uniquedata:
            uniquedata.append(d.document_id)
            uniquetransactions.append(d.id)
    data = DtsTransaction.objects.filter(
        Q(trans_to=request.session['emp_id']),
        Q(id__in=uniquetransactions),
        Q(document__subject__icontains=search)
    ).order_by('-document__tracking_no')

    if status:
        latest_statuses = list()
        for d in data:
            if d.document.get_my_drn.doctype.doctype_class_id == int(status):
                latest_statuses.append(d.id)
        data = DtsTransaction.objects.filter(id__in=latest_statuses).order_by('-document__tracking_no')

    context = {
        'data': Paginator(data, rows).page(page),
        'tab_title': 'Document Tracking | My DRNs',
        'title': 'document_tracking',
        'sub_title': 'my_drn',
        'docclass': DtsDoctypeClass.objects.all().order_by('name'),
        'category': DtsCategory.objects.all()
    }
    return render(request, 'frontend/tracking/my_drn.html', context)


def format_timedelta(seconds):
    d, h, m, s = 0, 0, 0, 0
    d = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    h = seconds // 3600
    seconds %= 3600
    m = seconds // 60
    seconds %= 60
    s = seconds
    return "{} {} {} {}".format("{:.0f} day{},".format(d, 's' if d != 1 else '') if d > 0 else '',
                                "{:.0f} hour{},".format(h, 's' if h != 1 else '') if h > 0 else '',
                                "{:.0f} minute{},".format(m, 's' if m != 1 else '') if m > 0 else '',
                                "{:.0f} second{}".format(s, 's' if s != 1 else '') if s > 0 else '')


@login_required
def my_drn_summary(request):
    if request.method == 'POST':
        emp = Empprofile.objects.filter(pi__user__id=request.user.id).first()
        all_created = DtsTransaction.objects. \
            filter(Q(trans_from_id=emp.id) & Q(action=0) & ~Q(trans_to_id=emp.id) &
                   Q(date_saved__icontains=request.POST.get('summary-month')))
        all_received = DtsTransaction.objects. \
            filter(~Q(trans_from_id=emp.id) & Q(action=2) & Q(trans_to_id=emp.id) &
                   Q(date_saved__icontains=request.POST.get('summary-month')) &
                   ~Q(id__in=all_created.values_list('id', flat=True)))
        all_created_forwarded = DtsTransaction.objects. \
            filter(Q(trans_from_id=emp.id) & Q(action=2) & ~Q(trans_to_id=emp.id) &
                   Q(date_saved__icontains=request.POST.get('summary-month')))

        # For created by current user, grouped by document origin
        created_by_docorigin_output = [[], []]
        created_by_docorigin = None
        if all_created:
            created_by_docorigin = all_created.values('id', 'document__docorigin__name')
            for index, row in pd.DataFrame(
                    pd.DataFrame(list(created_by_docorigin)).groupby(['document__docorigin__name'])
                    ['document__docorigin__name'].count()).iterrows():
                created_by_docorigin_output[0].append(index)
                created_by_docorigin_output[1].append(row[0])

        # For created by current user, grouped by recipient divisions
        created_by_recipient_divisions_output = [[], []]
        created_by_recipient_divisions = None
        if all_created:
            created_by_recipient_divisions = all_created.values('id', 'trans_to__section__div__div_acronym')
            for index, row in pd.DataFrame(pd.DataFrame(list(created_by_recipient_divisions)) \
                                                   .groupby(['trans_to__section__div__div_acronym'])
                                           ['trans_to__section__div__div_acronym'].count()).iterrows():
                created_by_recipient_divisions_output[0].append(index)
                created_by_recipient_divisions_output[1].append(row[0])

        # For created by current user, grouped by document types
        created_by_document_types_output = [[], []]
        created_by_document_types = None
        if all_created:
            created_by_document_types = all_created.values('id', 'document__doctype__doctype_class__name')
            for index, row in pd.DataFrame(pd.DataFrame(list(created_by_document_types)) \
                                                   .groupby(['document__doctype__doctype_class__name'])
                                           ['document__doctype__doctype_class__name'].count()).iterrows():
                created_by_document_types_output[0].append(index.replace(' Records', ''))
                created_by_document_types_output[1].append(row[0])

        # For created by current user, grouped by actions
        created_by_actions_output = [[], []]
        created_by_actions = None
        if all_created:
            created_by_actions_total = 0
            created_by_actions = all_created_forwarded.values('id', 'trans_datecompleted')
            for index, row in pd.DataFrame(pd.DataFrame(list(created_by_actions)).notna()
                                                   .groupby(['trans_datecompleted'])['trans_datecompleted']
                                                   .count()).iterrows():
                created_by_actions_output[0].append('Acted' if index else 'Pending')
                created_by_actions_output[1].append(row[0])
                created_by_actions_total = created_by_actions_total + int(row[0])
            if created_by_actions_total < len(created_by_docorigin):
                created_by_actions_output[0].append('Unprocessed')
                created_by_actions_output[1].append(len(created_by_docorigin) - created_by_actions_total)

        # For received by current user, grouped by sending divisions
        received_by_sending_divisions_output = [[], []]
        received_by_sending_divisions = None
        if all_received:
            received_by_sending_divisions = all_received.values('id', 'trans_from__section__div__div_acronym')
            for index, row in pd.DataFrame(pd.DataFrame(list(received_by_sending_divisions)) \
                                                   .groupby(['trans_from__section__div__div_acronym'])
                                           ['trans_from__section__div__div_acronym'].count()).iterrows():
                received_by_sending_divisions_output[0].append(index)
                received_by_sending_divisions_output[1].append(row[0])

        # For received by current user, grouped by actions
        received_by_actions_output = [[], []]
        received_by_actions = None
        if all_received:
            received_by_actions = all_received.values('id', 'trans_datecompleted')
            for index, row in pd.DataFrame(pd.DataFrame(list(received_by_actions)).notna()
                                                   .groupby(['trans_datecompleted'])['trans_datecompleted']
                                                   .count()).iterrows():
                received_by_actions_output[0].append('Acted' if index else 'Pending')
                received_by_actions_output[1].append(row[0])

        # Calculate average process time for each document
        average_processing_time = datetime.timedelta(seconds=0)
        if all_received:
            average_processing_time_df = pd.DataFrame(
                list(all_received.values('trans_datestarted', 'trans_datecompleted')))
            average_processing_time_df['proc_time'] = average_processing_time_df['trans_datecompleted'] - \
                                                      average_processing_time_df['trans_datestarted']
            average_processing_time = average_processing_time_df['proc_time'].mean()

    context = {
        'created_by_docorigin_output': created_by_docorigin_output,
        'created_by_docorigin_count': len(created_by_docorigin) if created_by_docorigin else 0,
        'created_by_recipient_divisions_output': created_by_recipient_divisions_output,
        'created_by_recipient_divisions_count': len(created_by_recipient_divisions) if created_by_recipient_divisions else 0,
        'created_by_document_types_output': created_by_document_types_output,
        'created_by_document_types_count': len(created_by_document_types) if created_by_document_types else 0,
        'created_by_actions_output': created_by_actions_output,
        'created_by_actions_count': len(created_by_actions) if created_by_actions else 0,
        'received_by_sending_divisions_output': received_by_sending_divisions_output,
        'received_by_sending_divisions_count': len(received_by_sending_divisions) if received_by_sending_divisions else 0,
        'received_by_actions_output': received_by_actions_output,
        'received_by_actions_count': len(received_by_actions) if received_by_actions else 0,
        'average_processing_time': str(format_timedelta(average_processing_time.total_seconds())).strip()
    }
    return render(request, 'frontend/tracking/summary.html', context)


@login_required
def view_document_blank(request, pk):
    data = DtsDocument.objects.filter(id=pk).first()
    status = data.get_latest_status
    if status:
        if status.trans_to_id == request.session['emp_id'] and not status.trans_datestarted:
            DtsTransaction.objects.filter(id=status.id).update(
                trans_datestarted=timezone.now(),
                action=2
            )

    permission = 'document_custodian'
    permissions = AuthUserUserPermissions.objects.filter(permission__codename=permission) \
        .values_list('user_id', flat=True)
    doc_controllers = Empprofile.objects.filter(Q(pi__user__is_active=1), Q(pi__user__id__in=permissions),
                                                ~Q(id=request.session['emp_id'])).annotate(
        fullname=Concat(Value('['), 'id_number', Value('] '), Upper('pi__user__first_name'), Value(' '),
                        Upper('pi__user__last_name'))).order_by('pi__user__last_name')

    context = {
        'data': data,
        'docclass': DtsDoctypeClass.objects.all().order_by('name'),
        'doc_controllers': doc_controllers,
        'divisions': Division.objects.all().order_by('div_name'),
        'category': DtsCategory.objects.all()
    }
    return render(request, 'frontend/tracking/view_document_blank.html', context)


@login_required
@csrf_exempt
def delete_drn(request):
    if request.method == "POST":
        with transaction.atomic():
            a = DtsAttachment.objects.filter(transaction__document_id=request.POST.get('id'))
            a.delete()
            b = DtsTransaction.objects.filter(document_id=request.POST.get('id'))
            b.delete()
            c = DtsDrn.objects.filter(document_id=request.POST.get('id'))
            c.delete()
            d = DtsDocument.objects.filter(id=request.POST.get('id'))
            d.delete()
            return JsonResponse({'data': 'success'})
    return JsonResponse({'error': 'You are not authorized to perform this operation.'})


@login_required
def get_division_and_section(request, id_number):
    results = list()
    employee = Empprofile.objects.filter(id_number=id_number).first()
    section = ' {}'.format(employee.pi.user.get_section)
    division = employee.pi.user.get_division
    results.append(division)
    results.append(section)
    data = json.dumps(results)
    return HttpResponse(data, 'application/json')
