import re

import textdistance
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from backend.forms import BloodtypeForm, CivilstatusForm, HobbiesForm, DegreeForm, EducationLevelForm, EligibilityForm, \
    HonorsForm, SchoolForm, BrgyForm, CityForm, ProvinceForm, CountriesForm, OrganizationForm, NonacadForm, \
    TrainingtitleForm, TrainingtypeForm
from backend.models import Position
from backend.views import AjaxableResponseMixin
from frontend.models import Bloodtype, Civilstatus, Hobbies, Degree, Educationlevel, Eligibility, Honors, School, Brgy, \
    City, Province, Countries, Organization, Nonacad, Trainingtitle, Trainingtype, Educationbackground, Voluntary, \
    Membership, Training, Civilservice, Workexperience, Skills, Recognition


@login_required
@permission_required("admin.superadmin")
def bloodtype(request):
    form = BloodtypeForm()
    if request.method == "POST":
        form = BloodtypeForm(request.POST)
        if form.is_valid():
            bt = form.save(commit=False)
            bt.upload_by_id = request.user.id
            messages.success(request, 'The blood type {} was added successfully.'.format(form.cleaned_data['name']))
            bt.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Bloodtype.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'descriptive',
        'sub_sub_title': 'bloodtype'
    }
    return render(request, 'backend/libraries/pis/bloodtype.html', context)


class BloodtypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/bloodtype_update.html'
    model = Bloodtype
    form_class = BloodtypeForm
    success_url = reverse_lazy('bloodtype')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required("admin.superadmin")
def civilstatus(request):
    form = CivilstatusForm()
    if request.method == "POST":
        form = CivilstatusForm(request.POST)
        if form.is_valid():
            cs = form.save(commit=False)
            cs.upload_by_id = request.user.id
            messages.success(request, 'The civil status {} was added successfully.'.format(form.cleaned_data['name']))
            cs.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Civilstatus.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'descriptive',
        'sub_sub_title': 'civilstatus'
    }
    return render(request, 'backend/libraries/pis/civilstatus.html', context)


class CivilstatusUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/civilstatus_update.html'
    model = Civilstatus
    form_class = CivilstatusForm
    success_url = reverse_lazy('civil-status')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def hobbies(request):
    form = HobbiesForm()
    if request.method == "POST":
        form = HobbiesForm(request.POST)
        if form.is_valid():
            check = Hobbies.objects.filter(hob_name=form.cleaned_data['hob_name'])
            if check:
                return JsonResponse({'error': True, 'msg': 'This hobby already exists.'})
            else:
                hob = form.save(commit=False)
                hob.pi_id = request.session['pi_id']
                messages.success(request,
                                 'The hobby {} was added successfully.'.format(form.cleaned_data['hob_name']))
                hob.save()
                return JsonResponse({'error': False})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Hobbies.objects.filter(Q(hob_name__icontains=search)).order_by('hob_name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'descriptive',
        'sub_sub_title': 'hobbies'
    }
    return render(request, 'backend/libraries/pis/hobbies.html', context)


class HobbiesUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/hobbies_update.html'
    model = Hobbies
    form_class = HobbiesForm
    success_url = reverse_lazy('hobbies')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def degree(request):
    form = DegreeForm()
    if request.method == "POST":
        form = DegreeForm(request.POST)
        if form.is_valid():
            check = Degree.objects.filter(degree_name=form.cleaned_data['degree_name'])
            if check:
                return JsonResponse({'msg': 'Degree with this Name already exists.'})
            else:
                degree = form.save(commit=False)
                degree.pi_id = request.user.id
                messages.success(request,
                                 'The countries {} was added successfully.'.format(form.cleaned_data['degree_name']))
                degree.save()
                return JsonResponse({'error': False})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Degree.objects.filter(Q(degree_name__icontains=search)).order_by('degree_name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'education',
        'sub_sub_title': 'degree',
        'model': Degree.objects.all()
    }
    return render(request, 'backend/libraries/pis/degree.html', context)


class DegreeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/degree_update.html'
    model = Degree
    form_class = DegreeForm
    success_url = reverse_lazy('degree')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def educationlevel(request):
    form = EducationLevelForm()
    if request.method == "POST":
        form = EducationLevelForm(request.POST)
        if form.is_valid():
            el = form.save(commit=False)
            el.upload_by_id = request.user.id
            messages.success(request,
                             'The education level {} was added successfully.'.format(form.cleaned_data['lev_name']))
            el.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Educationlevel.objects.filter(Q(lev_name__icontains=search)).order_by('lev_name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'education',
        'sub_sub_title': 'level'
    }
    return render(request, 'backend/libraries/pis/educationlevel.html', context)


class EducationlevelUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/educationlevel_update.html'
    model = Educationlevel
    form_class = EducationLevelForm
    success_url = reverse_lazy('educationlevel')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def eligibility(request):
    form = EligibilityForm()
    if request.method == "POST":
        form = EligibilityForm(request.POST)
        if form.is_valid():
            check = Eligibility.objects.filter(el_name=form.cleaned_data['el_name'])
            if check:
                return JsonResponse({'msg': 'This eligibility already exists.'})
            else:
                el = form.save(commit=False)
                el.pi_id = request.session['pi_id']
                messages.success(request,
                                 'The eligibility {} was added successfully.'.format(form.cleaned_data['el_name']))
                el.save()
                return JsonResponse({'error': False})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Eligibility.objects.filter(Q(el_name__icontains=search)).order_by('el_name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'education',
        'sub_sub_title': 'eligibility'
    }
    return render(request, 'backend/libraries/pis/eligibility.html', context)


class EligibilityUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/eligibility_update.html'
    model = Eligibility
    form_class = EligibilityForm
    success_url = reverse_lazy('eligibility')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def honors(request):
    form = HonorsForm()
    if request.method == "POST":
        form = HonorsForm(request.POST)
        if form.is_valid():
            check = Honors.objects.filter(hon_name=form.cleaned_data['hon_name'])
            if check:
                return JsonResponse({'msg': 'This honor already exists.'})
            else:
                el = form.save(commit=False)
                el.pi_id = request.session['pi_id']
                messages.success(request,
                                 'The honor {} was added successfully.'.format(form.cleaned_data['hon_name']))
                el.save()
                return JsonResponse({'error': False})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(Honors.objects.filter(Q(hon_name__icontains=search)).order_by('hon_name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'education',
        'sub_sub_title': 'honors'
    }
    return render(request, 'backend/libraries/pis/honors.html', context)


class HonorsUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/honors_update.html'
    model = Honors
    form_class = HonorsForm
    success_url = reverse_lazy('honors')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def school(request):
    form = SchoolForm()
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            check = School.objects.filter(school_name=form.cleaned_data['school_name'])
            if check:
                return JsonResponse({'msg': 'This school is already exists.'})
            else:
                school = form.save(commit=False)
                school.pi_id = request.session['pi_id']
                messages.success(request,
                                 'The school {} was added successfully.'.format(form.cleaned_data['school_name']))
                school.save()
                return JsonResponse({'error': False})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'data': Paginator(School.objects.filter(Q(school_name__icontains=search)).order_by('school_name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'education',
        'sub_sub_title': 'school'
    }
    return render(request, 'backend/libraries/pis/school.html', context)


class SchoolUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/school_update.html'
    model = School
    form_class = SchoolForm
    success_url = reverse_lazy('school')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def brgy(request):
    form = BrgyForm()
    if request.method == "POST":
        form = BrgyForm(request.POST)
        if form.is_valid():
            brgy = form.save(commit=False)
            brgy.upload_by_id = request.user.id
            messages.success(request, 'The city {} was added successfully.'.format(form.cleaned_data['name']))
            brgy.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'brgy': Paginator(Brgy.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'location',
        'sub_sub_title': 'brgy'
    }
    return render(request, 'backend/libraries/pis/brgy.html', context)


class BrgyUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/brgy_update.html'
    model = Brgy
    form_class = BrgyForm
    success_url = reverse_lazy('brgy')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def city(request):
    form = CityForm()
    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.save(commit=False)
            city.upload_by_id = request.user.id
            messages.success(request, 'The city {} was added successfully.'.format(form.cleaned_data['name']))
            city.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'city': Paginator(City.objects.filter(Q(name__icontains=search) |
                                              Q(prov_code__name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'location',
        'sub_sub_title': 'city'
    }
    return render(request, 'backend/libraries/pis/city.html', context)


class CityUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/city_update.html'
    model = City
    form_class = CityForm
    success_url = reverse_lazy('city')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def province(request):
    form = ProvinceForm()
    if request.method == "POST":
        form = ProvinceForm(request.POST)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.upload_by_id = request.user.id
            messages.success(request,
                             'The province {} was added successfully.'.format(form.cleaned_data['name']))
            prov.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'prov': Paginator(Province.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'location',
        'sub_sub_title': 'province'
    }
    return render(request, 'backend/libraries/pis/province.html', context)


class ProvinceUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/province_update.html'
    model = Province
    form_class = ProvinceForm
    success_url = reverse_lazy('province')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def countries(request):
    form = CountriesForm()
    if request.method == "POST":
        form = CountriesForm(request.POST)
        if form.is_valid():
            cs = form.save(commit=False)
            cs.upload_by_id = request.user.id
            messages.success(request, 'The countries {} was added successfully.'.format(form.cleaned_data['name']))
            cs.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'cs': Paginator(Countries.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'location',
        'sub_sub_title': 'countries'
    }
    return render(request, 'backend/libraries/pis/countries.html', context)


class CountryUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/country_update.html'
    model = Countries
    form_class = CountriesForm
    success_url = reverse_lazy('countries')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def organization(request):
    form = OrganizationForm()
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.pi_id = request.session['pi_id']
            messages.success(request,
                             'The organization {} was added successfully.'.format(form.cleaned_data['org_name']))
            org.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'org': Paginator(Organization.objects.filter(Q(org_name__icontains=search)).order_by('org_name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'others',
        'sub_sub_title': 'org'
    }
    return render(request, 'backend/libraries/pis/organization.html', context)


class OrganizationUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/organization_update.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def nonacad(request):
    form = NonacadForm()
    if request.method == "POST":
        form = NonacadForm(request.POST)
        if form.is_valid():
            el = form.save(commit=False)
            el.pi_id = request.session['pi_id']
            messages.success(request,
                             'The non-academic/recognition {} was added successfully.'.format(
                                 form.cleaned_data['na_name']))
            el.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'na': Paginator(Nonacad.objects.filter(Q(na_name__icontains=search)).order_by('na_name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'others',
        'sub_sub_title': 'na'
    }
    return render(request, 'backend/libraries/pis/nonacad.html', context)


class NonacadUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/nonacad_update.html'
    model = Nonacad
    form_class = NonacadForm
    success_url = reverse_lazy('nonacad')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def trainingtitle(request):
    form = TrainingtitleForm()
    if request.method == "POST":
        form = TrainingtitleForm(request.POST)
        if form.is_valid():
            tt = form.save(commit=False)
            tt.pi_id = request.session['pi_id']
            messages.success(request,
                             'The training title {} was added successfully.'.format(form.cleaned_data['tt_name']))
            tt.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'tt': Paginator(Trainingtitle.objects.filter(Q(tt_name__icontains=search)).order_by('tt_name'), rows).page(
            page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'training',
        'sub_sub_title': 'title'
    }
    return render(request, 'backend/libraries/pis/trainingtitle.html', context)


class TrainingtitleUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/trainingtitle_update.html'
    model = Trainingtitle
    form_class = TrainingtitleForm
    success_url = reverse_lazy('trainingtitle')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.pi_id = self.request.session['pi_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def trainingtype(request):
    form = TrainingtypeForm()
    if request.method == "POST":
        form = TrainingtypeForm(request.POST)
        if form.is_valid():
            tt = form.save(commit=False)
            tt.upload_by_id = request.user.id
            messages.success(request,
                             'The training type {} was added successfully.'.format(form.cleaned_data['type_name']))
            tt.save()
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': form,
        'tt': Paginator(Trainingtype.objects.filter(Q(type_name__icontains=search)).order_by('type_name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'training',
        'sub_sub_title': 'type'
    }
    return render(request, 'backend/libraries/pis/trainingtype.html', context)


class TrainingtypeUpdate(LoginRequiredMixin, AjaxableResponseMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/libraries/pis/trainingtype_update.html'
    model = Trainingtype
    form_class = TrainingtypeForm
    success_url = reverse_lazy('trainingtype')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.upload_by_id = self.request.user.id
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def find_merges(request, model, q, id):
    thismodel = None
    if model == 'degree':
        thismodel = Degree.objects.annotate(name=F('degree_name')).annotate(acronym=F('degree_acronym'))\
            .filter(~Q(id=id))
    elif model == 'organization':
        thismodel = Organization.objects.annotate(name=F('org_name')).filter(~Q(id=id))
    elif model == 'honors':
        thismodel = Honors.objects.annotate(name=F('hon_name')).filter(~Q(id=id))
    elif model == 'schools':
        thismodel = School.objects.annotate(name=F('school_name')).filter(~Q(id=id))
    elif model == 'trainingtitles':
        thismodel = Trainingtitle.objects.annotate(name=F('tt_name')).filter(~Q(id=id))
    elif model == 'eligibilities':
        thismodel = Eligibility.objects.annotate(name=F('el_name')).filter(~Q(id=id))
    elif model == 'positions':
        thismodel = Position.objects.filter(~Q(id=id))
    elif model == 'hobbies':
        thismodel = Hobbies.objects.annotate(name=F('hob_name')).filter(~Q(id=id))
    elif model == 'nonacads':
        thismodel = Nonacad.objects.annotate(name=F('na_name')).filter(~Q(id=id))

    results = []
    for el in thismodel:
        if el.name.lower() in re.split('[ \t\n\r\f,.;!?"()"\\\'/]', q.lower()) or q.lower() in el.name.lower():
            results.append({'name': el.name, 'id': el.id, 'acronym': el.acronym.upper() if hasattr(el, 'acronym') else ''})

    return JsonResponse({'data': results})


@login_required
@permission_required('admin.superadmin')
def merge_degree(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        acronym = request.POST.get('current_acronym')
        id = request.POST.get('current_id')

        z = Degree.objects.get(id=id)
        if z:
            z.degree_name = entity
            z.degree_acronym = acronym
            z.deg_status = 1
            z.pi_id = request.user.id
            z.save()

            for d in todelete:
                x = Educationbackground.objects.filter(degree_id=d)
                for j in x:
                    j.degree_id = id
                    j.save()
                Degree.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_organization(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Organization.objects.get(id=id)
        if z:
            z.org_name = entity
            z.org_status = 1
            z.pi_id = request.user.id
            z.save()

            for d in todelete:
                x = Voluntary.objects.filter(org_id=d)
                for j in x:
                    j.org_id = id
                    j.save()
                x = Membership.objects.filter(org_id=d)
                for j in x:
                    j.org_id = id
                    j.save()
                Organization.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_honors(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Honors.objects.get(id=id)
        if z:
            z.hon_name = entity
            z.hon_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Educationbackground.objects.filter(hon_id=d)
                for j in x:
                    j.hon_id = id
                    j.save()
                Honors.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_schools(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        acronym = request.POST.get('current_acronym')
        id = request.POST.get('current_id')

        z = School.objects.get(id=id)
        if z:
            z.school_name = entity
            z.school_acronym = acronym
            z.school_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Educationbackground.objects.filter(school_id=d)
                for j in x:
                    j.school_id = id
                    j.save()
                School.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_trainingtitles(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Trainingtitle.objects.get(id=id)
        if z:
            z.tt_name = entity
            z.tt_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Training.objects.filter(tt_id=d)
                for j in x:
                    j.tt_id = id
                    j.save()
                Trainingtitle.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_eligibilities(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Eligibility.objects.get(id=id)
        if z:
            z.el_name = entity
            z.el_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Civilservice.objects.filter(el_id=d)
                for j in x:
                    j.el_id = id
                    j.save()
                Eligibility.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_positions(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        acronym = request.POST.get('current_acronym')
        id = request.POST.get('current_id')

        z = Position.objects.get(id=id)
        if z:
            z.name = entity
            z.acronym = acronym
            z.status = 1
            z.upload_by_id = request.user.id
            z.save()

            for d in todelete:
                x = Workexperience.objects.filter(position_id=d)
                for j in x:
                    j.position_id = id
                    j.save()
                Position.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_hobbies(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Hobbies.objects.get(id=id)
        if z:
            z.hob_name = entity
            z.hob_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Skills.objects.filter(hob_id=d)
                for j in x:
                    j.hob_id = id
                    j.save()
                Hobbies.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('admin.superadmin')
def merge_nonacads(request):
    if request.method == "POST":
        todelete = request.POST.getlist('include_merge')
        entity = request.POST.get('current_entity')
        id = request.POST.get('current_id')

        z = Nonacad.objects.get(id=id)
        if z:
            z.na_name = entity
            z.na_status = 1
            z.pi_id = request.session['pi_id']
            z.save()

            for d in todelete:
                x = Recognition.objects.filter(na_id=d)
                for j in x:
                    j.na_id = id
                    j.save()
                Nonacad.objects.get(pk=d).delete()

    messages.success(request, 'Merging of similar entries into one entity was successful.')
    return JsonResponse({'data': 'success'})
