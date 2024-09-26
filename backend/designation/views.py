import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.forms import DesignationForm
from backend.models import Designation, Empprofile
from backend.views import AjaxableResponseMixin


@login_required
@permission_required("admin.superadmin")
def designation(request):
    form = DesignationForm(initial={'emp_id': None})
    if request.method == "POST":
        form = DesignationForm(request.POST, initial={'emp_id': None})
        if form.is_valid():
            badg = form.save(commit=False)
            if request.POST.get('emp_id') == '':
                badg.emp_id = None
            else:
                emp_id = re.split('\[|\]', request.POST.get('emp_id'))
                name = Empprofile.objects.values('id').filter(id_number=emp_id[1]).first()
                badg.emp_id = name['id']
            messages.success(request,
                             'Designation for {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'badges': Paginator(Designation.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'employees',
        'sub_sub_title': 'designation',
    }
    return render(request, 'backend/libraries/designation/designation.html', context)


class DesignationUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/designation/designation_update.html'
    model = Designation
    form_class = DesignationForm
    success_url = reverse_lazy('designation')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        if form.instance.emp_id == '':
            form.instance.emp_id = None
        else:
            emp_id = re.split('\[|\]', form.instance.emp_id)
            name = Empprofile.objects.values('id').filter(id_number=emp_id[1]).first()
            form.instance.emp_id = name['id']
        return super().form_valid(form)
