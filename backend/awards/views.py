import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import hashers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from backend.awards.models import Badges, Classification, Awlevels, Awards, Attachments, Prizes, Nominees, Awcategory, \
    Criteria, Deliberation, AwGuidelines, AwEligibility, AwEligibilityChecklist
from backend.forms import BadgesForm, ClassificationForm, AwlevelsForm, AwcategoriesForm
from backend.models import Empprofile
from backend.templatetags.tags import date_isbetween
from backend.views import AjaxableResponseMixin


@login_required
@permission_required('admin.superadmin')
def badges(request):
    form = BadgesForm()
    if request.method == "POST":
        form = BadgesForm(request.POST, request.FILES)
        if form.is_valid():
            badg = form.save(commit=False)
            badg.uploaded_by_id = request.session['emp_id']
            messages.success(request, 'The badge {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': BadgesForm,
        'data': Paginator(Badges.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'awards',
        'sub_sub_title': 'badges',
    }
    return render(request, 'backend/libraries/awards/badges.html', context)


class BadgesUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/awards/badges_update.html'
    model = Badges
    form_class = BadgesForm
    success_url = reverse_lazy('badges')
    permission_required = 'admin.superadmin'

    def form_valid(self, form):
        form.instance.uploaded_by_id = self.request.session['emp_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def awclassification(request):
    form = ClassificationForm()
    if request.method == "POST":
        form = ClassificationForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            badg.status = 1
            badg.uploaded_by_id = request.session['emp_id']
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
        'form': ClassificationForm,
        'data': Paginator(Classification.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'awards',
        'sub_sub_title': 'classification',
    }
    return render(request, 'backend/libraries/awards/classification.html', context)


class ClassificationUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/awards/classification_update.html'
    model = Classification
    form_class = ClassificationForm
    success_url = reverse_lazy('classification')
    permission_required = "admin.superadmin"

    def form_valid(self, form):
        form.instance.uploaded_by_id = self.request.session['emp_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def awlevels(request):
    form = AwlevelsForm()
    if request.method == "POST":
        form = AwlevelsForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            badg.status = 1
            badg.uploaded_by_id = request.session['emp_id']
            messages.success(request, 'The level {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': AwlevelsForm,
        'data': Paginator(Awlevels.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'awards',
        'sub_sub_title': 'level',
    }
    return render(request, 'backend/libraries/awards/levels.html', context)


class AwlevelsUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/awards/levels_update.html'
    model = Awlevels
    form_class = AwlevelsForm
    success_url = reverse_lazy('award-level')
    permission_required = "admin.superadmin"

    def form_valid(self, form):
        form.instance.uploaded_by_id = self.request.session['emp_id']
        return super().form_valid(form)


@login_required
@permission_required('admin.superadmin')
def awcategories(request):
    form = AwcategoriesForm()
    if request.method == "POST":
        form = AwcategoriesForm(request.POST)
        if form.is_valid():
            badg = form.save(commit=False)
            badg.status = 1
            badg.uploaded_by_id = request.session['emp_id']
            badg.icon = 'user'
            messages.success(request, 'The category {} was added successfully.'.format(form.cleaned_data['name']))
            badg.save()

            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'form': AwcategoriesForm,
        'data': Paginator(Awcategory.objects.filter(Q(name__icontains=search)).order_by('name'), rows).page(page),
        'rows': rows,
        'title': 'libraries',
        'sub_title': 'awards',
        'sub_sub_title': 'category',
    }
    return render(request, 'backend/libraries/awards/category.html', context)


class AwcategoriesUpdate(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    login_url = 'backend-login'
    template_name = 'backend/libraries/awards/categories_update.html'
    model = Awcategory
    form_class = AwcategoriesForm
    success_url = reverse_lazy('award-category')
    permission_required = "admin.superadmin"

    def form_valid(self, form):
        form.instance.uploaded_by_id = self.request.session['emp_id']
        return super().form_valid(form)


@login_required
@permission_required('auth.awards')
def awards(request):
    if request.method == "POST":
        award = Awards(
            name=request.POST.get('award_name'),
            category_id=request.POST.get('category'),
            year=request.POST.get('year'),
            level_id=request.POST.get('level'),
            badge_id=request.POST.get('badge'),
            classification_id=request.POST.get('classification'),
            status=1,
            uploaded_by_id=request.session['emp_id'],
            is_nomination=request.POST.get('nomination'),
            nomination_start=request.POST.get('nomination_start'),
            nomination_end=request.POST.get('nomination_end')
        )
        award.save()

        file = request.FILES.getlist('file[]')
        description = request.POST.getlist('description[]')
        attachment = [
            {'file': f, 'description': d}
            for f, d in zip(file, description)
        ]

        for row in attachment:
            Attachments.objects.create(
                name=row['description'],
                file=row['file'],
                awards_id=award.id
            )

        prize = request.POST.getlist('prize[]')
        unit = request.POST.getlist('unit[]')
        qty = request.POST.getlist('quantity[]')
        if prize[0] != '':
            prizes = [
                {'prize': p, 'unit': u, 'qty': q}
                for p, u, q in zip(prize, unit, qty)
            ]

            for row in prizes:
                Prizes.objects.create(
                    name=row['prize'],
                    quantity=row['qty'],
                    unit=row['unit'],
                    awards_id=award.id
                )

        messages.success(request, "The {} was successfully added".format(request.POST.get('award_name')))
        return JsonResponse({'data': 'success'})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        'badges': Paginator(Awards.objects.filter(Q(name__icontains=search))
                            .order_by('-year', 'category__name', 'name'), rows).page(page),
        'level': Awlevels.objects.filter(status=1),
        'category': Awcategory.objects.filter(status=1),
        'classification': Classification.objects.filter(status=1),
        'badge': Badges.objects.all(),
        'yr': datetime.now().year,
        'rows': rows,
        'management': True,
        'title': 'awards_management',
        'sub_title': 'awards'
    }
    return render(request, 'backend/pas/awards/awards.html', context)


@login_required
@permission_required('auth.awards')
def update_awards(request, pk):
    if request.method == "POST":
        if request.POST.get('action') == 'update':
            aws = Awards.objects.filter(id=pk).first()
            aws.name = request.POST.get('award_name')
            aws.category_id = request.POST.get('category')
            aws.year = request.POST.get('year')
            aws.level_id = request.POST.get('level')
            aws.badge_id = request.POST.get('badge')
            aws.classification_id = request.POST.get('classification')
            aws.uploaded_by_id = request.session['emp_id']
            aws.is_nomination = request.POST.get('nomination')
            aws.nomination_start = request.POST.get('nomination_start')
            aws.nomination_end = request.POST.get('nomination_end')
            aws.save()

            prize = request.POST.getlist('prize[]')
            unit = request.POST.getlist('unit[]')
            qty = request.POST.getlist('quantity[]')
            prize_id = request.POST.getlist('prize-id[]')

            # get all existing prizes from database
            all_prizes = Prizes.objects.filter(Q(awards_id=pk)).all()
            for p in all_prizes:
                if prize_id.count(str(p.id)) == 0:
                    Prizes.objects.filter(Q(id=p.id)).delete()

            if prize[0] != '':
                prizes = [
                    {'prize': p, 'unit': u, 'qty': q, 'id': i}
                    for p, u, q, i in zip(prize, unit, qty, prize_id)
                ]

                for row in prizes:
                    if row['id'] == '' or row['id'] is None:
                        Prizes.objects.create(
                            name=row['prize'],
                            quantity=row['qty'],
                            unit=row['unit'],
                            awards_id=pk
                        )
                    else:
                        Prizes.objects.filter(id=int(row['id'])).update(name=row['prize'], quantity=float(row['qty']),
                                                                        unit=row['unit'])

            desc = request.POST.getlist('description[]')
            att_id = request.POST.getlist('att-id[]')

            # get all existing attachment from database
            all_attachment = Attachments.objects.filter(Q(awards_id=pk)).all()
            for a in all_attachment:
                if att_id.count(str(a.id)) == 0:
                    Attachments.objects.filter(Q(id=a.id)).delete()

            attachment = [
                {'id': a, 'desc': d}
                for a, d in zip(att_id, desc)
            ]

            for row in attachment:
                if row['id'] is not None or row['id'] != '':
                    Attachments.objects.filter(Q(id=row['id'])).update(name=row['desc'])
                else:
                    Attachments.objects.create(
                        name=row['desc'],
                        file=None,
                        awards_id=pk
                    )

            desc_add = request.POST.getlist('description-add[]')
            file_add = request.FILES.getlist('file-add[]')
            attachment_add = [
                {'file': f, 'description': d}
                for f, d in zip(file_add, desc_add)
            ]

            for row in attachment_add:
                Attachments.objects.create(
                    name=row['description'],
                    file=row['file'],
                    awards_id=pk
                )

            return JsonResponse(
                {'data': 'success', 'msg': "The {} was successfully updated.".format(request.POST.get('award_name'))})
        else:
            cname = request.POST.getlist('criteria_name[]')
            cdesc = request.POST.getlist('criteria_desc[]')
            cpctg = request.POST.getlist('criteria_percentage[]')
            c_id = request.POST.getlist('criteria_id[]')

            # get all existing criteria from database
            all_criteria = Criteria.objects.filter(Q(awards_id=pk), Q(is_active=1)).all()
            for p in all_criteria:
                if c_id.count(str(p.id)) == 0:
                    Criteria.objects.filter(Q(id=p.id)).update(is_active=0)

            if cname[0] != '':
                crites = [
                    {'name': p, 'desc': u, 'pctg': q, 'id': i}
                    for p, u, q, i in zip(cname, cdesc, cpctg, c_id)
                ]

                for row in crites:
                    if row['id'] == '' or row['id'] is None:
                        Criteria.objects.create(
                            name=row['name'],
                            desc=row['desc'],
                            percentage=row['pctg'],
                            is_active=1,
                            awards_id=pk
                        )
                    else:
                        Criteria.objects.filter(id=int(row['id'])).update(name=row['name'], desc=row['desc'],
                                                                          percentage=int(row['pctg']))

            return JsonResponse({'data': 'success', 'msg': "The criteria for {} was successfully updated.".format(
                request.POST.get('award_name'))})

    context = {
        'awards': Awards.objects.filter(id=pk).first(),
        'prizes': Prizes.objects.filter(awards_id=pk),
        'criteria': Criteria.objects.filter(awards_id=pk, is_active=1),
        'category': Awcategory.objects.filter(status=1),
        'attachments': Attachments.objects.filter(awards_id=pk),
        'level': Awlevels.objects.filter(status=1),
        'classification': Classification.objects.filter(status=1),
        'badge': Badges.objects.all(),
        'tab_title': 'Update Awards',
        'title': 'awards_management',
        'management': True,
        'sub_title': 'awards',
    }
    awsh = Awards.objects.filter(id=pk).first()
    if awsh and awsh.status == 1:
        return render(request, 'backend/pas/awards/update_awards.html', context)
    else:
        raise Http404('You are not authorized to access this content. Please contact your administrator.')


@login_required
@permission_required('auth.awards')
def awards_eligibility_criteria(request, pk):
    if request.method == "POST":
        eligibilities = request.POST.getlist('eligibility[]')

        AwEligibility.objects.filter(~Q(eligibility__in=eligibilities), awards_id=pk).delete()
        check = AwEligibility.objects.filter(awards_id=pk)
        store = [row.id for row in check]
        if check:
            y = 1
            x = 0
            for row in eligibilities:
                if y > len(check):
                    AwEligibility.objects.create(
                        eligibility=row,
                        awards_id=pk
                    )
                else:
                    AwEligibility.objects.filter(id=store[x]).update(
                        eligibility=row,
                        awards_id=pk
                    )
                    y += 1
                    x += 1
        else:
            for row in eligibilities:
                AwEligibility.objects.create(
                    eligibility=row,
                    awards_id=pk
                )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully save the awards eligibility criteria.'})

    context = {
        'eligibility': AwEligibility.objects.filter(awards_id=pk),
        'pk': pk
    }
    return render(request, 'backend/pas/awards/view_eligibility.html', context)


@login_required
@permission_required('auth.awards')
def toggle_awards(request):
    if request.method == "POST":
        aws = Awards.objects.filter(id=request.POST.get('id')).first()
        aws.status = not aws.status
        aws.save()
        return JsonResponse({'data': 'success'})
    else:
        return JsonResponse(
            {'error': 'You are not authorized to access this content. Please contact your administrator.'})


@login_required
@permission_required('auth.awards')
def validate_nominees(request, pk):
    award = Awards.objects.filter(id=pk).first()
    nominees = Nominees.objects.filter(awards_id=pk).extra(
        select={'manual': 'FIELD(nominated_by_id,%s)' % ','.join(map(str, [request.session['emp_id']]))},
        order_by=['-is_winner', '-status', '-manual']
    )

    if award.nomination_start and award.nomination_end:
        is_done = date_isbetween(datetime.now().date(), (
            datetime.strptime(str(award.nomination_start), '%Y-%m-%d').date(),
            datetime.strptime(str(award.nomination_end), '%Y-%m-%d').date()
        ))
    else:
        is_done = False

    context = {
        'nominees': nominees if nominees else None,
        'criteria': Criteria.objects.filter(awards_id=pk),
        'eligibility': AwEligibility.objects.filter(awards_id=pk),
        'row': award,
        'isdone': is_done,
        'pk': pk
    }
    return render(request, 'backend/awards/view_nominees.html', context)


@login_required
@permission_required('auth.awards')
def eligibility_criteria_checklist(request, pk):
    if request.method == "POST":
        eligibilities = request.POST.getlist('eligibility[]')

        AwEligibilityChecklist.objects.filter(~Q(eligibility__in=eligibilities), nominees_id=pk).delete()
        check = AwEligibilityChecklist.objects.filter(nominees_id=pk)
        store = [row.id for row in check]
        if check:
            y = 1
            x = 0
            for row in eligibilities:
                if y > len(check):
                    AwEligibilityChecklist.objects.create(
                        eligibility_id=row,
                        nominees_id=pk
                    )
                else:
                    AwEligibilityChecklist.objects.filter(id=store[x]).update(
                        eligibility_id=row,
                        nominees_id=pk
                    )
                    y += 1
                    x += 1
        else:
            for row in eligibilities:
                AwEligibilityChecklist.objects.create(
                    eligibility_id=row,
                    nominees_id=pk
                )
        Nominees.objects.filter(id=pk).update(status=1)
        return JsonResponse({'data': 'success', 'msg': 'You have successfully verified the nominee.'})
    nominees = Nominees.objects.filter(id=pk).first()
    context = {
        'nominees': nominees,
        'eligibility': AwEligibility.objects.filter(awards_id=nominees.awards_id),
    }
    return render(request, 'backend/awards/checklist_eligibility.html', context)


@login_required
@csrf_exempt
@permission_required('auth.awards')
def update_checklist_eligibility(request, pk):
    if request.method == "POST":
        eligibilities = request.POST.getlist('eligibility[]')

        AwEligibilityChecklist.objects.filter(~Q(eligibility__in=eligibilities), nominees_id=pk).delete()
        check = AwEligibilityChecklist.objects.filter(nominees_id=pk)
        store = [row.id for row in check]
        if check:
            y = 1
            x = 0
            for row in eligibilities:
                if y > len(check):
                    AwEligibilityChecklist.objects.create(
                        eligibility_id=row,
                        nominees_id=pk
                    )
                else:
                    AwEligibilityChecklist.objects.filter(id=store[x]).update(
                        eligibility_id=row,
                        nominees_id=pk
                    )
                    y += 1
                    x += 1
        else:
            for row in eligibilities:
                AwEligibilityChecklist.objects.create(
                    eligibility_id=row,
                    nominees_id=pk
                )

        Nominees.objects.filter(id=pk).update(status=0)
        return JsonResponse({'data': 'success', 'msg': 'You have successfully updated the eligibility checklist of the nominee.'})


@login_required
@permission_required('auth.awards')
def add_nominee(request, pk):
    if request.method == "POST":
        nominee = re.split('\[|\]', request.POST.get('nominee'))
        name = Empprofile.objects.values('id').filter(id_number=nominee[1]).first()
        details = Nominees(
            awards_id=pk,
            nominee_id=name['id'],
            nominated_by_id=request.session['emp_id'],
            datetime=datetime.now(),
            why=request.POST.get('why'),
            title=request.POST.get('title'),
            status=0,
            is_winner=0,
        )
        details.save()
        return JsonResponse({'data': 'success'})

        # xx = Nominees.objects.filter(Q(nominee_id=name['id']), Q(awards_id=pk)).count()
        # 
        # if xx == 0:
        #     details.save()
        #     return JsonResponse({'data': 'success'})
        # else:
        #     return JsonResponse({'data': 'failed', 'error': 'Duplicate nomination.'})
    context = {
        'awards_id': pk,
        'award': Awards.objects.filter(id=pk).first(),
    }
    return render(request, 'backend/awards/add_nominee.html', context)


@login_required
@permission_required('auth.awards')
def edit_nominee(request, pk):
    noms = Nominees.objects.filter(id=pk).first()
    if request.method == "POST":
        toupdate = Nominees.objects.filter(id=pk)
        toupdate.update(datetime=datetime.now())
        toupdate.update(why=request.POST.get('why'))
        toupdate.update(title=request.POST.get('title'))
        return JsonResponse({'data': 'success'})

    context = {
        'awards_id': noms.awards_id,
        'nominee': noms,
        'award': Awards.objects.filter(id=noms.awards_id).first(),
    }
    return render(request, 'backend/awards/add_nominee.html', context)


@login_required
@csrf_exempt
@permission_required('auth.awards')
def verified_nominee(request, pk):
    Nominees.objects.filter(Q(id=pk)).update(status=1)
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.awards')
def delete_nominee(request, pk):
    Nominees.objects.filter(Q(id=pk)).delete()
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.awards')
def reset_results(request, pk):
    Nominees.objects.filter(Q(awards_id=pk)).update(is_winner=0)
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.awards')
def mark_as_winner(request, pk):
    Nominees.objects.filter(Q(id=pk)).update(is_winner=1)
    return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required('auth.awards')
def check_password(request):
    user = Empprofile.objects.filter(Q(id=request.POST['session_emp_id'])).first()
    is_true = hashers.check_password(request.POST['password'], user.pi.user.password)
    return JsonResponse({'data': is_true})


@login_required
@permission_required('auth.awards')
def nominees_report(request):
    if request.method == "POST":
        context = {
            'management': True,
            'title': 'awards_management',
            'sub_title': 'awards_report',
            'awards': Awards.objects.filter(id=request.POST.get('awards'), year=request.POST.get('year')).first(),
            'data': Nominees.objects.filter(awards_id=request.POST.get('awards'),
                                            awards__year=request.POST.get('year')),
            'category': Awcategory.objects.filter(status=1),
            'notpost': False,
        }
        return render(request, 'backend/pas/awards/nominees_report.html', context)

    context = {
        'management': True,
        'title': 'awards_management',
        'sub_title': 'awards_report',
        'sub_sub_title': 'nominees_report',
        'category': Awcategory.objects.filter(status=1),
        'notpost': True,
    }
    return render(request, 'backend/pas/awards/nominees_report.html', context)


@login_required
@csrf_exempt
@permission_required('auth.awards_deliberators')
def check_awards(request):
    awards = Awards.objects.filter(category_id=request.POST.get('category'), year=request.POST.get('year'))
    data = [dict(id=row.id, awards_name=row.name) for row in awards]
    return JsonResponse({'data': data})


@login_required
@permission_required('auth.awards')
def print_nominees_report(request):
    if request.method == "POST":
        context = {
            'awards': Awards.objects.filter(id=request.POST.get('print_awards')).first(),
            'data': Nominees.objects.filter(awards_id=request.POST.get('print_awards')),
            'category': Awcategory.objects.filter(status=1),
        }
        return render(request, 'backend/pas/awards/print_nominees_report.html', context)


@login_required
@permission_required('auth.awards')
def deliberation_results(request):
    if request.method == "POST":
        a = list()
        b = Deliberation.objects.values('graded_by_id') \
            .filter(Q(nominee__awards_id=request.POST.get('awards')), Q(criteria__is_active=1)) \
            .annotate(total_grade=Sum('grade'))
        for x in b:
            a.append(x['graded_by_id'])
        c = Empprofile.objects.filter(Q(id__in=a))

        context = {
            'management': True,
            'title': 'awards_management',
            'sub_title': 'deliberation_results',
            'sub_sub_title': 'deliberation_results',
            'graders': c,
            'awards': Awards.objects.filter(id=request.POST.get('awards'), year=request.POST.get('year')).first(),
            'data': Nominees.objects.filter(awards_id=request.POST.get('awards'),
                                            awards__year=request.POST.get('year')),
            'category': Awcategory.objects.filter(status=1),
            'notpost': False,
            'year': request.POST.get('year'),
            'ctgy': request.POST.get('category'),
            'awrd': request.POST.get('awards'),
        }
        return render(request, 'backend/pas/awards/deliberation_results.html', context)

    context = {
        'management': True,
        'title': 'awards_management',
        'sub_title': 'deliberation_results',
        'sub_sub_title': 'deliberation_results',
        'notpost': True,
        'category': Awcategory.objects.filter(status=1),
    }
    return render(request, 'backend/pas/awards/deliberation_results.html', context)


@login_required
@permission_required('auth.awards')
def print_deliberation_results(request):
    if request.method == "POST":
        a = list()
        b = Deliberation.objects.values('graded_by_id') \
            .filter(Q(nominee__awards_id=request.POST.get('awards')), Q(criteria__is_active=1)) \
            .annotate(total_grade=Sum('grade'))
        for x in b:
            a.append(x['graded_by_id'])
        c = Empprofile.objects.filter(Q(id__in=a))
        context = {
            'graders': c,
            'awards': Awards.objects.filter(id=request.POST.get('awards'), year=request.POST.get('year')).first(),
            'data': Nominees.objects.filter(awards_id=request.POST.get('awards'),
                                            awards__year=request.POST.get('year')),
        }
        return render(request, 'backend/pas/awards/print_deliberation_results.html', context)


@login_required
@permission_required('auth.awards')
def upload_guidelines(request):
    if request.method == "POST":
        check = AwGuidelines.objects.filter(year=request.POST.get('year'))
        if not check:
            AwGuidelines.objects.create(
                year=request.POST.get('year'),
                title=request.POST.get('title'),
                file=request.FILES.get('file')
            )
            return JsonResponse({'data': 'success', 'msg': 'PRAISE Guidelines uploaded successfully.'})
        else:
            return JsonResponse({'error': True, 'msg': 'PRAISE Guidelines already uploaded.'})
    context = {
        'management': True,
        'title': 'awards_management',
        'sub_title': 'guidelines'
    }
    return render(request, 'backend/awards/guidelines.html', context)


@login_required
@csrf_exempt
@permission_required('auth.awards')
def delete_guidelines(request, pk):
    AwGuidelines.objects.filter(id=pk).delete()
    return JsonResponse({'data': 'success', 'msg': 'PRAISE Awards Guidelines has been successfully deleted.'})
