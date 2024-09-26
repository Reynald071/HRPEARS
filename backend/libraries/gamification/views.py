from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.libraries.gamification.forms import GamifyLevelsForm, GamifyActivitiesForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from backend.libraries.gamification.models import GamifyLevels, GamifyActivities
from backend.views import AjaxableResponseMixin


@login_required
@permission_required("admin.superadmin")
def gamify_levels(request):
    form = GamifyLevelsForm()
    if request.method == "POST":
        form = GamifyLevelsForm(request.POST, request.FILES)
        if form.is_valid():
            cs = form.save(commit=False)
            cs.upload_by_id = request.user.id
            messages.success(request, 'The level {} was added successfully.'.format(form.cleaned_data['name']))
            cs.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(GamifyLevels.objects.filter(Q(name__icontains=search)).order_by('value'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'gamification',
        'sub_sub_title': 'levels'
    }
    return render(request, 'backend/libraries/gamification/levels.html', context)


class GamifyLevelsUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/gamification/levels_update.html'
    model = GamifyLevels
    form_class = GamifyLevelsForm
    success_url = reverse_lazy('gamify-levels')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required("admin.superadmin")
def gamify_activities(request):
    form = GamifyActivitiesForm()
    if request.method == "POST":
        form = GamifyActivitiesForm(request.POST)
        if form.is_valid():
            cs = form.save(commit=False)
            cs.upload_by_id = request.user.id
            messages.success(request, 'The activity {} was added successfully.'.format(form.cleaned_data['activity']))
            cs.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(GamifyActivities.objects.filter(Q(activity__icontains=search)).order_by('activity'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'gamification',
        'sub_sub_title': 'activities'
    }
    return render(request, 'backend/libraries/gamification/activities.html', context)


class GamifyActivitiesUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/gamification/activities_update.html'
    model = GamifyActivities
    form_class = GamifyActivitiesForm
    success_url = reverse_lazy('gamify-activities')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)
