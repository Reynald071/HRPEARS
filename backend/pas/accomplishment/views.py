from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from backend.models import Division, Section, Empprofile, Aoa


@login_required
@permission_required('auth.dtr_logs')
def view_accomplishment_report(request):
    if request.method == "POST":
        try:
            checked = request.POST.getlist('checked[]')
            allemp = request.POST.getlist('empid[]')
            data = [{'checked': c, 'allemp': a}
                    for c, a in zip(checked, allemp)]
            selectedempid = []

            for row in data:
                if row['checked'] == 'checked':
                    selectedempid.append(row['allemp'])

            employees = Empprofile.objects.filter(id__in=selectedempid)
            start_date = datetime.strptime(request.POST.get('period_from_hidden'), "%Y-%m-%d")
            end_date = datetime.strptime(request.POST.get('period_to_hidden'), "%Y-%m-%d")
            delta = end_date - start_date
            alldays = list()
            for i in range(delta.days + 1):
                alldays.append(start_date + timedelta(days=i))
            context = {
                'ifcheck': request.POST.get('ifcheck'),
                'employees': employees,
                'start_date': start_date,
                'end_date': end_date,
                'all_days': alldays,
            }
            return render(request, 'backend/pas/accomplishment/print_accomplishment_report.html', context)
        except Exception as e:
            return render(request, 'backend/pas/accomplishment/print_accomplishment_report.html', {'error': "There are some employee that don't have biometric serial key."})

    emp = Empprofile.objects.filter(id=request.session['emp_id']).first()


    section = Section.objects.all()
    division = Division.objects.all()
    aoa = Aoa.objects.all()

    context = {
        'aoa': aoa,
        'section': section,
        'division': division,
        'tab_title': 'Accomplishment Report',
        'title': 'employee',
        'sub_title': 'monitoring',
        'sub_sub_title': 'accomplishment_report',
        'date': datetime.now()
    }
    return render(request, 'backend/pas/accomplishment/view_accomplishment_report.html', context)