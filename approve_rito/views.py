from datetime import datetime, date

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.db.models import Q

from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.personnel.travel.serializers import TravelSerializers
from backend.templatetags.tags import check_permission
from frontend.models import Ritopeople, Ritodetails, Rito


@login_required
@permission_required('auth.supervisor')
def approve_rito_home(request):
    current_year = request.GET.get('current_year', datetime.now().year)
    context = {
        'current_year': current_year,
    }
    return render(request, 'approve_rito/home.html', context)


class TravelSupervisorPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'supervisor') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class TravelSupervisorView(generics.ListAPIView):
    serializer_class = TravelSerializers
    permission_classes = [IsAuthenticated, TravelSupervisorPermissions]

    def get_queryset(self):
        rito_status = self.request.query_params.get('status')
        if rito_status == 'all':
            queryset = Rito.objects.filter(
                Q(status__in=[2, 3, 5]) &
                Q(date__year__icontains=self.request.query_params.get('year')) &
                Q(emp__section__div__div_chief_id=self.request.session.get('pi_id'))
            )
            return queryset
        else:
            queryset = Rito.objects.filter(
                Q(status__in=[2, 3, 5]) &
                Q(date__year__icontains=self.request.query_params.get('year')) &
                Q(emp__section__div__div_chief_id=self.request.session.get('pi_id')) &
                Q(status=rito_status)
            )
            return queryset
