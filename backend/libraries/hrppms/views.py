from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.forms import FundsourceForm, AoaForm, ProjectForm, EmpstatusForm, PositionForm, AccessionForm, \
    SeparationForm
from backend.views import AjaxableResponseMixin
from backend.models import Fundsource, Aoa, Project, Empstatus, Position, HrppmsModeaccession, HrppmsModeseparation


@login_required
@permission_required('admin.superadmin')
def mode_accession(request):
    form = AccessionForm()
    if request.method == "POST":
        form = AccessionForm(request.POST)
        if form.is_valid():
            accession = form.save(commit=False)
            accession.uploadedby_id = request.user.id
            messages.success(request, 'The mode of accession {} was added successfully.'.format(form.cleaned_data['name']))
            accession.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'accession': Paginator(HrppmsModeaccession.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'modeaccess'
    }
    return render(request, 'backend/libraries/hrppms/mode_accession.html', context)


class mode_accessionUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/hrppms/mode_accession_update.html'
    model = HrppmsModeaccession
    form_class = AccessionForm
    success_url = reverse_lazy('mode-accession')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.uploadedby_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def mode_separation(request):
    form = SeparationForm()
    if request.method == "POST":
        form = SeparationForm(request.POST)
        if form.is_valid():
            separation = form.save(commit=False)
            separation.uploadedby_id = request.user.id
            messages.success(request, 'The mode of separation {} was added successfully.'.format(form.cleaned_data['name']))
            separation.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'separation': Paginator(HrppmsModeseparation.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'separation'
    }
    return render(request, 'backend/libraries/hrppms/mode_separations.html', context)


class mode_separationUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/hrppms/mode_separations_update.html'
    model = HrppmsModeseparation
    form_class = SeparationForm
    success_url = reverse_lazy('mode-separation')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.uploadedby_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def fundsource(request):
    form = FundsourceForm()
    if request.method == "POST":
        form = FundsourceForm(request.POST)
        if form.is_valid():
            fundsource = form.save(commit=False)
            fundsource.upload_by_id = request.user.id
            messages.success(request, 'The fund source {} was added successfully.'.format(form.cleaned_data['name']))
            fundsource.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'fundsource': Paginator(Fundsource.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'fundsource'
    }
    return render(request, 'backend/libraries/hrppms/fundsource.html', context)


class FundsourceUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/hrppms/fundsource_update.html'
    model = Fundsource
    form_class = FundsourceForm
    success_url = reverse_lazy('fundsource')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def aoa(request):
    form = AoaForm()
    if request.method == "POST":
        form = AoaForm(request.POST)
        if form.is_valid():
            aoa = form.save(commit=False)
            aoa.upload_by_id = request.user.id
            messages.success(request,
                             'The area of assignment {} was added successfully.'.format(form.cleaned_data['name']))
            aoa.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'aoa': Paginator(Aoa.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'aoa'
    }
    return render(request, 'backend/libraries/hrppms/aoa.html', context)


class AoaUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/hrppms/aoa_update.html'
    model = Aoa
    form_class = AoaForm
    success_url = reverse_lazy('aoa')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def project(request):
    form = ProjectForm()
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.upload_by_id = request.user.id
            messages.success(request,
                             'The project/program {} was added successfully.'.format(form.cleaned_data['name']))
            project.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'project': Paginator(Project.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'project'
    }
    return render(request, 'backend/libraries/hrppms/project.html', context)


class ProjectUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/hrppms/project_update.html'
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def empstatus(request):
    form = EmpstatusForm()
    if request.method == "POST":
        form = EmpstatusForm(request.POST)
        if form.is_valid():
            empstatus = form.save(commit=False)
            empstatus.upload_by_id = request.user.id
            messages.success(request,
                             'The employment status {} was added successfully.'.format(form.cleaned_data['name']))
            empstatus.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'empstatus': Paginator(Empstatus.objects.filter(Q(name__icontains=search) |
                                                        Q(acronym__icontains=search)).order_by('name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'empstatus'
    }
    return render(request, 'backend/libraries/hrppms/empstatus.html', context)


class EmpstatusUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/hrppms/empstatus_update.html'
    model = Empstatus
    form_class = EmpstatusForm
    success_url = reverse_lazy('empstatus')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def position(request):
    form = PositionForm()
    if request.method == "POST":
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.upload_by_id = request.user.id
            messages.success(request, 'The position {} was added successfully.'.format(form.cleaned_data['name']))
            position.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'position': Paginator(Position.objects.filter(Q(name__icontains=search) |
                                                      Q(acronym__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'position'
    }
    return render(request, 'backend//libraries/hrppms/position.html', context)


class PositionUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend//libraries/hrppms/position_update.html'
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy('position')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)

