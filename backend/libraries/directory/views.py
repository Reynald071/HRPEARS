from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.forms import DirectoryDetailTypeForm
from backend.models import DirectoryDetailType
from backend.views import AjaxableResponseMixin


@login_required
@permission_required('admin.superadmin')
def detailtype(request):
    form = DirectoryDetailTypeForm()
    if request.method == "POST":
        form = DirectoryDetailTypeForm(request.POST)
        if form.is_valid():
            detailtype = form.save(commit=False)
            detailtype.upload_by_id = request.user.id
            messages.success(request, 'The detail type {} was added successfully.'.format(form.cleaned_data['type']))
            detailtype.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(DirectoryDetailType.objects.filter(Q(type__icontains=search)).order_by('type'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'directory',
        'sub_sub_title': 'detailtype'
    }
    return render(request, 'backend/libraries/directory/type.html', context)


class DirectoryDetailTypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/directory/type_update.html'
    model = DirectoryDetailType
    form_class = DirectoryDetailTypeForm
    success_url = reverse_lazy('detail-type')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)
