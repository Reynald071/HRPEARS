from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.documents.models import Docs201Type, DocsIssuancesType
from backend.forms import SopClassForm, Docs201TypeForm, IssuancesTypeForm, DlClassForm
from backend.views import AjaxableResponseMixin
from frontend.models import DownloadableformsSopClass, DownloadableformsClass


@login_required
@permission_required('admin.superadmin')
def sop_class(request):
    form = SopClassForm()
    if request.method == "POST":
        form = SopClassForm(request.POST)
        if form.is_valid():
            doctypee = form.save(commit=False)
            doctypee.upload_by_id = request.user.id
            messages.success(request, 'The SOP classification {} was added successfully.'.format(form.cleaned_data['name']))
            doctypee.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(DownloadableformsSopClass.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'documents',
        'sub_sub_title': 'sop_class'
    }
    return render(request, 'backend/libraries/documents/sop_class.html', context)


class SopClassUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/documents/sop_class_update.html'
    model = DownloadableformsSopClass
    form_class = SopClassForm
    success_url = reverse_lazy('sop-class')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def dl_class(request):
    form = DlClassForm()
    if request.method == "POST":
        form = DlClassForm(request.POST)
        if form.is_valid():
            dlclass = form.save(commit=False)
            dlclass.upload_by_id = request.user.id
            dlclass.is_sop = False
            messages.success(request, 'The downloadable class {} was added successfully.'.format(form.cleaned_data['name']))
            dlclass.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(DownloadableformsClass.objects.filter(Q(name__icontains=search), Q(is_sop=False)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'documents',
        'sub_sub_title': 'dl_class'
    }
    return render(request, 'backend/libraries/documents/dl_class.html', context)


class DlClassUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/documents/dl_class_update.html'
    model = DownloadableformsClass
    form_class = DlClassForm
    success_url = reverse_lazy('dl-class')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def docs_201_type(request):
    form = Docs201TypeForm()
    if request.method == "POST":
        form = Docs201TypeForm(request.POST)
        if form.is_valid():
            doctypee = form.save(commit=False)
            doctypee.upload_by_id = request.user.id
            messages.success(request, 'The 201 document type {} was added successfully.'.format(form.cleaned_data['name']))
            doctypee.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Docs201Type.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'documents',
        'sub_sub_title': 'docs_201_type'
    }
    return render(request, 'backend/libraries/documents/docs_201_type.html', context)


class Docs201TypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/documents/docs_201_type_update.html'
    model = Docs201Type
    form_class = Docs201TypeForm
    success_url = reverse_lazy('docs-201-type')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def issuances_type(request):
    form = IssuancesTypeForm()
    if request.method == "POST":
        form = IssuancesTypeForm(request.POST)
        if form.is_valid():
            doctypee = form.save(commit=False)
            doctypee.upload_by_id = request.user.id
            messages.success(request, 'The issuance type {} was added successfully.'.format(form.cleaned_data['name']))
            doctypee.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(DocsIssuancesType.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'documents',
        'sub_sub_title': 'issuances_type'
    }
    return render(request, 'backend/libraries/documents/issuances_type.html', context)


class IssuancesTypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/documents/issuances_type_update.html'
    model = DocsIssuancesType
    form_class = IssuancesTypeForm
    success_url = reverse_lazy('issuances-type')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)
