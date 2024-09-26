from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.documents.models import DtsDoctype
from backend.forms import DtsDoctypeForm
from backend.views import AjaxableResponseMixin


@login_required
@permission_required('admin.superadmin')
def doctype(request):
    form = DtsDoctypeForm()
    if request.method == "POST":
        form = DtsDoctypeForm(request.POST)
        if form.is_valid():
            doctypee = form.save(commit=False)
            doctypee.upload_by_id = request.user.id
            messages.success(request, 'The document type {} was added successfully.'.format(form.cleaned_data['name']))
            doctypee.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(DtsDoctype.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'tracking',
        'sub_sub_title': 'doctype'
    }
    return render(request, 'backend/libraries/tracking/type.html', context)


class DtsDoctypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/tracking/type_update.html'
    model = DtsDoctype
    form_class = DtsDoctypeForm
    success_url = reverse_lazy('doc-type')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)
