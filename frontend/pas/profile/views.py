from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.decorators import method_decorator
from ldap3 import MODIFY_REPLACE
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from backend.convocation.models import ConvocationQRCode
from backend.libraries.pas.forms import UploadPictureForm
from backend.models import Personalinfo, Empprofile, Division, Section, AuthUser, Indiginous, Fundsource, Aoa, Project, \
    Position, Empstatus, HrppmsModeseparation, HrppmsModeaccession, Salarygrade, Stepinc, AuthUserUserPermissions
from backend.pas.transmittal.models import TransmittalNew
from backend.templatetags.tags import convert_string_to_crypto
from frontend.forms import UploadCoverPhotoForm
from frontend.models import Address, Deductionnumbers, Familybackground, Educationbackground, Civilservice, \
    Workexperience, Voluntary, Skills, Recognition, Training, Membership, Additional, Reference, PdsUpdateTracking, \
    PisConfig, Ritopeople, PasAccomplishmentOutputs, SocialMediaAccount, IncaseOfEmergency
from frontend.templatetags.tags import gamify
from portal.active_directory import searchSamAccountName
from portal.decorator import ajax_required


@login_required
def my_profile(request):
    emp = Empprofile.objects.filter(pi_id=request.session['pi_id']).values('picture').first()
    request.session['picture'] = emp['picture']
    obj = get_object_or_404(Empprofile, pk=request.session['emp_id'])
    upload_form = UploadPictureForm(instance=obj)
    upload_cover_photo_form = UploadCoverPhotoForm(instance=obj)
    context = {
        'tab_title': 'My Profile',
        'title': 'profile',
        'sub_title': 'about',
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first(),
        'badges': Paginator(AuthUserUserPermissions.objects.filter(user_id=request.user.id), 3).page(1),
        'all_badges': AuthUserUserPermissions.objects.filter(user_id=request.user.id),
        'upload_form': upload_form,
        'upload_cover_photo_form': upload_cover_photo_form
    }
    return render(request, 'frontend/pas/profile/my_profile.html', context)


@login_required
def transmittal(request):
    context = {
        'title': 'f_documents',
        'sub_title': 'my_transmittal',
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first(),
    }
    return render(request, 'frontend/documents/transmittal.html', context)


@login_required
def view_transmittal(request, pk):
    context = {
        'transmittal': TransmittalNew.objects.filter(id=pk).first()
    }
    return render(request, 'frontend/documents/view_transmittal.html', context)


@login_required
def upload_cover_photo(request):
    obj = get_object_or_404(Empprofile, pk=request.session['emp_id'])
    form = UploadCoverPhotoForm(request.POST, request.FILES, instance=obj)
    if request.method == "POST":
        if form.is_valid():
            cover_photo = form.save(commit=False)
            cover_photo.emp_id = request.session['emp_id']

            # Save points for update/upload cover photo
            gamify(5, request.session['emp_id'])

            cover_photo.save()
            form.save()
    return JsonResponse({'data': 'success', 'msg': 'Your cover photo was updated.', 'cover_photo': obj.cover_photo.url})


@login_required
def settings(request):
    check = ConvocationQRCode.objects.filter(emp_id=request.session['emp_id'])

    if not check:
        employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
        ConvocationQRCode.objects.create(
            emp_id=request.session['emp_id'],
            qrcode=str(convert_string_to_crypto(employee.id_number))
        )

    context = {
        'change_passwordform': PasswordChangeForm(request.user),
        'qrcode': ConvocationQRCode.objects.filter(emp_id=request.session['emp_id']).first()
    }
    return render(request, 'frontend/pas/profile/settings.html', context)


@login_required
def incase_of_emergency(request):
    employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
    if request.method == "POST":
        IncaseOfEmergency.objects.filter(pi_id=employee.pi.id).update(
            contact_name=request.POST.get('contact_name'),
            contact_number=request.POST.get('contact_number')
        )

        # Save points for updating of about info
        gamify(7, request.session['emp_id'])

        return JsonResponse({'data': 'success'})


@login_required
def social_media(request):
    if request.method == "POST":
        exists = SocialMediaAccount.objects.filter(emp_id=request.session['emp_id']).first()
        if exists:
            SocialMediaAccount.objects.filter(emp_id=request.session['emp_id']).update(
                facebook_url=request.POST.get('facebook_url'),
                instagram_url=request.POST.get('instagram_url'),
                twitter_url=request.POST.get('twitter_url')
            )
        else:
            SocialMediaAccount.objects.create(
                emp_id=request.session['emp_id'],
                facebook_url=request.POST.get('facebook_url'),
                instagram_url=request.POST.get('instagram_url'),
                twitter_url=request.POST.get('twitter_url')
            )

        # Save points for updating of about info
        gamify(7, request.session['emp_id'])

        return JsonResponse({'data': 'success'})


@login_required
def change_password(request):
    if request.method == 'POST':
        # ad = searchSamAccountName(request.session['username'])

        # if ad["status"]:
        check = User.objects.get(username=request.session['username'])
        if check.check_password(request.POST.get('old_password')):
            enc_pwd = '"{}"'.format(request.POST.get('new_password')).encode('utf-16-le')
            # ad["connection"].modify(ad["userDN"], {'unicodePwd': [(MODIFY_REPLACE, [enc_pwd])]})

            AuthUser.objects.filter(username=request.session['username']).update(
                password=make_password(request.POST.get('new_password'))
            )

            return JsonResponse({'success': 'success'})
        else:
            return JsonResponse({'error': 'error'})
        # else:
        #     return JsonResponse({'confirm': 'confirm'})
    return render(request, 'frontend/pas/profile/settings.html')


@login_required
def about(request):
    if request.method == "POST":
        with transaction.atomic():
            Empprofile.objects.filter(id=request.session['emp_id']).update(
                item_number=request.POST.get('item_number'),
                account_number=request.POST.get('account_number'),
                position_id=request.POST.get('position'),
                empstatus_id=request.POST.get('empstatus'),
                project_id=request.POST.get('project'),
                section_id=request.POST.get('section'),
                fundsource_id=request.POST.get('fund_source'),
                aoa_id=request.POST.get('aoa'),
                salary_rate=request.POST.get('salary_rate'),
                salary_grade=request.POST.get('salary_grade'),
                step_inc=request.POST.get('step_inc'),
                dateofcreation_pos=request.POST.get('docp') if request.POST.get('docp') else None,
                designation=request.POST.get('designation'),
                dateof_designation=request.POST.get('dod') if request.POST.get('dod') else None,
                mode_access_id=request.POST.get('mode_access'),
                specialorder_no=request.POST.get('special_order_no'),
                plantilla_psipop=request.POST.get('plantilla'),
                former_incumbent=request.POST.get('former_incumbent'),
                mode_sep_id=request.POST.get('mode_sep'),
                date_vacated=request.POST.get('date_vacated') if request.POST.get('date_vacated') else None,
                remarks_vacated=request.POST.get('remarks_vacated')
            )

            Personalinfo.objects.filter(id=request.session['pi_id']).update(
                type_of_disability=request.POST.get('tod'),
                type_of_indi_id=request.POST.get('tig')
            )

            # Save points for updating of about info
            gamify(7, request.session['emp_id'])

            return JsonResponse({'data': 'success'})
    employee = Empprofile.objects.filter(id=request.session['emp_id']).first()
    context = {
        'employee': employee,
        'division': Division.objects.all(),
        'section': Section.objects.all(),
        'fundsource': Fundsource.objects.filter(status=1).order_by('name'),
        'aoa': Aoa.objects.filter(status=1).order_by('name'),
        'project': Project.objects.filter(status=1).order_by('name'),
        'position': Position.objects.filter(status=1).order_by('name'),
        'empstatus': Empstatus.objects.filter(status=1).order_by('name'),
        'mode_separation': HrppmsModeseparation.objects.filter(status=1).order_by('name'),
        'mode_accession': HrppmsModeaccession.objects.filter(status=1).order_by('name'),
        'sg': Salarygrade.objects.filter(status=1),
        'stepinc': Stepinc.objects.filter(status=1),
        'personal_info': Personalinfo.objects.filter(id=request.session['pi_id']).first(),
        'indi': Indiginous.objects.filter(status=1).order_by('name'),
        'sm': SocialMediaAccount.objects.filter(emp_id=request.session['emp_id']).first(),
        'incase': IncaseOfEmergency.objects.filter(pi_id=employee.pi.id).first()
    }
    return render(request, 'frontend/pas/profile/about.html', context)


@login_required
def activities(request):
    context = {
        'travel_history': Ritopeople.objects.filter(name_id=request.session['emp_id'], detail__rito__status=3).order_by(
            '-detail__inclusive_to')[:4],
        'last_update': PdsUpdateTracking.objects.filter(pi_id=request.session['pi_id']),
        'mobile_no': Personalinfo.objects.filter(id=request.session['pi_id']).first(),
        'pis_config': PisConfig.objects.all(),
        'accomplishment': PasAccomplishmentOutputs.objects.all().filter(emp_id=request.session['emp_id']).order_by(
            '-date_period')[:3]
    }
    return render(request, 'frontend/pas/profile/activities.html', context)


@login_required
def travel_history(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    context = {
        'title': 'profile',
        'sub_title': 'travel_history',
        'tab_parent': 'Employee Data',
        'tab_title': 'Travel History',
        'travel_history': Paginator(
            Ritopeople.objects.filter(name_id=request.session['emp_id'], detail__rito__status=3).order_by(
                '-detail__inclusive_to'), rows).page(page),
    }
    return render(request, 'frontend/pas/profile/travel_history.html', context)


@login_required
def pds_pageone(request, pk):
    pi = Personalinfo.objects.filter(id=pk).first()

    context = {
        'pds': Personalinfo.objects.filter(id=pk).first(),
        'employee': Empprofile.objects.filter(id=request.session['emp_id']).first(),
        'address': Address.objects.filter(pi_id=pi.id).first(),
        'numbers': Deductionnumbers.objects.filter(pi_id=pi.id).first(),
        'family': Familybackground.objects.filter(pi_id=pi.id).first(),
        'eb': Educationbackground.objects.filter(pi_id=pi.id).order_by('level_id'),
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/pds_pageone.html', context)


@login_required
def pds_pagetwo(request, pk):
    context = {
        'civil': Civilservice.objects.filter(pi_id=pk),
        'work': Workexperience.objects.filter(pi_id=pk).order_by('-we_to')[0:29],
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/pds_pagetwo.html', context)


@login_required
def pds_pagethree(request, pk):
    context = {
        'voluntary': Voluntary.objects.filter(pi_id=pk),
        'training': Training.objects.filter(pi_id=pk).order_by('-tr_to')[0:21],
        'skills': Skills.objects.filter(pi_id=pk),
        'nonacad': Recognition.objects.filter(pi_id=pk),
        'membership': Membership.objects.filter(pi_id=pk),
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/pds_pagethree.html', context)


@login_required
def pds_pagefour(request, pk):
    additional = Additional.objects.filter(pi_id=pk)
    data = [dict(question=row.question, answers=row.answers) for row in additional]
    context = {
        'reference': Reference.objects.filter(pi_id=pk),
        'additional': data,
        'date': datetime.now(),
        'employee': Empprofile.objects.filter(pi_id=pk).first(),
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/pds_pagefour.html', context)


@login_required
def pds_pagefive(request, pk):
    date_today = date.today()
    fiveyear_interval_date = datetime.now() - timedelta(days=5 * 365)
    context = {
        'work': Workexperience.objects.filter(pi_id=pk).order_by('-we_to')[29:],
        'training': Training.objects.filter(pi_id=pk, tr_to__range=[fiveyear_interval_date.strftime("%Y-%m-%d"),
                                                                    date_today]).order_by('-tr_to')[21:],
        'date': datetime.now(),
        'pk': pk
    }
    return render(request, 'frontend/pas/profile/pds_pagefive.html', context)


@login_required
def print_pds_pageone(request, pk):
    pi = Personalinfo.objects.filter(id=pk).first()
    emp = Empprofile.objects.filter(pi_id=pk).first()
    context = {
        'pds': Personalinfo.objects.filter(id=pk).first(),
        'employee': Empprofile.objects.filter(id=emp.id).first(),
        'address': Address.objects.filter(pi_id=pi.id).first(),
        'numbers': Deductionnumbers.objects.filter(pi_id=pi.id).first(),
        'family': Familybackground.objects.filter(pi_id=pi.id).first(),
        'education_background': Educationbackground.objects.filter(pi_id=pi.id).order_by('level_id', 'period_to'),
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/print_pds_pageone.html', context)


@login_required
def print_pds_pagetwo(request, pk):
    context = {
        'civil': Civilservice.objects.filter(pi_id=pk),
        'work': Workexperience.objects.filter(pi_id=pk).order_by('-we_to')[0:29],
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/print_pds_pagetwo.html', context)


@login_required
def print_pds_pagethree(request, pk):
    context = {
        'voluntary': Voluntary.objects.filter(pi_id=pk),
        'training': Training.objects.filter(pi_id=pk).order_by('-tr_to')[0:21],
        'skills': Skills.objects.filter(pi_id=pk),
        'nonacad': Recognition.objects.filter(pi_id=pk),
        'membership': Membership.objects.filter(pi_id=pk),
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/print_pds_pagethree.html', context)


@login_required
def print_pds_pagefour(request, pk):
    additional = Additional.objects.filter(pi_id=pk)
    data = [dict(question=row.question, answers=row.answers) for row in additional]
    context = {
        'reference': Reference.objects.filter(pi_id=pk),
        'additional': data,
        'date': datetime.now(),
        'employee': Empprofile.objects.filter(pi_id=pk).first(),
        'pk': pk,
        'date': datetime.now()
    }
    return render(request, 'frontend/pas/profile/print_pds_pagefour.html', context)


@login_required
def print_pds_pagefive(request, pk):
    date_today = date.today()
    fiveyear_interval_date = datetime.now() - timedelta(days=5 * 365)
    context = {
        'work': Workexperience.objects.filter(pi_id=pk).order_by('-we_to')[29:],
        'training': Training.objects.filter(pi_id=pk, tr_to__range=[fiveyear_interval_date.strftime("%Y-%m-%d"),
                                                                    date_today]).order_by('-tr_to')[21:],
        'date': datetime.now(),
        'pk': pk
    }
    return render(request, 'frontend/pas/profile/print_pds_pagefive.html', context)
