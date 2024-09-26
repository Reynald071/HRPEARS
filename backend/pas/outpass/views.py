import datetime
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from backend.models import Outpass
from backend.pas.outpass.forms import AttachmentOutpassForm
from backend.templatetags.tags import getdatesinweek
from frontend.models import Locatorslip, Outpassdetails


@login_required
def outpass_request(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    context = {
        "outpass": Paginator(
            Outpassdetails.objects.filter(Q(date__icontains=search),
                                          Q(outpass__status__icontains=status)).order_by('-date'), rows).page(page),
        'rows': rows,
        'title': 'outpass',
        'sub_title': 'requests',
    }
    x = Outpassdetails.objects.filter(Q(date__lt=date.today()), Q(time_returned=None)).all()
    if x:
        for xx in x:
            z = Outpassdetails.objects.get(id=xx.id)
            z.time_returned = '17:00:00'
            z.save()
    return render(request, 'backend/pas/outpass/outpass_request.html', context)


@login_required
def approve_outpass(request, pk, status):
    Outpass.objects.filter(id=pk).update(status=status)
    Locatorslip.objects.filter(outpass_id=pk).update(status=status)
    return redirect('outpass-request')


class AttachmentOutpassUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'backend/pas/outpass/attachment_outpass.html'
    model = Locatorslip
    form_class = AttachmentOutpassForm
    success_url = reverse_lazy('outpass-request')


@csrf_exempt
@login_required
def get_outpass_total(request):
    outpass = Outpass.objects.filter(status=1)
    return JsonResponse({'total': outpass.count()})


@csrf_exempt
@login_required
def get_outpass_total_returning(request):
    outpass = Outpassdetails.objects.filter(Q(outpass__status=2), Q(time_returned=None), Q(date__icontains=date.today()))
    return JsonResponse({'total': outpass.count()})


@login_required
def outpass_report(request):
    if request.method == "POST":
        r = datetime.strptime(request.POST.get('datesearch') + '-1', "%G-W%V-%u")
        dts = getdatesinweek(r.strftime('%Y-%m-%d'))
        newdts = []
        distinctIDs = []
        queryset = []
        for dt in dts:
            newdts.append(dt.strftime('%Y-%m-%d'))

        for newdt in newdts:
            dist = Outpassdetails.objects.filter(Q(outpass__status=2), Q(date=newdt)).all()
            for row in dist:
                if row.outpass.in_behalf_of not in distinctIDs:
                    distinctIDs.append(row.outpass.in_behalf_of)
                    queryset.append(row)

        
        context = {
            'datestart': r.strftime('%Y-%m-%d'),
            'outpassdetails': queryset
        }
        return render(request, 'backend/pas/outpass/outpass_report_print.html', context)

    context = {
        'title': 'outpass',
        'sub_title': 'reports',
    }
    x = Outpassdetails.objects.filter(Q(date__lt=date.today()), Q(time_returned=None)).all()
    if x:
        for xx in x:
            z = Outpassdetails.objects.get(id=xx.id)
            z.time_returned = '17:00:00'
            z.save()
    return render(request, 'backend/pas/outpass/outpass_report.html', context)


@login_required
def outpass_returned(request):
    page = request.GET.get('page', 1)
    rows = request.GET.get('rows', 20)
    search = request.GET.get('search', '')
    context = {
        "outpass": Outpassdetails.objects.filter(Q(outpass__status=2), Q(date__icontains=date.today())).all().order_by(
            '-date'),
        'time': datetime.strptime('00:00', '%H:%M').time(),
        'currenttime': datetime.now().time(),
        'rows': rows,
        'title': 'outpass',
        'sub_title': 'returned',
    }
    x = Outpassdetails.objects.filter(Q(date__lt=date.today()), Q(time_returned=None)).all()
    if x:
        for xx in x:
            z = Outpassdetails.objects.get(id=xx.id)
            z.time_returned = '17:00:00'
            z.save()

    return render(request, 'backend/pas/outpass/outpass_returned.html', context)


@login_required
def trigger_returned(request, pk):
    Outpassdetails.objects.filter(id=pk).update(time_returned=datetime.now())
    return redirect('outpass-returned');