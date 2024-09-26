from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.libraries.leave.forms import LeavetypeForm, LeavesubtypeForm, LeavespentForm
from backend.libraries.leave.models import LeaveType, LeaveSubtype, LeaveSpent, LeavePermissions
from backend.models import Empstatus
from backend.views import AjaxableResponseMixin


@login_required
@permission_required('admin.superadmin')
def leave_type(request):
    form = LeavetypeForm()
    if request.method == "POST":
        form = LeavetypeForm(request.POST)
        if form.is_valid():
            messages.success(request,
                             'The leave type {} was added successfully.'.format(form.cleaned_data['name']))
            form.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'leave_type': Paginator(LeaveType.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'leave',
        'sub_sub_title': 'leave_type'
    }
    return render(request, 'backend/libraries/leave/leave_type.html', context)


class LeavetypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/leave/update_leavetype.html'
    model = LeaveType
    form_class = LeavetypeForm
    success_url = reverse_lazy('leave_type')
    permission_required = 'admin.superadmin'


@login_required
@permission_required('admin.superadmin')
def leave_subtype(request):
    form = LeavesubtypeForm()
    if request.method == "POST":
        form = LeavesubtypeForm(request.POST)
        if form.is_valid():
            perm = request.POST.getlist('leave_permissions[]')

            form_id = form.save()
            for row in perm:
                LeavePermissions.objects.create(
                    empstatus_id=row,
                    leavesubtype_id=form_id.id
                )
            messages.success(request,
                             'The leave sub-type {} was added successfully.'.format(form.cleaned_data['name']))

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'leave_subtype': Paginator(LeaveSubtype.objects.filter(Q(name__icontains=search)).order_by('order'), rows).page(page),
        'rows': rows,
        'empstatus': Empstatus.objects.filter(status=1),
        'title': 'libraries',
        'sub_title': 'leave',
        'sub_sub_title': 'leave_subtype'
    }
    return render(request, 'backend/libraries/leave/leave_subtype.html', context)


class LeavesubtypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/leave/update_leavesubtype.html'
    model = LeaveSubtype
    form_class = LeavesubtypeForm
    success_url = reverse_lazy('leave_subtype')
    permission_required = 'admin.superadmin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empstatus'] = Empstatus.objects.filter(status=1)
        context['pk'] = self.object.id
        return context

    def form_valid(self, form):
        perm = self.request.POST.getlist('leave_permissions[]')
        data = [str(row.id) for row in
                LeavePermissions.objects.filter(leavesubtype_id=self.object.id)]
        comparison = list(set(perm) - set(data))
        form.save()
        LeavePermissions.objects.filter(leavesubtype_id=self.object.id).delete()

        for row in comparison:
            LeavePermissions.objects.create(empstatus_id=row, leavesubtype_id=self.object.id)

        return redirect('leave_subtype')


@login_required
@permission_required('admin.superadmin')
def leave_spent(request):
    form = LeavespentForm()
    if request.method == "POST":
        if request.method == "POST":
            form = LeavespentForm(request.POST)
            if form.is_valid():
                messages.success(request,
                                 'The leave spent {} was added successfully.'.format(form.cleaned_data['name']))
                form.save()
                return JsonResponse({'error': False})
            else:
                return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'leave_spent': Paginator(LeaveSpent.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'title': 'libraries',
        'sub_title': 'leave',
        'sub_sub_title': 'leave_spent'
    }
    return render(request, 'backend/libraries/leave/leave_spent.html', context)


class LeavespentUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/leave/update_leavespent.html'
    model = LeaveSpent
    form_class = LeavespentForm
    success_url = reverse_lazy('leave_spent')
    permission_required = 'admin.superadmin'




