import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.documents.models import Docs201Type, Docs201Files
from backend.models import Empprofile


@login_required
def file_uploading(request):
    context = {
        'title': 'employee',
        'sub_title': 'file_uploading'
    }
    return render(request,'backend/employee_data/file_uploading/file_uploading.html', context)


@login_required
def file_uploading_content(request, employee_id_number):
    employee = Empprofile.objects.filter(id_number=employee_id_number).first()
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

    context = {
        'management': True,
        'tab_title': '201 File Management',
        'title': 'file',
        'sub_sub_title': '201_files',
        'type': Docs201Type.objects.filter(status=1).order_by('name'),
        'employee': employee
    }
    return render(request, 'backend/employee_data/file_uploading/file_uploading_content.html', context)


@login_required
@csrf_exempt
def file_uploading_delete(request):
    if request.method == "POST":
        Docs201Files.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
def file_uploading_update(request):
    if request.method == "POST":
        Docs201Files.objects.filter(id=request.POST.get('edit-id')).update(
            name=request.POST.get('edit-filename'),
            year=request.POST.get('edit-year'),
        )
        return JsonResponse({'data': 'success', 'msg': 'You have successfully edited the 201 file.'})


def separate_text_number(s):
    try:
        numbers = ''.join(re.findall(r'\d+', s))
        text = ''.join(re.findall(r'[^\d_]+', s))
        return text, numbers
    except Exception as e:
        return None, None


@login_required
def file_uploading_multiple(request):
    if request.method == "POST":
        files = request.FILES.getlist('multiple_file[]')

        for file in files:
            filename, year_str = separate_text_number(file.name)

            # Validate and convert year to integer, if possible
            try:
                year = int(year_str) if year_str.isdigit() and 1000 <= int(year_str) <= 9999 else None
            except ValueError:
                year = None  # Set year to None if conversion fails

            Docs201Files.objects.create(
                number_201_type_id=request.POST.get('multiple-document-type-id'),
                name=filename if filename else file.name,
                emp_id=request.POST.get('multiple_emp_id'),
                file=file,
                year=year,
                upload_by_id=request.session['emp_id']
            )

        return JsonResponse({'data': 'success'})


@login_required
def file_uploading_delete_all(request):
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
@csrf_exempt
def file_uploading_delete_marked(request):
    if request.method == "POST":
        marked_files = request.POST.getlist('markedFiles[]')
        for row in marked_files:
            Docs201Files.objects.filter(id=row).delete()
        return JsonResponse({'data': 'success'})

