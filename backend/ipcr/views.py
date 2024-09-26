import re
from datetime import date, datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Avg, F, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from backend.documents.models import Docs201Files, DtsDocument, DtsDrn, DtsTransaction, DtsDivisionCc
from backend.ipcr.forms import Upload201AttachmentForm
from backend.ipcr.models import IPC_Rating
from backend.models import Empprofile, Empstatus, Designation, DRNTracker
from backend.views import generate_serial_string
from frontend.models import PortalConfiguration
from frontend.templatetags.tags import gamify, generateDRN


@login_required
@permission_required('auth.performance_manager')
def ipcr_encoding(request):
    if request.method == "POST":
        id_number = re.split('\[|\]', request.POST.get('employee'))
        emp = Empprofile.objects.values('id').filter(id_number=id_number[1]).first()

        check = IPC_Rating.objects.filter(emp_id=emp['id'], year=request.POST.get('year'), semester=request.POST.get('semester'))

        if not check:
            if request.FILES.get('attachment'):
                file = Docs201Files(
                    number_201_type_id=21,
                    emp_id=emp['id'],
                    file=request.FILES.get('attachment'),
                    year=request.POST.get('year'),
                    upload_by_id=request.session['emp_id'],
                    name="IPCR 1st Semester - {}".format(request.POST.get('year')) if request.POST.get('semester') == "1" else "IPCR 2nd Semester - {}".format(request.POST.get('year'))
                )

                file.save()

            IPC_Rating.objects.create(
                year=request.POST.get('year'),
                semester=request.POST.get('semester'),
                ipcr=request.POST.get('ipcr'),
                emp_id=emp['id'],
                file_id=file.id if request.FILES.get('attachment') else None
            )

            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'error': True, 'msg': 'IPC rating already exists.'})
    context = {
        'employment_status': Empstatus.objects.filter(status=1),
        'title': 'performance',
        'sub_title': 'ipcr_monitoring',
        'sub_sub_title': 'ipcr_encoding'
    }
    return render(request, 'backend/ipcr/ipcr_encoding.html', context)


@login_required
@permission_required('auth.performance_manager')
def ipcr_details(request, pk):
    if request.method == "POST":
        check = IPC_Rating.objects.filter(emp_id=request.POST.get('employee_id'), year=request.POST.get('year'),
                                          semester=request.POST.get('semester'))

        if check: # If no changes
            IPC_Rating.objects.filter(id=pk).update(
                year=request.POST.get('year'),
                semester=request.POST.get('semester'),
                ipcr=request.POST.get('ipcr'),
            )

            return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the IPC rating.'})
        else:
            check = IPC_Rating.objects.filter(emp_id=request.POST.get('employee_id'), year=request.POST.get('year'),
                                              semester=request.POST.get('semester'))

            if not check:
                IPC_Rating.objects.filter(id=pk).update(
                    year=request.POST.get('year'),
                    semester=request.POST.get('semester'),
                    ipcr=request.POST.get('ipcr'),
                )

                return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the IPC rating.'})
            else:
                return JsonResponse({'error': True, 'msg': 'IPC rating already exists.'})
    context = {
        'data': IPC_Rating.objects.filter(id=pk).first(),
    }
    return render(request, 'backend/ipcr/ipcr_details.html', context)


@login_required
@permission_required('auth.performance_manager')
def generate_ipcr_ranking(request):
    if request.method == "POST":
        rank = Empprofile.objects.annotate(
            avg_ipcr=Avg('ipc_rating__ipcr'),
            year=F('ipc_rating__year')
        ).filter(
            Q(empstatus_id=request.POST.get('employment_status')) &
            Q(year=request.POST.get('year'))
        ).order_by('-avg_ipcr', 'pi__user__last_name')

        employee_without_rank = Empprofile.objects.filter(
            ~Q(id__in=[row.id for row in rank]) &
            Q(empstatus_id=request.POST.get('employment_status'))
        ).order_by('pi__user__last_name')

        context = {
            'data': rank,
            'employee_without_rank': employee_without_rank,
            'year': request.POST.get('year'),
        }
        return render(request, 'backend/ipcr/ranking.html', context)


@login_required
@permission_required('auth.performance_manager')
def generate_drn_for_ipcr(request):
    if request.method == "POST":
        lasttrack = DtsDocument.objects.order_by('-id').first()
        track_num = generate_serial_string(lasttrack.tracking_no) if lasttrack else \
            generate_serial_string(None, 'DT')

        sender = Empprofile.objects.filter(id=request.session['emp_id']).first()
        emp = Empprofile.objects.filter(id=request.POST.get('emp_id')).first()

        document = DtsDocument(
            doctype_id=4,
            docorigin_id=2,
            sender=sender.pi.user.get_fullname,
            subject="Certificate of Performance Rating of {}".format(emp.pi.user.get_fullname),
            purpose="For Signature",
            document_date=datetime.now(),
            document_deadline=None,
            other_info="CY {}".format(request.POST.get('cy')),
            tracking_no=track_num,
            creator_id=request.session['emp_id'],
            drn=None
        )

        document.save()

        drn_data = DtsDrn(
            document_id=document.id,
            category_id=1,
            doctype_id=4,
            division_id=1,
            section_id=None
        )

        drn_data.save()

        generated_drn = generateDRN(document.id, drn_data.id, True)
        config = PortalConfiguration.objects.filter(key_name='COPR').first()

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

        DRNTracker.objects.create(
            drn=generated_drn,
            value=request.POST.get('cy'),
            emp_id=request.POST.get('emp_id')
        )

        gamify(11, request.session['emp_id'])
        return JsonResponse({'data': 'success', 'drn': generated_drn})


@login_required
@permission_required('auth.performance_manager')
def generate_performance_rating(request):
    id_number = re.split('\[|\]', request.POST.get('employee'))
    emp = Empprofile.objects.filter(id_number=id_number[1]).first()

    start_year = request.POST.get('start_year')
    end_year = request.POST.get('end_year')

    year = []
    for row in range(int(start_year), int(end_year) + 1):
        year.append(row)

    context = {
        'today': date.today(),
        'signatory': Designation.objects.filter(id=3).first(),
        'year': year,
        'cy': "{}".format(start_year) if start_year == end_year else "{} - {}".format(start_year, end_year),
        'emp': emp
    }
    return render(request, 'backend/ipcr/performance_rating.html', context)


@login_required
@permission_required('auth.performance_manager')
def update_performance_rating_drn(request):
    if request.method == "POST":
        check = DRNTracker.objects.filter(value=request.POST.get('pk'), emp_id=request.POST.get('emp_id'))
        print(request.POST.get('pk'), request.POST.get('emp_id'))
        if not check:
            DRNTracker.objects.create(
                drn=request.POST.get('drn'),
                value=request.POST.get('pk'),
                emp_id=request.POST.get('emp_id')
            )
        else:
            check.update(
                drn=request.POST.get('drn')
            )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the DRN.'})


@login_required
@permission_required('auth.performance_manager')
def ipcr_file(request, pk):
    check = IPC_Rating.objects.filter(id=pk)

    if not check:
        obj = get_object_or_404(Docs201Files, pk=pk)
        form = Upload201AttachmentForm(request.POST, request.FILES, instance=obj)
    else:
        data = check.first()
        attachment = Docs201Files.objects.filter(number_201_type=21, emp_id=data.emp_id)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.upload_by_id = request.session['emp_id']
            data.save()
            form.save()
            return JsonResponse({'data': 'success', 'msg': 'You have successfully uploaded the attachment.'})

    context = {
        'form': form if not check else None,
        'data': data if check else None,
        'attachment': attachment if check else None,
        'pk': pk
    }
    return render(request, 'backend/ipcr/ipcr_file.html', context)


@login_required
@permission_required('auth.performance_manager')
def select_ipcr_file(request, pk):
    if request.method == "POST":
        IPC_Rating.objects.filter(id=pk).update(
            file_id=request.POST.get('file')
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully attached the attachment on the rating.'})


@permission_required('auth.performance_manager')
def ipcr_certification(request):
    context = {
        'title': 'performance',
        'sub_title': 'ipcr_certification',
    }
    return render(request, 'backend/ipcr/ipcr_certification.html', context)
