from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.infimos.serializers import InfimosSerializers, InfimosHistoryTrackingSerializers
from backend.infimos.models import TransPayeename, InfimosHistoryTracking
from backend.templatetags.tags import check_permission


class InfimosPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'infimos') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class PayrollInchargePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'payroll_incharge') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class Infimos20Views(generics.ListAPIView):
    serializer_class = InfimosSerializers
    permission_classes = [IsAuthenticated, InfimosPermissions]

    def get_queryset(self):
        queryset = TransPayeename.objects.using('infimos20').filter(transaction__remarks='Personnel')
        return queryset


class Infimos21Views(generics.ListAPIView):
    serializer_class = InfimosSerializers
    permission_classes = [IsAuthenticated, InfimosPermissions]

    def get_queryset(self):
        queryset = TransPayeename.objects.using('infimos21').filter(transaction__remarks='Personnel')
        return queryset


class Infimos22Views(generics.ListAPIView):
    serializer_class = InfimosSerializers
    permission_classes = [IsAuthenticated, InfimosPermissions]

    def get_queryset(self):
        queryset = TransPayeename.objects.using('infimos22').filter(transaction__remarks='Personnel')
        return queryset


class Infimos23Views(generics.ListAPIView):
    serializer_class = InfimosSerializers
    permission_classes = [IsAuthenticated, InfimosPermissions]

    def get_queryset(self):
        queryset = TransPayeename.objects.using('infimos23').filter(transaction__remarks='Personnel')
        return queryset


class InfimosViews(generics.ListAPIView):
    serializer_class = InfimosSerializers
    permission_classes = [IsAuthenticated, InfimosPermissions]

    def get_queryset(self):
        year = self.request.query_params.get('year')
        current_year = year[-2:]
        queryset = TransPayeename.objects.using('infimos{}'.format(current_year)).filter(transaction__remarks='Personnel')
        return queryset


class InfimosHistoryViews(generics.ListAPIView):
    serializer_class = InfimosHistoryTrackingSerializers
    permission_classes = [IsAuthenticated, PayrollInchargePermissions]

    def get_queryset(self):
        queryset = InfimosHistoryTracking.objects.order_by('-id')
        return queryset