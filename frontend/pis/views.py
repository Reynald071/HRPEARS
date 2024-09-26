from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.forms import SchoolForm, DegreeForm, HonorsForm, EligibilityForm, PositionForm, EmpstatusForm, \
    OrganizationForm, TrainingtitleForm, HobbiesForm, NonacadForm
from backend.models import AuthUser, Personalinfo, ExtensionName, Position, Empstatus, Empprofile
from frontend.models import Address, Deductionnumbers, PdsUpdateTracking, Province, Bloodtype, Countries, Civilstatus, \
    City, Brgy, Children, Familybackground, Educationbackground, Educationlevel, Honors, Degree, School, Civilservice, \
    Eligibility, Workexperience, Voluntary, Organization, Training, Trainingtype, Trainingtitle, Skills, Recognition, \
    Membership, Hobbies, Nonacad, Additional, Reference, Workhistory, Workexsheet, IncaseOfEmergency, Course
from frontend.templatetags.tags import gamify


@login_required
def personal_info(request):
    if request.method == "POST":
        AuthUser.objects.filter(id=request.user.id).update(
            first_name=request.POST.get('fname').upper(),
            last_name=request.POST.get('surname').upper(),
            middle_name=request.POST.get('mname').upper(),
            email=request.POST.get('email').lower()
        )

        pds = Personalinfo.objects.filter(id=request.session['pi_id']).update(
            ext_id=request.POST.get('ext'),
            dob=request.POST.get('dob'),
            pob=request.POST.get('pob').upper(),
            gender=request.POST.get('gender'),
            cs_id=request.POST.get('cs'),
            height=request.POST.get('height').upper(),
            weight=request.POST.get('weight').upper(),
            bt_id=request.POST.get('bt'),
            isfilipino=request.POST.get('isfilipino'),
            country_id=request.POST.get('countries'),
            mobile_no=request.POST.get('mobile_no'),
            isdualcitizenship=1 if request.POST.get('isdualcit') == 'on' else 0,
            dc_bybirth=1 if request.POST.get('isbybirth') == 'on' else 0,
            dc_bynaturalization=1 if request.POST.get('isbynaturalization') == 'on' else 0,
            telephone_no=request.POST.get('telephone_no').upper())

        check_address = Address.objects.filter(pi_id=request.session['pi_id'])

        if check_address:
            Address.objects.filter(pi_id=request.session['pi_id']).update(
                ra_house_no=request.POST.get('ra_house_no').upper(),
                ra_street=request.POST.get('ra_street').upper(),
                ra_village=request.POST.get('ra_village').upper(),
                ra_prov_code=None if request.POST.get('ra_prov_code') == '' else request.POST.get('ra_prov_code'),
                ra_city=request.POST.get('ra_city'),
                ra_brgy=request.POST.get('ra_brgy'),
                ra_zipcode=request.POST.get('ra_zipcode').upper(),
                pa_house_no=request.POST.get('pa_house_no').upper(),
                pa_street=request.POST.get('pa_street').upper(),
                pa_village=request.POST.get('pa_village').upper(),
                pa_prov_code=request.POST.get('pa_prov_code'),
                pa_city=request.POST.get('pa_city'),
                pa_brgy=request.POST.get('pa_brgy'),
                pa_zipcode=request.POST.get('pa_zipcode').upper()
            )
        else:
            Address.objects.create(
                ra_house_no=request.POST.get('ra_house_no').upper(),
                ra_street=request.POST.get('ra_street').upper(),
                ra_village=request.POST.get('ra_village').upper(),
                ra_prov_code=None if request.POST.get('ra_prov_code') == '' else request.POST.get('ra_prov_code'),
                ra_city=request.POST.get('ra_city'),
                ra_brgy=request.POST.get('ra_brgy'),
                ra_zipcode=request.POST.get('ra_zipcode').upper(),
                pa_house_no=request.POST.get('pa_house_no').upper(),
                pa_street=request.POST.get('pa_street').upper(),
                pa_village=request.POST.get('pa_village').upper(),
                pa_prov_code=request.POST.get('pa_prov_code'),
                pa_city=request.POST.get('pa_city'),
                pa_brgy=request.POST.get('pa_brgy'),
                pa_zipcode=request.POST.get('pa_zipcode').upper(),
                pi_id=request.session['pi_id']
            )

        check_num = Deductionnumbers.objects.filter(pi_id=request.session['pi_id'])

        if check_num:
            Deductionnumbers.objects.filter(pi_id=request.session['pi_id']).update(
                gsis_no=request.POST.get('gsis_no').upper() if request.POST.get('gsis_no') else "N/A",
                pagibig_no=request.POST.get('pagibig_no').upper(),
                philhealth_no=request.POST.get('philhealth_no').upper(),
                sss_no=request.POST.get('sss_no').upper(),
                tin_no=request.POST.get('tin_no').upper())
        else:
            Deductionnumbers.objects.create(
                gsis_no=request.POST.get('gsis_no').upper(),
                pagibig_no=request.POST.get('pagibig_no').upper(),
                philhealth_no=request.POST.get('philhealth_no').upper(),
                sss_no=request.POST.get('sss_no').upper(),
                tin_no=request.POST.get('tin_no').upper(),
                pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=1)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=1)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=1,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 1
        gamify(20, request.session['emp_id'])
        return JsonResponse({'data': 'success'})

    address = Address.objects.filter(pi_id=request.session['pi_id']).first()
    if address:
        context = {
            'pds': Personalinfo.objects.filter(user_id=request.user.id).first(),
            'ext': ExtensionName.objects.all().order_by('name'),
            'prov': Province.objects.all().order_by('name'),
            'bt': Bloodtype.objects.all().order_by('name'),
            'countries': Countries.objects.all().order_by('name'),
            'cs': Civilstatus.objects.all().order_by('name'),
            'numbers': Deductionnumbers.objects.filter(pi_id=request.session['pi_id']).first(),
            'pa_city': City.objects.filter(prov_code=address.pa_prov_code).order_by('name'),
            'ra_city': City.objects.filter(prov_code=address.ra_prov_code).order_by('name'),
            'pa_brgy': Brgy.objects.filter(city_code=address.pa_city).order_by('name'),
            'ra_brgy': Brgy.objects.filter(city_code=address.ra_city).order_by('name'),
            'address': Address.objects.filter(pi_id=request.session['pi_id']).first(),
            'tab_parent': 'Employee Data',
            'tab_child': 'Personal Data Sheet',
            'tab_title': 'Personal Information',
            'title': 'profile',
            'sub_title': 'pds',
            'sub_sub_title': 'personal_info'
        }
    else:
        context = {
            'pds': Personalinfo.objects.filter(user_id=request.user.id).first(),
            'ext': ExtensionName.objects.all().order_by('name'),
            'prov': Province.objects.all().order_by('name'),
            'bt': Bloodtype.objects.all().order_by('name'),
            'countries': Countries.objects.all().order_by('name'),
            'cs': Civilstatus.objects.all().order_by('name'),
            'numbers': Deductionnumbers.objects.filter(pi_id=request.session['pi_id']).first(),
            'address': Address.objects.filter(pi_id=request.session['pi_id']).first(),
            'tab_parent': 'Employee Data',
            'tab_child': 'Personal Data Sheet',
            'tab_title': 'Personal Information',
            'title': 'profile',
            'sub_title': 'pds',
            'sub_sub_title': 'personal_info'
        }
    return render(request, "frontend/pis/personal_info.html", context)


@csrf_exempt
@login_required
def show_city(request):
    if request.POST.get('prov_code') == "":
        return JsonResponse({'error': "ERROR!"})
    else:
        city = City.objects.all().filter(prov_code=request.POST.get('prov_code')).order_by('name')
        data = [dict(id=row.code, city_name=row.name) for row in city]
        return JsonResponse({'data': data})


@csrf_exempt
@login_required
def show_brgy(request):
    if request.POST.get('city_code') == "":
        return JsonResponse({'error': "ERROR!"})
    else:
        brgy = Brgy.objects.all().filter(city_code=request.POST.get('city_code')).order_by('name')
        data = [dict(id=row.id, brgy_name=row.name) for row in brgy]
        return JsonResponse({'data': data})


@csrf_exempt
@login_required()
def family_background(request):
    if request.method == 'POST':
        childrens = request.POST.getlist('children[]')
        birth = request.POST.getlist('birth[]')

        data = dict(zip(childrens, birth))
        count = Children.objects.filter(pi_id=request.session['pi_id'])

        store = [row.id for row in count]
        if count:
            y = 1
            x = 0
            for row in data.items():
                if y > len(count):
                    Children.objects.create(
                        child_fullname=row[0].upper(),
                        child_dob=row[1],
                        pi_id=request.session['pi_id'])
                else:
                    Children.objects.filter(id=store[x]).update(
                        child_fullname=row[0].upper(),
                        child_dob=row[1],
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in data.items():
                Children.objects.create(
                    child_fullname=row[0].upper(),
                    child_dob=row[1],
                    pi_id=request.session['pi_id'])

        check_family = Familybackground.objects.filter(pi_id=request.session['pi_id'])
        if check_family:
            Familybackground.objects.filter(pi_id=request.session['pi_id']).update(
                sp_surname=request.POST.get('sp_surname').upper(),
                sp_fname=request.POST.get('sp_fname').upper(),
                sp_mname=request.POST.get('sp_mname').upper(),
                sp_ext_id=request.POST.get('sp_ext'),
                sp_occupation=request.POST.get('sp_occupation').upper(),
                sp_employer=request.POST.get('sp_employer').upper(),
                sp_business=request.POST.get('sp_business').upper(),
                sp_telephone=request.POST.get('sp_telephone').upper(),
                f_surname=request.POST.get('f_surname').upper(),
                f_fname=request.POST.get('f_fname').upper(),
                f_mname=request.POST.get('f_mname').upper(),
                f_ext_id=request.POST.get('f_ext'),
                m_surname=request.POST.get('m_surname').upper(),
                m_fname=request.POST.get('m_fname').upper(),
                m_mname=request.POST.get('m_mname').upper())

        else:
            Familybackground.objects.create(
                sp_surname=request.POST.get('sp_surname').upper(),
                sp_fname=request.POST.get('sp_fname').upper(),
                sp_mname=request.POST.get('sp_mname').upper(),
                sp_ext_id=request.POST.get('sp_ext'),
                sp_occupation=request.POST.get('sp_occupation').upper(),
                sp_employer=request.POST.get('sp_employer').upper(),
                sp_business=request.POST.get('sp_business').upper(),
                sp_telephone=request.POST.get('sp_telephone').upper(),
                f_surname=request.POST.get('f_surname').upper(),
                f_fname=request.POST.get('f_fname').upper(),
                f_mname=request.POST.get('f_mname').upper(),
                f_ext_id=request.POST.get('f_ext'),
                m_surname=request.POST.get('m_surname').upper(),
                m_fname=request.POST.get('m_fname').upper(),
                m_mname=request.POST.get('m_mname').upper(),
                pi_id=request.session['pi_id'])

        exists = IncaseOfEmergency.objects.filter(pi_id=request.session['pi_id'])
        if exists:
            exists.update(
                contact_name=request.POST.get('ioe').title() if request.POST.get('ioe') != "Others" else request.POST.get('ioe_others').title(),
                contact_number=request.POST.get('ioe_no'),
                is_others=0 if request.POST.get('ioe') != "Others" else 1
            )
        else:
            IncaseOfEmergency.objects.create(
                pi_id=request.session['pi_id'],
                contact_name=request.POST.get('ioe').title() if request.POST.get('ioe') != "Others" else request.POST.get('ioe_others').title(),
                contact_number=request.POST.get('ioe_no'),
                is_others=0 if request.POST.get('ioe') != "Others" else 1
            )

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=2)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=2)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=2,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 1
        gamify(20, request.session['emp_id'])
        return JsonResponse({'data': 'success'})

    context = {
        'ext': ExtensionName.objects.all().order_by('id'),
        'family': Familybackground.objects.filter(pi_id=request.session['pi_id']).first(),
        'children': Children.objects.filter(pi_id=request.session['pi_id']),
        'incase_of_emergency': IncaseOfEmergency.objects.filter(pi_id=request.session['pi_id']).first(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Family Background',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'family_background'
    }
    return render(request, 'frontend/pis/family_background.html', context)


@csrf_exempt
@login_required
def show_children(request):
    child = Children.objects.all().filter(pi_id=request.session['pi_id'])
    data = [dict(child_fullname=row.child_fullname, child_dob=row.child_dob) for row in child]
    return JsonResponse({'data': data})


@csrf_exempt
@login_required
def remove_children(request):
    Children.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def educational_background(request):
    if request.method == "POST":
        level = request.POST.getlist('level[]')
        school = request.POST.getlist('school[]')
        degree = request.POST.getlist('degree[]')
        period_from = request.POST.getlist('from[]')
        period_to = request.POST.getlist('to[]')
        unit = request.POST.getlist('unit[]')
        year = request.POST.getlist('year[]')
        hon = request.POST.getlist('hon[]')

        data = [
            {'level': l, 'school': s, 'degree': d, 'period_from': fr, 'period_to': to, 'unit': u, 'year': y, 'hon': h}
            for l, s, d, fr, to, u, y, h in zip(level, school, degree, period_from, period_to, unit, year, hon)]

        check = Educationbackground.objects.filter(pi_id=request.session['pi_id'])

        store = [row.id for row in check]
        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Educationbackground.objects.create(
                        level_id=row['level'],
                        school_id=row['school'],
                        degree_id=row['degree'],
                        period_from=row['period_from'],
                        period_to=row['period_to'],
                        units_earned=row['unit'],
                        year_graduated=row['year'],
                        hon_id=row['hon'],
                        pi_id=request.session['pi_id'])
                else:
                    Educationbackground.objects.filter(id=store[x]).update(
                        level_id=row['level'],
                        school_id=row['school'],
                        degree_id=row['degree'],
                        period_from=row['period_from'],
                        period_to=row['period_to'],
                        units_earned=row['unit'],
                        year_graduated=row['year'],
                        hon_id=row['hon'],
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in data:
                Educationbackground.objects.create(
                    level_id=row['level'],
                    school_id=row['school'],
                    degree_id=row['degree'],
                    period_from=row['period_from'],
                    period_to=row['period_to'],
                    units_earned=row['unit'],
                    year_graduated=row['year'],
                    hon_id=row['hon'],
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=3)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=3)).update(date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=3,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 1
        gamify(20, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'level': Educationlevel.objects.all(),
        'hon': Honors.objects.filter((Q(hon_status=0) & Q(pi_id=request.session['pi_id'])) | Q(hon_status=1)).order_by('hon_name'),
        'course': Degree.objects.filter((Q(deg_status=0) & Q(pi_id=request.session['pi_id'])) | Q(deg_status=1)).order_by('degree_name'),
        'school': School.objects.filter((Q(school_status=0) & Q(pi_id=request.session['pi_id'])) | Q(school_status=1)).order_by(
            'school_name'),
        'educ': Educationbackground.objects.filter(pi_id=request.session['pi_id']).order_by('level_id', 'period_to'),
        'form_school': SchoolForm(),
        'form_degree': DegreeForm(),
        'form_honor': HonorsForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Educational Background',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'educational_background'
    }
    return render(request, 'frontend/pis/educational_background.html', context)


@csrf_exempt
@login_required
def delete_education(request):
    Educationbackground.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)

        if form.is_valid():
            check = School.objects.filter(Q(school_name=form.cleaned_data['school_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This school is already added.'})
            else:
                school = form.save(commit=False)
                school.school_status = 1 if request.user.id == 1 else 0
                school.pi_id = request.session['pi_id']
                school.save()
                return JsonResponse({'error': False, 'school_id': school.id, 'school_name': school.school_name})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})


@login_required
def add_degree(request):
    if request.method == "POST":
        form = DegreeForm(request.POST)

        if form.is_valid():
            check = Degree.objects.filter(Q(degree_name=form.cleaned_data['degree_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This degree is already added.'})
            else:
                degree = form.save(commit=False)
                degree.deg_status = 1 if request.user.id == 1 else 0
                degree.pi_id = request.session['pi_id']
                degree.save()
                return JsonResponse({'error': False, 'degree_id': degree.id, 'degree_name': degree.degree_name})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})


@login_required
def add_honor(request):
    if request.method == "POST":
        form = HonorsForm(request.POST)

        if form.is_valid():
            check = Honors.objects.filter(Q(hon_name=form.cleaned_data['hon_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This scholarship/academic honor is already added.'})
            else:
                hon = form.save(commit=False)
                hon.hon_status = 1 if request.user.id == 1 else 0
                hon.pi_id = request.session['pi_id']
                hon.save()
                return JsonResponse({'error': False, 'hon_id': hon.id, 'hon_name': hon.hon_name})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})


@login_required
def civil_service(request):
    if request.method == "POST":
        el = request.POST.getlist('el[]')
        course = request.POST.getlist('course[]')
        rating = request.POST.getlist('rating[]')
        date_exam = request.POST.getlist('date_exam[]')
        place = request.POST.getlist('place[]')
        number = request.POST.getlist('number[]')
        date_val = request.POST.getlist('date_val[]')

        data = [{'el': e, 'course': c, 'rating': r, 'date_exam': de, 'place': p, 'number': n, 'date_val': dv}
                for e,c, r, de, p, n, dv in zip(el, course, rating, date_exam, place, number, date_val)]

        check = Civilservice.objects.filter(pi_id=request.session['pi_id'])

        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Civilservice.objects.create(
                        el_id=row['el'],
                        cs_rating=row['rating'],
                        cs_dateexam=row['date_exam'],
                        cs_place=row['place'],
                        cs_number=row['number'],
                        cs_date_val=row['date_val'],
                        pi_id=request.session['pi_id'],
                        course_id=row['course']
                    )
                else:
                    Civilservice.objects.filter(id=store[x]).update(
                        el_id=row['el'],
                        cs_rating=row['rating'],
                        cs_dateexam=row['date_exam'],
                        cs_place=row['place'],
                        cs_number=row['number'],
                        cs_date_val=row['date_val'],
                        pi_id=request.session['pi_id'],
                        course_id=row['course']
                    )
                    y += 1
                    x += 1
        else:
            for row in data:
                Civilservice.objects.create(
                    el_id=row['el'],
                    cs_rating=row['rating'],
                    cs_dateexam=row['date_exam'],
                    cs_place=row['place'],
                    cs_number=row['number'],
                    cs_date_val=row['date_val'],
                    pi_id=request.session['pi_id'],
                    course_id=row['course']
                )

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=4)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=4)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=4,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 2
        gamify(21, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'el': Eligibility.objects.filter((Q(el_status=0) & Q(pi_id=request.session['pi_id'])) | Q(el_status=1)).order_by('el_name'),
        'civil': Civilservice.objects.filter(pi_id=request.session['pi_id']),
        'course': Course.objects.filter(Q(status=1) | Q(upload_by_id=request.session['pi_id'])),
        'form': EligibilityForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Civil Service Eligibility',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'civil_service'
    }
    return render(request, 'frontend/pis/civil_service.html', context)


@login_required
def add_pds_course(request):
    if request.method == "POST":
        Course.objects.create(
            name=request.POST.get('course'),
            status=0,
            upload_by_id=request.session['pi_id']
        )

        return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
def delete_civil_service(request):
    Civilservice.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_eligibility(request):
    if request.method == "POST":
        form = EligibilityForm(request.POST)

        if form.is_valid():
            check = Eligibility.objects.filter(Q(el_name=form.cleaned_data['el_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This eligibility is already added.'})
            else:
                el = form.save(commit=False)
                el.el_status = 1 if request.user.id == 1 else 0
                el.pi_id = request.session['pi_id']
                el.save()
                return JsonResponse({'error': False, 'el_id': el.id, 'el_name': el.el_name})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})


@login_required
def work_experience(request):
    if request.method == "POST":
        inc_from = request.POST.getlist('inc_from[]')
        inc_to = request.POST.getlist('inc_to[]')
        position = request.POST.getlist('position[]')
        company = request.POST.getlist('company[]')
        salary = request.POST.getlist('salary[]')
        sg_step = request.POST.getlist('sg_step[]')
        app_status = request.POST.getlist('as[]')
        gs = request.POST.getlist('gs[]')

        data = [{'inc_from': ic_fr, 'inc_to': ic_to, 'position': p, 'company': c, 'salary': s, 'sg_step': sg,
                 'app_status': aps, 'gs': g}
                for ic_fr, ic_to, p, c, s, sg, aps, g in
                zip(inc_from, inc_to, position, company, salary, sg_step, app_status, gs)]

        check = Workexperience.objects.filter(pi_id=request.session['pi_id'])
        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Workexperience.objects.create(
                        we_from=row['inc_from'],
                        we_to=row['inc_to'],
                        position_name=row['position'],
                        company=row['company'],
                        salary_rate=row['salary'].replace(',', ''),
                        sg_step=row['sg_step'],
                        empstatus_id=row['app_status'],
                        govt_service=row['gs'],
                        pi_id=request.session['pi_id'])
                else:
                    Workexperience.objects.filter(id=store[x]).update(
                        we_from=row['inc_from'],
                        we_to=row['inc_to'],
                        position_name=row['position'],
                        company=row['company'],
                        salary_rate=row['salary'].replace(',', ''),
                        sg_step=row['sg_step'],
                        empstatus_id=row['app_status'],
                        govt_service=row['gs'],
                        pi_id=request.session['pi_id'])

                    y += 1
                    x += 1
        else:
            for row in data:
                Workexperience.objects.create(
                    we_from=row['inc_from'],
                    we_to=row['inc_to'],
                    position_name=row['position'],
                    company=row['company'],
                    salary_rate=row['salary'].replace(',', ''),
                    sg_step=row['sg_step'],
                    empstatus_id=row['app_status'],
                    govt_service=row['gs'],
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=5)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=5)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=5,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 2
        gamify(21, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'position': Position.objects.filter((Q(status=0) & Q(upload_by_id=request.user.id)) | Q(status=1)).order_by('name'),
        'app_status': Empstatus.objects.filter((Q(status=0) & Q(upload_by_id=request.user.id)) | Q(status=1)).order_by('name'),
        'work': Workexperience.objects.filter(pi_id=request.session['pi_id']).order_by('-we_to'),
        'form_pt': PositionForm(),
        'form_empstatus': EmpstatusForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Work Experience',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'work_experience'
    }
    return render(request, 'frontend/pis/work_experience.html', context)


@csrf_exempt
@login_required
def delete_workexperience(request):
    Workexperience.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_position(request):
    if request.method == "POST":
        form = PositionForm(request.POST)

        if form.is_valid():
            check = Position.objects.filter(Q(name=form.cleaned_data['name']) & Q(upload_by_id=request.user.id))
            if check:
                return JsonResponse({'msg': 'This position title is already added.'})
            else:
                pt = form.save(commit=False)
                pt.status = 1 if request.user.id == 1 else 0
                pt.upload_by_id = request.user.id
                pt.save()
                return JsonResponse({'error': False, 'pos_id': pt.id, 'name': pt.name})


@login_required
def voluntary(request):
    if request.method == "POST":
        org = request.POST.getlist('org[]')
        inc_from = request.POST.getlist('inc_from[]')
        inc_to = request.POST.getlist('inc_to[]')
        num_hours = request.POST.getlist('num_hours[]')
        now = request.POST.getlist('now[]')

        data = [{'org': o, 'inc_from': ic_fr, 'inc_to': ic_to, 'num_hours': nh, 'now': n}
                for o, ic_fr, ic_to, nh, n in zip(org, inc_from, inc_to, num_hours, now)]

        check = Voluntary.objects.filter(pi_id=request.session['pi_id'])
        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Voluntary.objects.create(
                        organization=row['org'],
                        vol_from=row['inc_from'],
                        vol_to=row['inc_to'],
                        vol_hours=row['num_hours'],
                        now=row['now'],
                        pi_id=request.session['pi_id'])
                else:
                    Voluntary.objects.filter(id=store[x]).update(
                        organization=row['org'],
                        vol_from=row['inc_from'],
                        vol_to=row['inc_to'],
                        vol_hours=row['num_hours'],
                        now=row['now'],
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in data:
                Voluntary.objects.create(
                    organization=row['org'],
                    vol_from=row['inc_from'],
                    vol_to=row['inc_to'],
                    vol_hours=row['num_hours'],
                    now=row['now'],
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=6)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=6)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=6,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 3
        gamify(22, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'org': Organization.objects.filter((Q(org_status=0) & Q(pi_id=request.session['pi_id'])) | Q(org_status=1)).order_by('org_name'),
        'voluntary': Voluntary.objects.filter(pi_id=request.session['pi_id']),
        'form_org': OrganizationForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Voluntary Work',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'voluntary'
    }
    return render(request, 'frontend/pis/voluntary.html', context)


@csrf_exempt
@login_required
def delete_voluntary(request):
    Voluntary.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_org(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)

        if form.is_valid():
            check = Organization.objects.filter(Q(org_name=form.cleaned_data['org_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This organization name is already added.'})
            else:
                org = form.save(commit=False)
                org.org_status = 1 if request.user.id == 1 else 0
                org.pi_id = request.session['pi_id']
                org.save()
                return JsonResponse({'error': False, 'org_id': org.id, 'org_name': org.org_name})


@login_required
def training(request):
    if request.method == "POST":
        training = request.POST.getlist('training[]')
        inc_from = request.POST.getlist('inc_from[]')
        inc_to = request.POST.getlist('inc_to[]')
        num_hours = request.POST.getlist('num_hours[]')
        trainingtype = request.POST.getlist('type[]')
        conducted = request.POST.getlist('conducted[]')

        data = [{'training': t, 'inc_from': ic_fr, 'inc_to': ic_to, 'num_hours': nh, 'trainingtype': tt, 'conducted': c}
                for t, ic_fr, ic_to, nh, tt, c in zip(training, inc_from, inc_to, num_hours, trainingtype, conducted)]

        check = Training.objects.filter(pi_id=request.session['pi_id'])
        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Training.objects.create(
                        training=row['training'],
                        tr_from=row['inc_from'],
                        tr_to=row['inc_to'],
                        tr_hours=row['num_hours'],
                        training_type=row['trainingtype'],
                        conducted=row['conducted'],
                        pi_id=request.session['pi_id'])
                else:
                    Training.objects.filter(id=store[x]).update(
                        training=row['training'],
                        tr_from=row['inc_from'],
                        tr_to=row['inc_to'],
                        tr_hours=row['num_hours'],
                        training_type=row['trainingtype'],
                        conducted=row['conducted'],
                        pi_id=request.session['pi_id'])
                    x += 1
                    y += 1
        else:
            for row in data:
                Training.objects.create(
                    training=row['training'],
                    tr_from=row['inc_from'],
                    tr_to=row['inc_to'],
                    tr_hours=row['num_hours'],
                    training_type=row['trainingtype'],
                    conducted=row['conducted'],
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=7)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=7)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=7,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 3
        gamify(22, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'trainingtype': Trainingtype.objects.all(),
        'training': Trainingtitle.objects.filter((Q(tt_status=0) & Q(pi_id=request.session['pi_id'])) | Q(tt_status=1)).order_by('tt_name'),
        'data': Training.objects.filter(pi_id=request.session['pi_id']).order_by('-tr_to'),
        'form': TrainingtitleForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Trainings Attended',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'training'
    }
    return render(request, 'frontend/pis/training.html', context)


@csrf_exempt
@login_required
def delete_training(request):
    Training.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_trainingtitle(request):
    if request.method == "POST":
        form = TrainingtitleForm(request.POST)

        if form.is_valid():
            check = Trainingtitle.objects.filter(Q(tt_name=form.cleaned_data['tt_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This training title is already added.'})
            else:
                tt = form.save(commit=False)
                tt.tt_status = 1 if request.user.id == 1 else 0
                tt.pi_id = request.session['pi_id']
                tt.save()
                return JsonResponse({'error': False, 'tt_id': tt.id, 'tt_name': tt.tt_name})


@login_required
def others(request):
    if request.method == "POST":
        skills = request.POST.getlist('skills[]')
        nonacad = request.POST.getlist('nonacad[]')
        org = request.POST.getlist('org[]')

        check_skills = Skills.objects.filter(pi_id=request.session['pi_id'])
        store_skills = [row.id for row in check_skills]
        check_nonacad = Recognition.objects.filter(pi_id=request.session['pi_id'])
        store_nonacad = [row.id for row in check_nonacad]

        check_membership = Membership.objects.filter(pi_id=request.session['pi_id'])
        store_membership = [row.id for row in check_membership]

        if check_skills:
            y = 1
            x = 0
            for row in skills:
                if y > len(check_skills):
                    Skills.objects.create(
                        hob_id=row,
                        pi_id=request.session['pi_id'])
                else:
                    Skills.objects.filter(id=store_skills[x]).update(
                        hob_id=row,
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in skills:
                Skills.objects.create(
                    hob_id=row,
                    pi_id=request.session['pi_id'])

        if check_nonacad:
            y = 1
            x = 0
            for row in nonacad:
                if y > len(check_nonacad):
                    Recognition.objects.create(
                        na_id=row,
                        pi_id=request.session['pi_id'])
                else:
                    Recognition.objects.filter(id=store_nonacad[x]).update(
                        na_id=row,
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in nonacad:
                Recognition.objects.create(
                    na_id=row,
                    pi_id=request.session['pi_id'])

        if check_membership:
            y = 1
            x = 0
            for row in org:
                if y > len(check_membership):
                    Membership.objects.create(
                        org_id=row,
                        pi_id=request.session['pi_id'])
                else:
                    Membership.objects.filter(id=store_membership[x]).update(
                        org_id=row,
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in org:
                Membership.objects.create(
                    org_id=row,
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=8)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=8)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=8,
                pi_id=request.session['pi_id']
            )
        # Save points for personal data sheet page 3
        gamify(22, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'hobbies': Hobbies.objects.filter((Q(pi_id=request.session['pi_id']) & Q(hob_status=0)) | Q(hob_status=1)).order_by('hob_name'),
        'nonacad': Nonacad.objects.filter((Q(pi_id=request.session['pi_id']) & Q(na_status=0)) | Q(na_status=1)).order_by('na_name'),
        'org': Organization.objects.filter((Q(pi_id=request.session['pi_id']) & Q(org_status=0)) | Q(org_status=1)).order_by('org_name'),
        'skills': Skills.objects.filter(pi_id=request.session['pi_id']),
        'reg': Recognition.objects.filter(pi_id=request.session['pi_id']),
        'membership': Membership.objects.filter(pi_id=request.session['pi_id']),
        'form_hob': HobbiesForm(),
        'form_na': NonacadForm(),
        'form_org': OrganizationForm(),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Other Information',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'other'
    }
    return render(request, 'frontend/pis/others.html', context)


@csrf_exempt
@login_required
def delete_skills(request):
    Skills.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
def delete_acad(request):
    Recognition.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
def delete_membership(request):
    Membership.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def add_hobbies(request):
    if request.method == "POST":
        form = HobbiesForm(request.POST)

        if form.is_valid():
            check = Hobbies.objects.filter(Q(hob_name=form.cleaned_data['hob_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This skill/hobby is already added.'})
            else:
                hob = form.save(commit=False)
                hob.hob_status = 1 if request.user.id == 1 else 0
                hob.pi_id = request.session['pi_id']
                hob.save()
                return JsonResponse({'error': False, 'hob_id': hob.id, 'hob_name': hob.hob_name})


@login_required
def add_recog(request):
    if request.method == "POST":
        form = NonacadForm(request.POST)

        if form.is_valid():
            check = Nonacad.objects.filter(Q(na_name=form.cleaned_data['na_name']) & Q(pi_id=request.session['pi_id']))
            if check:
                return JsonResponse({'msg': 'This non-academic/recognition is already added.'})
            else:
                na = form.save(commit=False)
                na.na_status = 1 if request.user.id == 1 else 0
                na.pi_id = request.session['pi_id']
                na.save()
                return JsonResponse({'error': False, 'na_id': na.id, 'na_name': na.na_name})


@login_required
def additional_information(request):
    if request.method == "POST":
        answers = [request.POST.get('q1'), request.POST.get('q2'), request.POST.get('q3'), request.POST.get('q4'),
                  request.POST.get('q4'), request.POST.get('q5'), request.POST.get('q6'), request.POST.get('q7'),
                  request.POST.get('q8'), request.POST.get('q9'), request.POST.get('q10'), request.POST.get('q11'),
                  request.POST.get('q12')]

        answer_detail = ['', request.POST.get('answer1'), request.POST.get('answer2'), request.POST.get('answer3'), request.POST.get('answer4'),
                  request.POST.get('answer5'), request.POST.get('answer6'), request.POST.get('answer7'), request.POST.get('answer8'),
                  request.POST.get('answer9'), request.POST.get('answer10'), request.POST.get('answer11'), request.POST.get('answer12')]

        check = Additional.objects.filter(pi_id=request.session['pi_id'])
        if check:
            store = [row.id for row in check]
            count = 0
            for row in store:
                Additional.objects.filter(id=row).update(
                    question=answers[count],
                    answers=answer_detail[count],
                    ad_status=1,
                    pi_id=request.session['pi_id'])
                count = count + 1
        else:
            count = 0
            for row in answers:
                Additional.objects.create(
                    question=answers[count],
                    answers=answer_detail[count],
                    ad_status=1,
                    pi_id=request.session['pi_id'])
                count = count + 1

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=9)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=9)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=9,
                pi_id=request.session['pi_id']
            )

        # Save points for personal data sheet page 4
        gamify(23, request.session['emp_id'])
        return JsonResponse({'data': 'success'})

    additional = Additional.objects.filter(pi_id=request.session['pi_id'])
    data = [dict(question=row.question, answers=row.answers) for row in additional]
    context = {
        'additional': data,
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'Additional Information',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'additional'
    }
    return render(request, 'frontend/pis/additional.html', context)


@login_required
def attachment(request):
    if request.method == "POST":
        name = request.POST.getlist('name[]')
        address = request.POST.getlist('address[]')
        tel_no = request.POST.getlist('tel_no[]')

        data = [{'name': n, 'address': a, 'tel_no': tn}
                for n, a, tn in zip(name, address, tel_no)]

        check = Reference.objects.filter(pi_id=request.session['pi_id'])
        store = [row.id for row in check]

        if check:
            y = 1
            x = 0
            for row in data:
                if y > len(check):
                    Reference.objects.create(
                        name=row['name'],
                        address=row['address'],
                        tel_no=row['tel_no'],
                        pi_id=request.session['pi_id'])
                else:
                    Reference.objects.filter(id=store[x]).update(
                        name=row['name'],
                        address=row['address'],
                        tel_no=row['tel_no'],
                        pi_id=request.session['pi_id'])
                    y += 1
                    x += 1
        else:
            for row in data:
                Reference.objects.create(
                    name=row['name'],
                    address=row['address'],
                    tel_no=row['tel_no'],
                    pi_id=request.session['pi_id'])

        check_upd_tracking = PdsUpdateTracking.objects.filter(
            Q(pi_id=request.session['pi_id']) & Q(pis_config_id=10)).first()
        if check_upd_tracking:
            PdsUpdateTracking.objects.filter(Q(pi_id=request.session['pi_id']) & Q(pis_config_id=10)).update(
                date=datetime.now())
        else:
            PdsUpdateTracking.objects.create(
                pis_config_id=10,
                pi_id=request.session['pi_id']
            )

        Empprofile.objects.filter(id=request.session['emp_id']).update(
            date_id_issuance=request.POST.get('date'),
            place_id_issuance=request.POST.get('place')
        )

        # Save points for personal data sheet page 4
        gamify(23, request.session['emp_id'])
        return JsonResponse({'data': 'success'})
    context = {
        'reference': Reference.objects.filter(pi_id=request.session['pi_id']),
        'tab_parent': 'Employee Data',
        'tab_child': 'Personal Data Sheet',
        'tab_title': 'References',
        'title': 'profile',
        'sub_title': 'pds',
        'sub_sub_title': 'reference'
    }
    return render(request, 'frontend/pis/attachment.html', context)


@csrf_exempt
@login_required
def delete_reference(request):
    Reference.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@login_required
def work_experience_sheet(request):
    data = Workexperience.objects.filter(Q(pi_id=request.session['pi_id']) & (
                Q(company__icontains='DSWD') | Q(company__icontains='Department of Social Welfare and Development, Field Office Caraga')
                | Q(company__icontains='Department of Social Welfare and Development')
    ))

    data.update(
        company='Department of Social Welfare and Development, Field Office Caraga'.upper()
    )

    for row in data:
        check = Workhistory.objects.filter(we_id=row.id).first()
        if check is None:
            Workhistory.objects.create(
                emp_id=request.session['emp_id'],
                we_id=row.id
            )

    context = {
        'title': 'profile',
        'sub_title': 'work_experience',
    }
    return render(request, "frontend/pis/work_experience_sheet.html", context)


@login_required
def write_wes(request, pk):
    if request.method == "POST":
        check = Workexsheet.objects.filter(wh_id=request.POST.get('wh_id')).first()
        if check:
            Workexsheet.objects.filter(wh_id=request.POST.get('wh_id')).update(
                wh_id=request.POST.get('wh_id'),
                work_form=request.POST.get('content')
            )
        else:
            Workexsheet.objects.create(
                wh_id=request.POST.get('wh_id'),
                work_form=request.POST.get('content')
            )
        return JsonResponse({'data': 'success'})
    context = {
        'work_history': Workhistory.objects.filter(id=pk).first(),
        'work_sheet': Workexsheet.objects.filter(wh_id=pk).first()
    }
    return render(request, "frontend/pis/write_wes.html", context)


@login_required
def print_wes(request):
    context = {
        'work_sheet': Workexsheet.objects.filter(wh__emp_id=request.session['emp_id'])
    }
    return render(request, "frontend/pis/print_wes.html", context)
