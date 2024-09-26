from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.iso.models import IsoForms


@login_required
def iso_forms(request):
    if request.method == "POST":
        iso_id = request.POST.get('iso_id')
        docnum = request.POST.get('document_no')
        title = request.POST.get('title')
        revision = request.POST.get('revision')
        remarks = request.POST.get('remarks')
        attachment = request.FILES.get('attachment')

        if iso_id == '':
            doesexist = IsoForms.objects.filter(Q(document_no=docnum), Q(is_deleted=0)).first()
            if doesexist:
                return JsonResponse({'error': True, 'data': docnum})
            else:
                form = IsoForms(
                    title=title,
                    document_no=docnum,
                    attachment=attachment,
                    uploaded_on=datetime.now(),
                    uploaded_by_id=request.session['emp_id'],
                    revision_no=revision,
                    is_active=1,
                    remarks=remarks,
                    is_deleted=0,
                )
                form.save()
                return JsonResponse({'error': False, 'data': docnum})
        else:
            form = IsoForms.objects.get(id=iso_id)
            if attachment:
                form.attachment = attachment
            form.title = title
            form.document_no = docnum
            form.revision_no = revision
            form.remarks = remarks
            form.uploaded_on = datetime.now()
            form.uploaded_by_id = request.session['emp_id']
            form.save()
            return JsonResponse({'error': False, 'data': docnum, 'method': 'update'})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    context = {
        'leave': Paginator(
            IsoForms.objects.filter(((Q(document_no__icontains=search) | Q(title__icontains=search)) |
                                     Q(remarks__icontains=search)), Q(is_deleted=0))
                .order_by('document_no', '-uploaded_on', 'id', 'title'), rows).page(page) if status == '' else Paginator(
            IsoForms.objects.filter(((Q(document_no__icontains=search) | Q(title__icontains=search)) |
                                     Q(remarks__icontains=search)), Q(is_active=status), Q(is_deleted=0))
                .order_by('document_no', '-uploaded_on', 'id', 'title'), rows).page(page),
        'title': 'isoforms',
        'management': True,
        'sub_title': 'isouploads'
    }
    return render(request, 'backend/iso/forms.html', context)


@login_required
@csrf_exempt
def delete_form(request, pk):
    IsoForms.objects.filter(Q(id=pk)).update(is_deleted=1)
    return JsonResponse({'data': 'success'})
