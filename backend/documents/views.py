import re
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1

from backend.documents.models import Docs201Files, Docs201Type, DocsIssuancesType, DocsIssuancesFiles
from backend.models import Empprofile


@login_required
@permission_required('auth.file_uploading')
def documents_201_files(request):
    context = {
        'management': True,
        'tab_title': '201 File Management',
        'title': 'file',
        'sub_sub_title': '201_files',
    }
    return render(request, 'backend/documents/documents_201_files.html', context)


@login_required
@permission_required('auth.file_uploading')
def documents_201_content(request, employee_id_number):
    employee = Empprofile.objects.filter(id_number=employee_id_number).first()
    context = {
        'management': True,
        'tab_title': '201 File Management',
        'title': 'file',
        'sub_sub_title': '201_files',
        'type': Docs201Type.objects.filter(status=1).order_by('name'),
        'employee': employee
    }
    return render(request, 'backend/documents/document_201_content.html', context)


@login_required
@permission_required('auth.file_uploading')
def upload_201_documents(request):
    if request.method == "POST":
        file = request.FILES.get('file')

        Docs201Files.objects.create(
            number_201_type_id=request.POST.get('document-type-id'),
            name=request.POST.get('name'),
            emp_id=request.POST.get('emp_id'),
            file=file,
            year=request.POST.get('year'),
            upload_by_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success'})


def separate_text_number(s):
    # Use regex to match all numbers and all non-numbers, excluding underscores
    numbers = ''.join(re.findall(r'\d+', s))
    text = ''.join(re.findall(r'[^\d_]+', s))
    return text, numbers


@login_required
@permission_required('auth.file_uploading')
def upload_multiple_201_documents(request):
    if request.method == "POST":
        file = request.FILES.getlist('multiple_file[]')

        for row in file:
            filename, year = separate_text_number(row.name)
            Docs201Files.objects.create(
                number_201_type_id=request.POST.get('multiple-document-type-id'),
                name=filename,
                emp_id=request.POST.get('multiple_emp_id'),
                file=row,
                year=year if year else None,
                upload_by_id=request.session['emp_id']
            )

        return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.file_uploading')
def delete_all_201_documents(request):
    if request.method == "POST":
        Docs201Files.objects.filter(
            number_201_type_id=request.POST.get('multiple-document-type-id'),
            emp_id=request.POST.get('multiple_emp_id')
        ).delete()

        doc_type = Docs201Type.objects.filter(id=request.POST.get('multiple-document-type-id')).first()
        return JsonResponse({'data': 'success', 'msg': "All files associated with the document type '{}' have been successfully removed".format(
            doc_type.name
        )})


@login_required
@permission_required('auth.file_uploading')
def update_201_files(request):
    if request.method == "POST":
        Docs201Files.objects.filter(id=request.POST.get('edit-id')).update(
            name=request.POST.get('edit-filename'),
            year=request.POST.get('edit-year'),
        )
        return JsonResponse({'data': 'success', 'msg': 'You have successfully edited the 201 file.'})


@login_required
@csrf_exempt
@permission_required('auth.file_uploading')
def delete_201_file_upload(request):
    if request.method == "POST":
        Docs201Files.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.file_uploading')
def delete_multiple_201_documents(request):
    if request.method == "POST":
        marked_files = request.POST.getlist('markedFiles[]')
        for row in marked_files:
            Docs201Files.objects.filter(id=row).delete()
        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.file_uploading')
def issuances(request):
    context = {
        'issuances_type': DocsIssuancesType.objects.filter(status=1).order_by('name'),
        'management': True,
        'title': 'file',
        'sub_sub_title': 'issuances'
    }
    return render(request, 'backend/documents/issuances.html', context)


@login_required
@csrf_exempt
@permission_required('auth.file_uploading')
def upload_issuances(request, type_id):
    if request.method == "POST":
        file = request.FILES.getlist('file[]')

        for row in file:
            DocsIssuancesFiles.objects.create(
                issuances_type_id=request.POST.get('type_id'),
                file=row,
                year=request.POST.get('year'),
                upload_by_id=request.session['emp_id']
            )

        return JsonResponse({'data': 'success'})

    context = {
        'type': DocsIssuancesType.objects.filter(id=type_id).first(),
        'files': DocsIssuancesFiles.objects.filter(issuances_type_id=type_id).order_by('-year'),
        'type_id': type_id
    }
    return render(request, 'backend/documents/issuances_uploading.html', context)


@login_required
@csrf_exempt
@permission_required('auth.file_uploading')
def delete_issuances_file_upload(request):
    if request.method == "POST":
        DocsIssuancesFiles.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})