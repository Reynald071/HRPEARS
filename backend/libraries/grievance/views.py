from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.forms import GrievanceClassificationForm, GrievanceMediaForm, GrievanceStatusForm
from backend.libraries.grievance.models import GrievanceClassification, GrievanceMedia, GrievanceStatus
from backend.views import AjaxableResponseMixin


@login_required
def classification(request):
    form = GrievanceClassificationForm()
    if request.method == "POST":
        form = GrievanceClassificationForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            messages.success(request,
                             'The classification {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': GrievanceClassificationForm,
        'data': Paginator(GrievanceClassification.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'grievance',
        'sub_sub_title': 'classification',
    }
    return render(request, 'backend/libraries/grievance/classification.html', context)


class GrievanceClassificationUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/grievance/classification_update.html'
    model = GrievanceClassification
    form_class = GrievanceClassificationForm
    success_url = reverse_lazy('grievance-classification')

    def form_valid(self, form):
        return super().form_valid(form)


@login_required
def media(request):
    form = GrievanceMediaForm()
    if request.method == "POST":
        form = GrievanceMediaForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            messages.success(request,
                             'The medium {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': GrievanceMediaForm,
        'data': Paginator(GrievanceMedia.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'grievance',
        'sub_sub_title': 'media',
    }
    return render(request, 'backend/libraries/grievance/media.html', context)


class GrievanceMediaUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/grievance/media_update.html'
    model = GrievanceMedia
    form_class = GrievanceMediaForm
    success_url = reverse_lazy('grievance-media')

    def form_valid(self, form):
        return super().form_valid(form)


@login_required
def status(request):
    form = GrievanceStatusForm()
    if request.method == "POST":
        form = GrievanceStatusForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            messages.success(request,
                             'The status {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': GrievanceStatusForm,
        'data': Paginator(GrievanceStatus.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'grievance',
        'sub_sub_title': 'status',
    }
    return render(request, 'backend/libraries/grievance/status.html', context)


class GrievanceStatusUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/grievance/status_update.html'
    model = GrievanceStatus
    form_class = GrievanceStatusForm
    success_url = reverse_lazy('grievance-status')

    def form_valid(self, form):
        return super().form_valid(form)
