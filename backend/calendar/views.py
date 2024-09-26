import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from backend.calendar.models import CalendarType, CalendarPermission
from backend.forms import DirectoryDetailTypeForm, CalendarTypeForm
from backend.models import DirectoryDetailType, Empprofile
from backend.views import AjaxableResponseMixin


@login_required
@permission_required('admin.superadmin')
def calendar_type(request):
    form = CalendarTypeForm
    if request.method == "POST":
        form = CalendarTypeForm(request.POST)
        if form.is_valid():
            calendartype = form.save(commit=False)
            calendartype.scope = True if request.POST.get('scope') == '1' or request.POST.get('scope') == 1 else False
            calendartype.upload_by_id = request.user.id
            messages.success(request, 'The calendar type {} was added successfully.'.format(form.cleaned_data['name']))
            calendartype.save()

            CalendarPermission.objects.create(
                type_id=calendartype.id,
                emp_id=request.user.id
            )
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(CalendarType.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'calendar',
        'sub_sub_title': 'type'
    }
    return render(request, 'backend/libraries/calendar/type.html', context)


@login_required
@permission_required('admin.superadmin')
def calendar_type_permissions(request, id):
    context = {
        'data': CalendarPermission.objects.filter(type_id=id),
        'type_id': id,
        'user_id': request.user.id,
    }
    return render(request, 'backend/libraries/calendar/permission.html', context)


@login_required
@permission_required('admin.superadmin')
def add_calendar_permissions(request):
    if request.method == "POST":
        user_id = re.split('\[|\]', request.POST.get('emp'))
        emp = Empprofile.objects.filter(id_number=user_id[1]).first()
        check = CalendarPermission.objects.filter(emp_id=emp.id, type_id=request.POST.get('type_id'))

        if check:
            pass
        else:
            CalendarPermission.objects.create(
                type_id=request.POST.get('type_id'),
                emp_id=emp.pi.user.id
            )
        return JsonResponse({'data': 'success', 'type_id': request.POST.get('type_id')})

    context = {
        'data': CalendarPermission.objects.filter(type_id=id),
        'type_id': id,
    }
    return render(request, 'backend/libraries/calendar/permission.html', context)


@login_required
@csrf_exempt
@permission_required('admin.superadmin')
def remove_calendar_permissions(request, id):
    if request.method == "POST":
        x = CalendarPermission.objects.filter(id=id).first()
        type_id = x.type_id
        CalendarPermission.objects.filter(id=id).delete()
        return JsonResponse({'data': 'success', 'type_id': type_id})
    return JsonResponse({'data': 'error'})


class CalendarTypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/calendar/type_update.html'
    model = CalendarType
    form_class = CalendarTypeForm
    success_url = reverse_lazy('calendar-type')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)
