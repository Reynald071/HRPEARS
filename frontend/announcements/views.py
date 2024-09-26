from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from frontend.models import PortalAnnouncements
from frontend.templatetags.tags import gamify


@login_required
def announcements(request):
    if request.method == "POST":
        title = request.POST.get('title')
        caption = request.POST.get('caption')
        uploaded_by = request.session['emp_id']
        attachment = request.FILES.get('attachment')
        is_urgent = request.POST.get('is_urgent')
        announcement_type = request.POST.get('announcement_type')
        if request.POST.get('transaction_type') == '0':
            PortalAnnouncements.objects.create(
                title=title,
                caption=caption,
                uploaded_by_id=uploaded_by,
                attachment=attachment if attachment else None,
                announcement_type=announcement_type if announcement_type else None,
                is_urgent=True if is_urgent else False
            )

            # Save points for booking of event in calendar
            gamify(10, request.session['emp_id'])

            return JsonResponse({'data': 'success'})
        else:
            x = PortalAnnouncements.objects.filter(id=request.POST.get('announcement_id')).first()
            x.title = title
            x.caption = caption
            x.is_urgent = True if is_urgent else False
            if attachment:
                x.attachment = attachment
            x.save()

            # Save points for booking of event in calendar
            gamify(10, request.session['emp_id'])

            return JsonResponse({'data': 'success'})

    context = {
        'tab_title': 'Announcements',
        'title': 'announcements',
    }
    return render(request, 'frontend/announcements/announcements.html', context)


@login_required
@csrf_exempt
def delete_announcement(request):
    PortalAnnouncements.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'data': 'success'})
