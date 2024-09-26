from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from backend.models import DirectoryContact, DirectoryDetailType, ExtensionName, DirectoryDetails, DirectoryOrgtype
from backend.templatetags.tags import getDirectoryDetails


@login_required
def directory_list(request):
    context = {
        'ext': ExtensionName.objects.filter(status=1),
        'detail_types': DirectoryDetailType.objects.filter(status=1).order_by('type'),
        'orgtype': DirectoryOrgtype.objects.filter(status=1),
        'title': 'directory_list',
        'tab_title': 'Directory List'
    }
    return render(request, 'backend/directory/list.html', context)


@login_required
def edit_directory_list(request, pk):
    data = DirectoryContact.objects.filter(id=pk).first()
    context = {
        'data': data,
        'ext': ExtensionName.objects.filter(status=1),
        'orgtype': DirectoryOrgtype.objects.filter(status=1),
        'detail_types': DirectoryDetailType.objects.filter(status=1).order_by('type'),
        'directory_details': DirectoryDetails.objects.filter(dcontact_id=pk)
    }
    return render(request, 'backend/directory/update_list.html', context)


@login_required
@permission_required("auth.directory_management")
def directory_list_requests(request):
    if request.method == 'POST':
        dtype = request.POST.getlist('dtype[]')
        description = request.POST.getlist('description[]')

        data = [{'dtype': d, 'description': ds}
                for d, ds in zip(dtype, description)]

        if request.POST.get('action') == '1':
            check = DirectoryDetails.objects.filter(dcontact_id=request.POST.get('id'))
            store = [row.id for row in check]

            y = 1
            x = 0
            directory_contact = DirectoryContact.objects.filter(id=request.POST.get('id')).update(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                middle_name=request.POST.get('middle_name'),
                ext_id=request.POST.get('ext'),
                company=request.POST.get('company'),
                job_title=request.POST.get('job_title'),
                notes=request.POST.get('notes'),
                last_updated_by_id=request.user.id,
                last_updated_on=datetime.now(),
                orgtype_id=request.POST.get('orgtype'),
            )
            for row in data:
                if y > len(check):
                    DirectoryDetails.objects.create(
                        dcontact_id=request.POST.get('id'),
                        dtype_id=row['dtype'],
                        description=row['description'],
                    )
                else:
                    DirectoryDetails.objects.filter(id=store[x]).update(
                        dcontact_id=request.POST.get('id'),
                        dtype_id=row['dtype'],
                        description=row['description'],
                    )
                    y += 1
                    x += 1
        else:
            directory_contact = DirectoryContact.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                middle_name=request.POST.get('middle_name'),
                ext_id=request.POST.get('ext'),
                company=request.POST.get('company'),
                job_title=request.POST.get('job_title'),
                notes=request.POST.get('notes'),
                status=True,
                upload_by_id=request.user.id,
                last_updated_by_id=request.user.id,
                orgtype_id=request.POST.get('orgtype'),
            )
            for row in data:
                DirectoryDetails.objects.create(
                    dcontact_id=directory_contact.id,
                    dtype_id=row['dtype'],
                    description=row['description'],
                )

        return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
@permission_required("auth.directory_management")
def delete_detail(request):
    DirectoryDetails.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})


@csrf_exempt
@login_required
def contacts_search(request):
    allconts = DirectoryContact.objects.filter(Q(status=1),
                                               (Q(last_name__icontains=request.POST.get('contacts-search')) |
                                                Q(first_name__icontains=request.POST.get('contacts-search')) |
                                                Q(company__icontains=request.POST.get('contacts-search')) |
                                                Q(orgtype__name__icontains=request.POST.get('contacts-search')) |
                                                Q(orgtype__acronym__icontains=request.POST.get('contacts-search')) |
                                                Q(job_title__icontains=request.POST.get('contacts-search'))
                                                )).order_by('last_name', 'first_name')
    toreturn = list()
    detailtypes = DirectoryDetailType.objects.filter(status=1).order_by('type')
    for row in allconts:
        details = ''
        for d in detailtypes:
            x = getDirectoryDetails(d.id, row.id)
            y = ', '.join(x)
            details += '{}&emsp;:&emsp;{}<br>'.format(d.type, y)
        toreturn.append({
            'fullname': '{}, {}{}'.format(row.last_name, row.first_name,
                                          ' {}.'.format(row.middle_name[:1]) if row.middle_name.strip() != '' else ''),
            'company': row.company,
            'notes': row.notes,
            'orgtype': row.orgtype.name,
            'job_title': row.job_title,
            'details': details
        })
    return JsonResponse({'data': toreturn})
