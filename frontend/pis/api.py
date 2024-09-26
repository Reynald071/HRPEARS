from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from backend.models import Position
from frontend.models import School, Degree, Honors, Eligibility, Organization, Trainingtitle, Hobbies, Nonacad


@login_required
def api_schools(request, pi_id):
    return JsonResponse({'data': list(School.objects.filter((Q(school_status=0) & Q(pi_id=pi_id)) | Q(school_status=1)).order_by(
            'school_name').values())})


@login_required
def api_degrees(request, pi_id):
    return JsonResponse({'data': list(Degree.objects.filter((Q(deg_status=0) & Q(pi_id=pi_id)) | Q(deg_status=1)).order_by('degree_name').values())})


@login_required
def api_honors(request, pi_id):
    return JsonResponse({'data': list(Honors.objects.filter((Q(hon_status=0) & Q(pi_id=pi_id)) | Q(hon_status=1)).order_by('hon_name').values())})


@login_required
def api_eligibilities(request, pi_id):
    return JsonResponse({'data': list(Eligibility.objects.filter((Q(el_status=0) & Q(pi_id=pi_id)) | Q(el_status=1)).order_by('el_name').values())})


@login_required
def api_positions(request, user_id):
    return JsonResponse({'data': list(Position.objects.filter((Q(status=0) & Q(upload_by_id=user_id)) | Q(status=1)).order_by('name').values())})


@login_required
def api_organizations(request, pi_id):
    return JsonResponse({'data': list(Organization.objects.filter((Q(org_status=0) & Q(pi_id=pi_id)) | Q(org_status=1)).order_by('org_name').values())})


@login_required
def api_trainings(request, pi_id):
    return JsonResponse({'data': list(Trainingtitle.objects.filter((Q(tt_status=0) & Q(pi_id=pi_id)) | Q(tt_status=1)).order_by('tt_name').values())})


@login_required
def api_hobbies(request, pi_id):
    return JsonResponse({'data': list(Hobbies.objects.filter((Q(pi_id=pi_id) & Q(hob_status=0)) | Q(hob_status=1)).order_by('hob_name').values())})


@login_required
def api_nonacads(request, pi_id):
    return JsonResponse({'data': list(Nonacad.objects.filter((Q(pi_id=pi_id) & Q(na_status=0)) | Q(na_status=1)).order_by('na_name').values())})
