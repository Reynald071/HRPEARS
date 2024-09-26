from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.grievance.serializers import GrievanceSerializers
from backend.libraries.grievance.models import GrievanceQuery, GrievanceRecordsOfAction
from backend.models import Empprofile
from backend.templatetags.tags import check_permission


class GrievancePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'grievance_officer') or check_permission(request.user, 'superadmin') or check_permission(request.user, 'grievance_administrator'):
            return True
        else:
            return False


class GrievanceView(generics.ListAPIView):
    serializer_class = GrievanceSerializers
    permission_classes = [IsAuthenticated, GrievancePermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            if self.request.query_params.get('status'):
                data = GrievanceQuery.objects.order_by('-datetime')
                latest_statuses = list()
                for d in data:
                    if d.get_latest_status.gstatus.id == int(self.request.query_params.get('status')):
                        latest_statuses.append(d.id)
                queryset = GrievanceQuery.objects.filter(id__in=latest_statuses).order_by('-datetime')
                return queryset
            else:
                queryset = GrievanceQuery.objects.order_by('-datetime')
                return queryset
        else:
            if self.request.query_params.get('status') != 0:
                section = Empprofile.objects.filter(id=self.request.session['emp_id']).values_list('section_id')
                confi = GrievanceRecordsOfAction.objects.filter(
                    Q(gquery__is_confidential=True) &
                    Q(emp__section_id__in=section)
                ).values_list('gquery_id')
                data = GrievanceQuery.objects.filter(Q(is_confidential=False) | Q(id__in=confi)).order_by(
                    '-datetime')

                latest_statuses = list()
                for d in data:
                    if d.get_latest_status.gstatus.id == int(self.request.query_params.get('status')):
                        latest_statuses.append(d.id)
                queryset = GrievanceQuery.objects.filter(id__in=latest_statuses).order_by('-datetime')
                return queryset
            else:
                section = Empprofile.objects.filter(id=self.request.session['emp_id']).values_list('section_id')
                confi = GrievanceRecordsOfAction.objects.filter(
                    Q(gquery__is_confidential=True) &
                    Q(emp__section_id__in=section)
                ).values_list('gquery_id')
                queryset = GrievanceQuery.objects.filter(Q(is_confidential=False) | Q(id__in=confi)).order_by('-datetime')
                return queryset