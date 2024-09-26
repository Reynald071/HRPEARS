from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.models import Empprofile
from backend.pas.clearance.models import ClearanceContent
from frontend.templatetags.tags import getempbyuser, get_empstatus


@login_required
def clearance_content(request):
    if request.method == "POST":
        check = ClearanceContent.objects.filter(id=request.POST.get('update_id'))
        if check:
            check.update(
                content=request.POST.get('content')
            )
        else:
            ClearanceContent.objects.create(
                content=request.POST.get('content')
            )
        return JsonResponse({'data': 'success'})
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    context = {
        'title': 'libraries',
        'data': Paginator(ClearanceContent.objects.filter(content__icontains=search).order_by('-id'), rows).page(page),
        'sub_title': 'documents',
        'sub_sub_title': 'clearance_b'
    }
    return render(request, 'backend/pas/clearance/content.html', context)


@login_required
def view_clearance_layout(request, emp_id, id):
    context = {
        'employee': Empprofile.objects.filter(id=emp_id).first(),
        'data': ClearanceContent.objects.filter(id=id).first()
    }
    return render(request, 'backend/pas/clearance/clearance-layout.html', context)


@login_required
def view_clearance_layout_current(request):
    emp_id = getempbyuser(request.user.id).id
    id = get_empstatus(emp_id)
    context = {
        'employee': Empprofile.objects.filter(id=emp_id).first(),
        'data': ClearanceContent.objects.filter(id=id).first()
    }
    return render(request, 'backend/pas/clearance/clearance-layout.html', context)


@csrf_exempt
@login_required
def get_clearance_content(request):
    if request.method == "POST":
        data = ClearanceContent.objects.filter(id=request.POST.get('id')).first()
        return JsonResponse({'data': 'success', 'content': data.content, 'id': data.id})


@csrf_exempt
@login_required
def get_credentials(request, emp_id):
    today = datetime.today()
    employee = Empprofile.objects.filter(id=emp_id).first()
    fullname = "{}, {} {}".format(employee.pi.user.last_name, employee.pi.user.first_name, employee.pi.user.middle_name)
    position = "{}/{}/{}".format(employee.position.acronym, employee.salary_grade, employee.step_inc) if employee.position else None
    area = employee.aoa.name if employee.aoa else None
    empstatus = employee.empstatus.name if employee.empstatus else None
    project = employee.project.name if employee.project else None
    id_number = employee.id_number

    supervisor = ""
    division_chief = ""
    if employee.section:
        employee2 = Empprofile.objects.filter(id=employee.section.sec_head_id).first()
        supervisor = "{} {} {}".format(employee2.pi.user.first_name, employee2.pi.user.middle_name[:1] + "." if employee2.pi.user.middle_name else "", employee2.pi.user.last_name)

        employee3 = Empprofile.objects.filter(id=employee.section.div.div_chief_id).first()
        division_chief = "{} {} {}".format(employee3.pi.user.first_name, employee3.pi.user.middle_name[:1] + "." if employee3.pi.user.middle_name else "", employee3.pi.user.last_name)
    return JsonResponse({'fullname': fullname, 'position': position, 'area': area,
                         'empstatus': empstatus, 'project': project, 'id_number': id_number, 'date': today.strftime('%m/%d/%Y'),
                         'supervisor': supervisor, 'division_chief': division_chief})