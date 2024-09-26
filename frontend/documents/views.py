from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django_mysql.models.functions import SHA1

from backend.documents.models import Docs201Type, Docs201Files, DocsIssuancesFiles, DocsIssuancesType
from backend.forms import DownloadableForm
from frontend.models import DownloadableformsSopClass, Downloadableforms, DownloadableformsSopFileClass


@login_required
def files_201(request):
    context = {
        'tab_parent': 'Employee Data',
        'tab_title': '201 Files',
        'title': 'profile',
        'sub_title': 'f_201_files',
        'type': Docs201Type.objects.filter(status=1).order_by('name')
    }
    return render(request, 'frontend/documents/201_files.html', context)


@login_required
def display_201_files(request, hash_type):
    type = Docs201Type.objects.annotate(hash_type=SHA1('id')).filter(hash_type=hash_type).first()
    context = {
        'document_type': type,
        'tab_title': '201 Files'
    }
    return render(request, 'frontend/documents/display_201_files.html', context)


@login_required
def upload_user_document(request):
    if request.method == "POST":
        file = request.FILES.get('file')

        Docs201Files.objects.create(
            number_201_type_id=18,
            name=request.POST.get('name'),
            emp_id=request.session['emp_id'],
            file=file,
            year=request.POST.get('year'),
            upload_by_id=request.session['emp_id']
        )

        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
def delete_user_file_upload(request):
    if request.method == "POST":
        Docs201Files.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


def files_sop(request):
    form = DownloadableForm()
    if request.method == "POST":
        form = DownloadableForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request,
                             'The downloadable forms {} was added successfully.'.format(form.cleaned_data['title']))
            x = form.save()
            DownloadableformsSopFileClass.objects.create(
                sop_class_id=request.POST.get('classification'),
                downloadable_form_id=x.id
            )

    context = {
        'form': form,
        'tab_title': 'Standard Operating Procedures',
        'classification': DownloadableformsSopClass.objects.filter(Q(status=True)),
        'title': 'f_documents',
        'sub_title': 'downloadable_forms',
        'sub_sub_title': 'sop',
        'type': DownloadableformsSopClass.objects.filter(status=True).order_by('name')
    }
    return render(request, 'frontend/documents/sop.html', context)


@login_required
def display_sop_files(request, type_id):
    type = DownloadableformsSopClass.objects.filter(id=type_id).first()
    context = {
        'document_type': type,
        'files': DownloadableformsSopFileClass.objects.filter(sop_class_id=type_id).order_by('downloadable_form__title')
     }
    return render(request, 'frontend/documents/display_sop_files.html', context)


@login_required
def issuances(request):
    context = {
        'type': DocsIssuancesType.objects.filter(status=1).order_by('name'),
        'tab_title': 'Issuances',
        'title': 'issuances'
    }
    return render(request, 'frontend/documents/issuances.html', context)


@login_required
def issuances_files(request, type_id):
    type = DocsIssuancesType.objects.filter(id=type_id).first()
    context = {
        'type': type,
        'files': DocsIssuancesFiles.objects.filter(issuances_type_id=type_id).order_by('-year')
    }
    return render(request, 'frontend/documents/issuances_files.html', context)
