from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from backend.templatetags.tags import force_token_decryption
from frontend.rso.models import RsoType, RsoAttachment


def rso_attachment(request):
    context = {
        'rso_type': RsoType.objects.order_by('name')
    }
    return render(request, 'dashboard/rso.html', context)


def rso_attachment_view(request, pk):
    id = force_token_decryption(pk)
    if request.method == "POST":
        RsoAttachment.objects.create(
            year=request.POST.get('year'),
            rso_no=request.POST.get('rso_no'),
            type_id=id,
            title=request.POST.get('title'),
            attachment=request.FILES.get('attachment'),
            date_uploaded=datetime.now()
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully uploaded the file.'})

    context = {
        'rso_type': RsoType.objects.filter(id=id).first(),
        'pk': pk
    }
    return render(request, 'dashboard/rso_view.html', context)