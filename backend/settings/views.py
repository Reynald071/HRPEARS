from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from backend.models import AuthPermission, DjangoContentType, AuthUserUserPermissions, Patches
from backend.settings.forms import PermissionForm
from frontend.models import PortalConfiguration


@login_required
@permission_required("admin.superadmin")
def portal_settings(request):
    context = {
        'sub_title': 'portal_settings',
        'title': 'others',
        'tab_title': 'Settings'
    }
    return render(request, 'settings/settings.html', context)


@login_required
@permission_required("admin.superadmin")
def portal_api_logs(request):
    return render(request, 'settings/api_logs.html')


@login_required
@permission_required("admin.superadmin")
def portal_configuration(request):
    if request.method == "POST":
        PortalConfiguration.objects.create(
            key_name=request.POST.get('key_name'),
            key_acronym=request.POST.get('key_acronym'),
            counter=request.POST.get('counter') if request.POST.get('counter') else None,
            year=request.POST.get('year') if request.POST.get('year') else None
        )

        return JsonResponse({'data': 'success'})
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    context = {
        'data': Paginator(PortalConfiguration.objects.all().order_by('key_name'), rows).page(page)
    }
    return render(request, 'settings/configuration.html', context)


@login_required
@permission_required("admin.superadmin")
def portal_configuration_update(request):
    if request.method == "POST":
        PortalConfiguration.objects.filter(id=request.POST.get('id')).update(
            key_name=request.POST.get('key_name'),
            key_acronym=request.POST.get('key_acronym'),
            counter=request.POST.get('counter') if request.POST.get('counter') else None,
            year=request.POST.get('year') if request.POST.get('year') else None
        )

        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required("admin.superadmin")
def portal_configuration_delete(request):
    if request.method == "POST":
        PortalConfiguration.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@permission_required("admin.superadmin")
def portal_permission(request):
    if request.method == "POST":
        AuthPermission.objects.create(
            name=request.POST.get('name'),
            codename=request.POST.get('codename'),
            content_type_id=request.POST.get('content_type')
        )

        return JsonResponse({'data': 'success'})

    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    context = {
        'data': Paginator(AuthPermission.objects.all().order_by('name'), rows).page(page),
        'content_type': DjangoContentType.objects.all().order_by('app_label')
    }
    return render(request, 'settings/permission.html', context)


@login_required
@permission_required("admin.superadmin")
def update_portal_permission(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(AuthPermission, pk=pk)
        form = PermissionForm(request.POST, request.FILES, instance=obj)

        if form.is_valid():
            form.save()

        return JsonResponse({'data': 'success'})
    context = {
        'form': PermissionForm(instance=get_object_or_404(AuthPermission, pk=pk)),
        'permission': AuthPermission.objects.filter(id=pk).first()
    }
    return render(request, 'settings/edit_permission.html', context)


@login_required
@csrf_exempt
@permission_required("admin.superadmin")
def delete_portal_permission(request):
    if request.method == "POST":
        AuthPermission.objects.filter(id=request.POST.get('id')).delete()
        AuthUserUserPermissions.objects.filter(permission_id=request.POST.get('id')).delete()
        return JsonResponse({'data': 'success'})


@login_required
@csrf_exempt
@permission_required("admin.superadmin")
def delete_portal_user_permission(request):
    if request.method == "POST":
        user_id = request.POST.get('id')
        check = AuthUserUserPermissions.objects.get(id=user_id)
        if check.user_id != request.user.id:
            AuthUserUserPermissions.objects.filter(id=user_id).delete()
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'error': True, 'msg': "You cannot remove this permission because the current session "
                                                       "is still active."})


@login_required
@permission_required("admin.superadmin")
def patch_notes(request):
    if request.method == "POST":
        Patches.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            release_date=request.POST.get('release_date')
        )

        return JsonResponse({'data': 'success'})

    return render(request, 'settings/patch_notes.html')


@login_required
@permission_required("admin.superadmin")
def edit_patch_notes(request, pk):
    if request.method == "POST":
        Patches.objects.filter(id=pk).update(
            title=request.POST.get('edit-title'),
            description=request.POST.get('edit-description'),
            release_date=request.POST.get('edit_release_date')
        )

        return JsonResponse({'data': 'success'})
    context = {
        'patches': Patches.objects.filter(id=pk).first()
    }
    return render(request, 'settings/edit_patch_notes.html', context)
