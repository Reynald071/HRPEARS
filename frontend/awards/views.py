import re
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.awards.models import Awards, Nominees, Attachments, Awcategory, Criteria, Deliberation, AwGuidelines, \
    AwEligibility
from backend.models import Empprofile, Division
from frontend.models import PortalConfiguration


@login_required
def awards(request):
    context = {
        'categories': Awcategory.objects.filter(status=1),
        'name': awards,
        'tab_parent': 'Rewards & Recognition',
        'tab_title': 'Nominations',
        'title': 'rewards_and_recognition',
        'sub_title': 'nominations',
        'year': datetime.now().year
    }
    return render(request, 'frontend/awards/awards.html', context)


@login_required
def view_awards(request, year, category):
    if category == "all":
        awards = Awards.objects.filter(Q(year=year), Q(status=1)).order_by(
            'name')
    else:
        awards = Awards.objects.filter(Q(year=year), Q(category_id=category), Q(status=1)).order_by(
            'name')

    nominees = Nominees.objects.filter(Q(awards__year=year)).order_by('-id')
    latest = []
    for nominee in nominees[:10]:
        latest.append('<div class="row">'
                      '<div class="col-xs-2">'
                      '<img alt="image" class="img-circle" src="{}" '
                      'style="object-fit:cover; height:48px; width:48px;">'
                      '</div>'
                      '<div class="col-xs-10">'
                      '<strong><a href="javascript:;">{}</a></strong> has been nominated as '
                      '<a class="btn-edit-modal" data-id="{}" href="javascript:;">{}</a>. <br>'
                      '<small class="text-muted pull-right">{}</small>'
                      '</div>'
                      '</div>'
                      .format(nominee.nominee.picture.url, nominee.nominee.pi.user.get_fullname,
                              nominee.awards_id, nominee.awards.name, nominee.datetime.strftime('%b %d, %Y @ %I:%M %p')))

    context = {
        'awards': awards,
        'latest': latest,
        'others': len(nominees) - 10
    }
    return render(request, 'frontend/awards/view_awards.html', context)


@login_required
def view_nominees(request, pk):
    award = Awards.objects.filter(id=pk).first()
    division = Division.objects.filter(div_chief_id=request.session['emp_id']).first()
    if division or request.user.is_superuser:
        nominees = Nominees.objects.filter(awards_id=pk).extra(
            select={'manual': 'FIELD(nominated_by_id,%s)' % ','.join(map(str, [request.session['emp_id']]))},
            order_by=['-is_winner', '-status', '-manual']
        )
    else:
        nominees = Nominees.objects.filter(awards_id=pk, nominated_by_id=request.session['emp_id']).extra(
            select={'manual': 'FIELD(nominated_by_id,%s)' % ','.join(map(str, [request.session['emp_id']]))},
            order_by=['-is_winner', '-status', '-manual']
        )

    today = datetime.now().date()
    isnotdone = Awards.objects.filter(nomination_end__gte=today, id=pk)

    context = {
        'nominees': nominees if nominees else None,
        'row': award,
        'criteria': Criteria.objects.filter(awards_id=pk),
        'eligibility': AwEligibility.objects.filter(awards_id=pk),
        'attachments': Attachments.objects.filter(awards_id=pk),
        'isnotdone': isnotdone,
        'pk': pk
    }
    return render(request, 'frontend/awards/view_nominees.html', context)


@login_required
def nominee_count(request, pk):
    noms = Nominees.objects.filter(awards_id=pk).count()
    e = ["Number of Nominees: " + str(noms)]
    return JsonResponse({'data': e})


@login_required
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
            title=request.POST.get('title') if request.POST.get('title') else None,
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
    return render(request, 'frontend/awards/add_nominee.html', context)


@login_required
def edit_nominee(request, pk):
    noms = Nominees.objects.filter(id=pk).first()
    if request.method == "POST":
        toupdate = Nominees.objects.filter(id=pk)
        toupdate.update(datetime=datetime.now())
        toupdate.update(why=request.POST.get('why'))
        toupdate.update(title=request.POST.get('title') if request.POST.get('title') else None)
        return JsonResponse({'data': 'success'})

    context = {
        'awards_id': noms.awards_id,
        'nominee': noms,
        'award': Awards.objects.filter(id=noms.awards.id).first(),
    }
    return render(request, 'frontend/awards/add_nominee.html', context)


@login_required
@csrf_exempt
def delete_nominee(request, pk):
    Nominees.objects.filter(Q(id=pk)).delete()
    return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.awards_deliberators')
def deliberation(request):
    if request.method == "POST":
        if request.POST.get('action') == 'save':
            criteria_id = request.POST.getlist('criteria_id[]')
            nominee_id = request.POST.getlist('nominee_id[]')
            grade = request.POST.getlist('grade[]')

            grades = [
                {'c': c, 'n': n, 'g': g} for c, n, g in zip(criteria_id, nominee_id, grade)
            ]

            remarks_nominee_id = request.POST.getlist('remarks_nominee_id[]')
            remarks = request.POST.getlist('remarks[]')

            allremarks = [
                {'n': n, 'r': r}
                for n, r in zip(remarks_nominee_id, remarks)
            ]

            for row in grades:
                doesexist = Deliberation.objects.filter(Q(nominee_id=row['n']), Q(criteria_id=row['c']), Q(graded_by_id=request.session['emp_id'])).first()
                rm = ''
                for r in allremarks:
                    if r['n'] == row['n']:
                        rm = r['r']

                if row['g'] != '':
                    if not doesexist:
                        Deliberation.objects.create(
                            criteria_id=row['c'],
                            nominee_id=row['n'],
                            grade=row['g'],
                            remarks=rm,
                            graded_by_id=request.session['emp_id'],
                            graded_on=datetime.now()
                        )
                    else:
                        Deliberation.objects.filter(Q(nominee_id=row['n']), Q(criteria_id=row['c']), Q(graded_by_id=request.session['emp_id']))\
                            .update(grade=row['g'], graded_on=datetime.now(), remarks=rm)

        toggle = PortalConfiguration.objects.filter(key_name='Deliberation').first()
        if toggle.key_acronym == '1':
            context = {
                'title': 'human_resource_transactions',
                'sub_title': 'awardsf',
                'sub_sub_title': 'deliberation',
                'criteria': Criteria.objects.filter(Q(awards_id=request.POST.get('awards')), Q(is_active=1)).order_by('-percentage', 'id', 'name'),
                'awards': Awards.objects.filter(id=request.POST.get('awards'), year=request.POST.get('year')).first(),
                'data': Nominees.objects.filter(awards_id=request.POST.get('awards'), awards__year=request.POST.get('year')),
                'category': Awcategory.objects.filter(status=1),
                'notpost': False,
                'toggle': True,
                'year': request.POST.get('year'),
                'ctgy': request.POST.get('category'),
                'awrd': request.POST.get('awards'),
            }
        else:
            a = list()
            b = Deliberation.objects.values('graded_by_id') \
                .filter(Q(nominee__awards_id=request.POST.get('awards')), Q(criteria__is_active=1)) \
                .annotate(total_grade=Sum('grade'))
            for x in b:
                a.append(x['graded_by_id'])
            c = Empprofile.objects.filter(Q(id__in=a))

            context = {
                'title': 'human_resource_transactions',
                'sub_title': 'awardsf',
                'sub_sub_title': 'deliberation',
                'graders': c,
                'awards': Awards.objects.filter(id=request.POST.get('awards'), year=request.POST.get('year')).first(),
                'data': Nominees.objects.filter(awards_id=request.POST.get('awards'),
                                                awards__year=request.POST.get('year')),
                'category': Awcategory.objects.filter(status=1),
                'notpost': False,
                'toggle': False,
                'year': request.POST.get('year'),
                'ctgy': request.POST.get('category'),
                'awrd': request.POST.get('awards'),
            }
        return render(request, 'frontend/awards/deliberation.html', context)

    context = {
        'tab_title': 'Deliberation',
        'title': 'rewards_and_recognition',
        'sub_title': 'awardsf',
        'sub_sub_title': 'deliberation',
        'notpost': True,
        'category': Awcategory.objects.filter(status=1),
    }
    return render(request, 'frontend/awards/deliberation.html', context)


@login_required
@permission_required('auth.awards_deliberators')
def save_deliberation(request):
    if request.method == "POST":
        criteria_id = request.POST.getlist('criteria_id[]')
        nominee_id = request.POST.getlist('nominee_id[]')
        grade = request.POST.getlist('grade[]')

        grades = [
            {'c': c, 'n': n, 'g': g}
            for c, n, g in zip(criteria_id, nominee_id, grade)
        ]

        remarks_nominee_id = request.POST.getlist('remarks_nominee_id[]')
        remarks = request.POST.getlist('remarks[]')

        allremarks = [
            {'n': n, 'r': r}
            for n, r in zip(remarks_nominee_id, remarks)
        ]

        for row in grades:
            doesexist = Deliberation.objects.filter(Q(nominee_id=row['n']), Q(criteria_id=row['c']),
                                                    Q(graded_by_id=request.session['emp_id'])).first()
            rm = ''
            for r in allremarks:
                if r['n'] == row['n']:
                    rm = r['r']

            if row['g'] != '':
                if not doesexist:
                    Deliberation.objects.create(
                        criteria_id=row['c'],
                        nominee_id=row['n'],
                        grade=row['g'],
                        remarks=rm,
                        graded_by_id=request.session['emp_id'],
                        graded_on=datetime.now()
                    )
                else:
                    Deliberation.objects.filter(Q(nominee_id=row['n']), Q(criteria_id=row['c']),
                                                Q(graded_by_id=request.session['emp_id'])) \
                        .update(grade=row['g'], graded_on=datetime.now(), remarks=rm)

        return JsonResponse({'data': 'success'})


@login_required
@permission_required('auth.awards_deliberators')
def get_guidelines(request, year):
    guidelines = AwGuidelines.objects.filter(year=year).first()
    if guidelines:
        return JsonResponse({'title': guidelines.title, 'file': guidelines.file.url})
    else:
        return JsonResponse({'error': True, 'msg': 'No attachment available.'})