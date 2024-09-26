from django_mysql.models.functions import SHA1
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.lds.serializers import LdsRsoSerializer, LdsParticipantsSerializer, LdsFacilitatorSerializer, LdsIDPSerializer
from backend.templatetags.tags import check_permission
from frontend.lds.models import LdsRso, LdsParticipants, LdsFacilitator, LdsIDP


class LdsRsoViews(generics.ListAPIView):
    serializer_class = LdsRsoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LdsRso.objects.annotate(hash=SHA1('created_by_id')).filter(hash=self.request.query_params.get('pk')).order_by('-date_added')
        return queryset


class LdsManagerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'ld_manager') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class LdsRsoViewsAdmin(generics.ListAPIView):
    serializer_class = LdsRsoSerializer
    permission_classes = [IsAuthenticated, LdsManagerPermissions]
    queryset = LdsRso.objects.order_by('-date_added')


class LdsParticipantsViews(generics.ListAPIView):
    serializer_class = LdsParticipantsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LdsParticipants.objects.annotate(type_pk=SHA1('type'), rso_pk=SHA1('rso_id')).filter(
            type_pk=self.request.query_params.get('type_pk'),
            rso_pk=self.request.query_params.get('rso_pk')
        ).order_by('emp__pi__user__last_name')
        return queryset


class LdsFacilitatorsViews(generics.ListAPIView):
    serializer_class = LdsFacilitatorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LdsFacilitator.objects.annotate(rso_pk=SHA1('rso_id'), type_pk=SHA1('is_external')).filter(
            type_pk=self.request.query_params.get('type_pk'),
            rso_pk=self.request.query_params.get('rso_pk')
        ).order_by('emp__pi__user__last_name')
        return queryset


class LdsIDPViews(generics.ListAPIView):
    serializer_class = LdsIDPSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LdsIDP.objects.annotate(emp_pk=SHA1('emp_id')).filter(
            emp_pk=self.request.query_params.get('emp_pk')
        ).order_by('-date_created')
        return queryset


