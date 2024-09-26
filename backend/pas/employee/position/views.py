from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render

from backend.templatetags.tags import force_token_decryption
from backend.models import PositionVacancy, Position, Aoa, Salarygrade, Empstatus


@login_required
@permission_required("auth.position")
def position_status(request):
    if request.method == "POST":
        deadline = request.POST.get('deadline')
        position = PositionVacancy(
            number=request.POST.get('number'),
            item_number=request.POST.get('item_number'),
            position_id=request.POST.get('position'),
            empstatus_id=request.POST.get('empstatus'),
            aoa_id=request.POST.get('aoa'),
            quantity=request.POST.get('quantity'),
            salary_rate=request.POST.get('rate'),
            salary_grade_id=request.POST.get('grade'),
            job_description=request.POST.get('job_description'),
            deadline=deadline if deadline != '' else None,
            upload_by_id=request.session['user_id'],
        )

        position.save()

        return JsonResponse({'data': 'success'})

    context = {
        'title': 'employee',
        'sub_title': 'position_status',
        'position_choices': Position.objects.filter(status=1).order_by('name'),
        'aoa': Aoa.objects.filter(status=1).order_by('name'),
        'salary_grade': Salarygrade.objects.filter(status=1).order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1),
    }
    return render(request, 'backend/employee_data/position/position_status.html', context)


@login_required
@permission_required('auth.position')
def get_position_totals(request):
    total_draft = PositionVacancy.objects.filter(status=0).count()
    total_vacancy = PositionVacancy.objects.filter(status=1).count()
    total_filled = PositionVacancy.objects.filter(status=2).count()

    return JsonResponse({'vacancy': total_vacancy, 'filled': total_filled, 'draft': total_draft})


@csrf_exempt
@login_required
@permission_required('auth.position')
def submit_position(request):
    PositionVacancy.objects.filter(id=request.POST.get('id')).update(status=1)
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@permission_required('auth.position')
def delete_position(request):
    PositionVacancy.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@permission_required('auth.position')
def edit_position(request, pk):
    if request.method == "POST":
        deadline = request.POST.get('deadline')
        PositionVacancy.objects.filter(id=pk).update(
            number=request.POST.get('number'),
            item_number=request.POST.get('item_number'),
            position_id=request.POST.get('position'),
            empstatus_id=request.POST.get('empstatus'),
            aoa_id=request.POST.get('aoa'),
            quantity=request.POST.get('quantity'),
            salary_rate=request.POST.get('rate'),
            salary_grade_id=request.POST.get('grade'),
            job_description=request.POST.get('job_description'),
            deadline=deadline if deadline != '' else None,
        )

        return JsonResponse({'data': 'success'})

    context = {
        'position': PositionVacancy.objects.filter(id=pk).first(),
        'position_choices': Position.objects.filter(status=1).order_by('name'),
        'aoa': Aoa.objects.filter(status=1).order_by('name'),
        'salary_grade': Salarygrade.objects.filter(status=1).order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1),
    }
    return render(request, 'backend/employee_data/position/edit_position.html', context)


@login_required
@permission_required('auth.position')
def vacancy_attachment(request, pk):
    vacancy = PositionVacancy.objects.filter(id=pk).first()

    if request.method == "POST":
        file = request.FILES.get('file')

        vacancy.attachment = file
        vacancy.save()

        return JsonResponse({
            'data': 'success', 'vacancy_name': vacancy.position.name,
            'empstatus': vacancy.empstatus.name, 'pk': pk
        })

    context = {
        'vacancy': vacancy,
        'attachment': vacancy.attachment,
        'pk' : pk,
    }
    return render(request, 'backend/employee_data/position/attachment.html', context)

