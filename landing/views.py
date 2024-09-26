from datetime import datetime, date
import urllib

import requests
import json

from django.db import transaction
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django_mysql.models.functions import SHA1
from mailjet_rest import Client
from portal import settings

from backend.documents.models import DocsIssuancesType, DocsIssuancesFiles
from backend.models import Section, PositionVacancy
from backend.templatetags.tags import get_date_duration_from_now, force_token_decryption
from frontend.models import Faqs, PortalConfiguration, PortalAnnouncements, Province, City, Brgy, Civilstatus, \
    Eligibility
from landing.models import JobApplication, AppEligibility, AppStatus


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('backend-dashboard')
    else:
        website_links = PortalConfiguration.objects.filter(key_name='Website Links').first()
        vacancy = PositionVacancy.objects.filter(
            Q(status=1),
            Q(deadline__gte=date.today()) |
            Q(deadline=None)
        ).order_by('position__name')

        context = {
            'website_links': [row for row in website_links.key_acronym.split(',')],
            'vacancy': vacancy[:4],
            'vacancy_count': vacancy.count() - 4,
            'year': datetime.now().year
        }
        return render(request, "landing/landing_new.html", context)


def announcement_layout(request):
    # get announcements and display in dashboard
    announcements = PortalAnnouncements.objects \
        .filter(is_active=True, announcement_type=None).order_by('is_active', 'is_urgent', 'datetime')
    for announcement in announcements:
        get_date_duration_from_now(announcement.datetime, announcement.id, 10)

    announcements = PortalAnnouncements.objects.filter(is_active=True, announcement_type=None).order_by('is_active', 'is_urgent', 'datetime')

    context = {
        'announcements': announcements
    }

    return render(request, 'landing/announcement_layout.html', context)


def send_message(request):
    if request.method == "POST":
        api_key = 'c2bd3f2d3738a413c83ceb5efcf829f9'
        api_secret = '0c73544d0735d4f53efae833eade432d'
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": request.POST.get('email'),
                    },
                    "To": [
                        {
                            "Email": "phillipemonares@gmail.com",
                        }
                    ],
                    "Subject": request.POST.get('subject'),
                    "HTMLPart": "<p>{}<p> <br> <strong>The My PORTAL Team</strong>".format(request.POST.get('description')),
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return JsonResponse({'data': 'success', 'msg': 'You have successfully sent us a message. We will make sure that your request gets attended to by our staffs as soon as possible. Thank you!'})


def add_request(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            subject = request.POST.get('subject')
            description = request.POST.get('description')
            category = request.POST.get('category')
            subcategory = request.POST.get('subcategory')
            impact = request.POST.get('impact')
            urgency = request.POST.get('urgency')

            params = '{\
                "list_info": {\
                    "row_count": 100,\
                    "get_total_count": true,\
                    "search_criteria": [\
                        {\
                            "field": "department.site.id",\
                            "condition": "is",\
                            "values": [901]\
                        },\
                        {\
                            "field": "login_name",\
                            "logical_operator": "and",\
                            "condition": "is",\
                            "values": [\"'+username+'\"]\
                        },\
                        {\
                            "field": "status",\
                            "logical_operator": "and",\
                            "condition": "is",\
                            "values": ["ACTIVE"]\
                        }\
                    ]\
                }\
            }'
            encoded_params = urllib.parse.quote(params, safe='')
            users_url = "https://ictsupport.dswd.gov.ph/api/v3/users?input_data={}".format(encoded_params)
            headers = {
                'authtoken': '1B326C87-0D66-4A44-8393-0D7B31DA4918'
            }
            users_results = requests.request("GET", users_url, headers=headers)
            users = json.loads(users_results.text)
            user_exist = True if (users['list_info'])['total_count'] > 0 else False
            if user_exist:
                with transaction.atomic():
                    url = "https://ictsupport.dswd.gov.ph/api/v3/requests"

                    payload = {'input_data': '{\
                        "request": {\
                            "subject": "'+subject+'",\
                            "description": "'+description+'",\
                            "requester": {\
                                "login_name": "'+username+'"\
                            },\
                            "impact": {\
                                "id": "'+impact+'"\
                            },\
                            "udf_fields": {\
                                "udf_pick_3003": "Field Office Caraga"\
                            },\
                            "urgency": {\
                                "id": "'+urgency+'"\
                            },\
                            "category": {\
                                "id": "'+category+'"\
                            },\
                            "subcategory": {\
                                "id": "'+subcategory+'"\
                            }\
                        }\
                    }'}
                    headers = {
                        'authtoken': '27067971-EDEF-4A4C-944F-2474750C8C3C',
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    response_json = json.loads(response.text)
                    is_success = True if (response_json['response_status'])['status_code'] == 2000 else False
                    if is_success:
                        return JsonResponse({'data': 'success'})
                    return JsonResponse({'data': 'error', 'errors': 'The transaction did not push through. Please try '
                                                                    'again.'})
                
            return JsonResponse({'data': 'error', 'errors': 'Requester username does not exist.'})
        except Exception as e:
            return JsonResponse({'data': 'error', 'errors': 'An exception occurred. '+str(e)})
    return JsonResponse({'data': 'error', 'errors': 'You are not authorized to access this content. Please contact '
                                                    'your administrator.'})


def get_categories(request):
    params = '{\
        "list_info": {\
            "row_count": 100,\
            "sort_field": "name",\
            "sort_order": "asc",\
            "search_criteria": [\
                {\
                    "field": "deleted",\
                    "condition": "is",\
                    "values": [false]\
                }\
            ]\
        }\
    }'
    encoded_params = urllib.parse.quote(params, safe='')
    categories_url = "https://ictsupport.dswd.gov.ph/api/v3/categories?input_data={}".format(encoded_params)
    headers = {
        'authtoken': '1B326C87-0D66-4A44-8393-0D7B31DA4918'
    }

    categories_results = requests.request("GET", categories_url, headers=headers)
    categories = json.loads(categories_results.text)
    json_list = []
    for row in categories['categories']:
        json_list.append({row['id']: row['name']})
    return JsonResponse(json_list, safe=False)


def get_subcategories(request, pk):
    params = '{\
        "list_info": {\
            "row_count": 100,\
            "sort_field": "name",\
            "sort_order": "asc",\
            "search_criteria": [\
                {\
                    "field": "category.id",\
                    "condition": "is",\
                    "values": ['+str(pk)+']\
                },\
                {\
                    "field": "deleted",\
                    "condition": "is",\
                    "logical_operator": "and",\
                    "values": [false]\
                }\
            ]\
        }\
    }'
    encoded_params = urllib.parse.quote(params, safe='')
    subcategories_url = "https://ictsupport.dswd.gov.ph/api/v3/subcategories?input_data={}".format(encoded_params)
    headers = {
        'authtoken': '1B326C87-0D66-4A44-8393-0D7B31DA4918'
    }

    subcategories_results = requests.request("GET", subcategories_url, headers=headers)
    subcategories = json.loads(subcategories_results.text)
    json_list = []
    for row in subcategories['subcategories']:
        json_list.append({row['id']: row['name']})
    return JsonResponse(json_list, safe=False)


def get_urgencies(request):
    params = '{\
        "list_info": {\
            "row_count": 100,\
            "sort_field": "name",\
            "sort_order": "asc",\
            "search_criteria": [\
                {\
                    "field": "deleted",\
                    "condition": "is",\
                    "values": [false]\
                }\
            ]\
        }\
    }'
    encoded_params = urllib.parse.quote(params, safe='')
    urgencies_url = "https://ictsupport.dswd.gov.ph/api/v3/urgencies?input_data={}".format(encoded_params)
    headers = {
        'authtoken': '1B326C87-0D66-4A44-8393-0D7B31DA4918'
    }

    urgencies_results = requests.request("GET", urgencies_url, headers=headers)
    urgencies = json.loads(urgencies_results.text)
    json_list = []
    for row in urgencies['urgencies']:
        json_list.append({row['id']: row['name']})
    return JsonResponse(json_list, safe=False)


def get_impacts(request):
    params = '{\
        "list_info": {\
            "row_count": 100,\
            "sort_field": "name",\
            "sort_order": "asc",\
            "search_criteria": [\
                {\
                    "field": "deleted",\
                    "condition": "is",\
                    "values": [false]\
                }\
            ]\
        }\
    }'
    encoded_params = urllib.parse.quote(params, safe='')
    impacts_url = "https://ictsupport.dswd.gov.ph/api/v3/impacts?input_data={}".format(encoded_params)
    headers = {
        'authtoken': '1B326C87-0D66-4A44-8393-0D7B31DA4918'
    }

    impacts_results = requests.request("GET", impacts_url, headers=headers)
    impacts = json.loads(impacts_results.text)
    json_list = []
    for row in impacts['impacts']:
        json_list.append({row['id']: row['name']})
    return JsonResponse(json_list, safe=False)


def landing_issuances(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('backend-dashboard')
    else:
        website_links = PortalConfiguration.objects.filter(key_name='Website Links').first()
        context = {
            'type': DocsIssuancesType.objects.filter(status=1),
            'website_links': [row for row in website_links.key_acronym.split(',')],
        }
        return render(request, 'landing/issuances.html', context)


def landing_issuances_files(request, pk):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('backend-dashboard')
    else:
        type = DocsIssuancesType.objects.annotate(hash=SHA1('id')).filter(hash=pk).first()
        website_links = PortalConfiguration.objects.filter(key_name='Website Links').first()
        context = {
            'type': type,
            'files': DocsIssuancesFiles.objects.annotate(hash=SHA1('issuances_type_id')).filter(hash=pk).order_by('-year'),
            'website_links': [row for row in website_links.key_acronym.split(',')],
        }
        return render(request, 'landing/issuances_files.html', context)


def job_vacancies(request):

    search = request.GET.get('search', '')

    if search != '':
        vacancy = PositionVacancy.objects.filter(
            Q(status=1),
            Q(deadline__gte=date.today()) |
            Q(deadline=None),
            Q(position__name__icontains=search) |
            Q(empstatus__name__icontains=search) |
            Q(aoa__name__icontains=search)
        ).order_by('position__name')
    else:
        vacancy = PositionVacancy.objects.filter(
            Q(status=1),
            Q(deadline__gte=date.today()) |
            Q(deadline=None)
        ).order_by('position__name')

    context = {
        'title': 'Vacancies',
        'vacancy': vacancy,
        'vacancy_count': vacancy.count(),
        'search': search,
    }
    return render(request, 'landing/job_app/vacancies_view.html', context)


def vacancy_details(request, pk):
    id = force_token_decryption(pk)
    vacancy = PositionVacancy.objects.filter(id=id).first()

    context = {
        'vacancy': vacancy,
    }
    return render(request, 'landing/job_app/vacancy_detail.html', context)


def job_application(request, pk):
    id = force_token_decryption(pk)

    if request.method == "POST":
        config = PortalConfiguration.objects.filter(key_name='JOB_APP').first()

        current_counter = config.counter + 1
        current_year = datetime.now().year
        current_month = datetime.now().month

        tracking_no = 'APP-{}-{}-{}'.format(
            str(current_year).zfill(4),
            str(current_month).zfill(2),
            '%04d' % int(current_counter)
        )

        with transaction.atomic():
            job_app = JobApplication(
                tracking_no=tracking_no,
                vacancy_id=id,
                date_of_app=datetime.now(),
                first_name=request.POST.get('f_name'),
                middle_name=request.POST.get('m_name'),
                last_name=request.POST.get('l_name'),
                extension=request.POST.get('extension'),
                sex=request.POST.get('sex'),
                dob=request.POST.get('dob'),
                civil_status_id=request.POST.get('civil_status'),
                email=request.POST.get('email'),
                contact_no=request.POST.get('contact'),
                course=request.POST.get('course'),
                work_exp=request.POST.get('work_exp'),
                province_id=request.POST.get('province'),
                city_id=request.POST.get('city'),
                brgy_id=request.POST.get('brgy'),
                zip_code=request.POST.get('zip_code'),
                street=request.POST.get('street'),
                tor=request.FILES.get('tor'),
                app_letter=request.FILES.get('app_letter'),
                pds=request.FILES.get('pds'),
                we_sheet=request.FILES.get('we_sheet'),
                cert_training=request.FILES.get('cert_training'),
                cert_employment=request.FILES.get('cert_employment'),
                ipcr=request.FILES.get('ipcr'),
            )

            job_app.save()

            PortalConfiguration.objects.filter(key_name='JOB_APP').update(
                counter=F('counter') + 1
            )

            if request.POST.get('el_radio') == "with_el":
                el_name = request.POST.getlist('el_name[]')
                el_rating = request.POST.getlist('el_rating[]')
                el_date = request.POST.getlist('el_date[]')
                el_place = request.POST.getlist('el_place[]')
                el_num = request.POST.getlist('el_num[]')
                el_dov = request.POST.getlist('el_dov[]')
                el_file = request.FILES.getlist('el_file[]')

                data = [
                    {'name': n, 'rating': r, 'date': d, 'place': p, 'num': num, 'dov': dov, 'file': f}
                    for n, r, d, p, num, dov, f in zip(el_name, el_rating, el_date, el_place, el_num, el_dov, el_file)
                ]

                for row in data:
                    AppEligibility.objects.create(
                        app_id=job_app.id,
                        name=row['name'],
                        rating=row['rating'] if row['rating'] != '' else None,
                        date=row['date'],
                        place=row['place'],
                        license_number=row['num'],
                        license_dov=row['dov'] if row['dov'] != '' else None,
                        attachment=row['file'],
                    )

        vacancy = PositionVacancy.objects.filter(id=id).first()

        msg = f"""
            Your application in {vacancy.position.name} with Tracking No.:
            <p class="font-weight-bold text-info py-3" style="font-size: 20px;">{tracking_no}</p> 
            was successfuly submitted!
        """

        return JsonResponse({'data': 'success', 'msg': msg, 'tracking_no': tracking_no})

    context = {
        'title': 'Application Page',
        'sub_title': 'Application',
        'province': Province.objects.filter(status=1).order_by('name'),
        'civil_status': Civilstatus.objects.filter(status=1),
        'vacancy': PositionVacancy.objects.filter(id=id).first(),
        'pk': pk,
    }
    return render(request, 'landing/job_app/application.html', context)


def show_city(request, prov_code):
    context = {
        'city': City.objects.filter(status=1, prov_code_id=prov_code).order_by('name'),
    }
    return render(request, 'landing/job_app/show_city.html', context)


def show_brgy(request, city_code):
    context = {
        'brgy': Brgy.objects.filter(status=1, city_code_id=city_code).order_by('name'),
    }
    return render(request, 'landing/job_app/show_brgy.html', context)


def check_captcha(request):
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result['success']:
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'data': 'error', 'msg': 'Invalid reCAPTCHA. Please try again.'})


def app_success(request, tracking_no):
    job_app = JobApplication.objects.filter(tracking_no=tracking_no).first()

    context = {
        'title': 'Success',
        'sub_title': 'Application',
        'job_app': job_app,
    }
    return render(request, 'landing/job_app/success.html', context)


def app_tracking(request):
    tracking_no = request.GET.get('tracking_no')

    app = JobApplication.objects.filter(tracking_no=tracking_no).first()
    status = AppStatus.objects.filter(status=1).order_by('order')

    context = {
        'title': 'Tracking',
        'sub_title': 'Application',
        'application': app,
        'tracking_no': tracking_no,
        'status': status
    }
    return render(request, 'landing/job_app/tracking.html', context)

