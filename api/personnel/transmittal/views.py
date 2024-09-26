from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.personnel.transmittal.serializers import TransmittalSerializer, TransmittalOldSerializer
from backend.pas.transmittal.models import TransmittalNew, TransmittalOld
from backend.templatetags.tags import check_permission


class TransmittalPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'transmittal') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class TransmittalEmployeeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransmittalSerializer

    def get_queryset(self):
        if self.request.query_params.get('pk'):
            queryset = TransmittalNew.objects.filter(emp_id=self.request.query_params.get('pk')).order_by('-tracking_no')

            return queryset


class TransmittalEmployeeOldView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransmittalOldSerializer

    def get_queryset(self):
        if self.request.query_params.get('id_number'):
            queryset = TransmittalOld.objects.filter(id_number=self.request.query_params.get('id_number')).order_by('-tracking_id')

            return queryset


class TransmittalView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, TransmittalPermissions]
    serializer_class = TransmittalSerializer

    def get_queryset(self):
        if self.request.query_params.get('pk'):
            queryset = TransmittalNew.objects.filter(emp_id=self.request.query_params.get('pk')).order_by('-tracking_no')
        else:
            queryset = TransmittalNew.objects.order_by('-tracking_no')
        return queryset


class TransmittalOldView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, TransmittalPermissions]
    serializer_class = TransmittalOldSerializer

    def get_queryset(self):
        if self.request.query_params.get('id_number'):
            queryset = TransmittalOld.objects.filter(id_number=self.request.query_params.get('id_number')).order_by('-tracking_id')
        else:
            queryset = TransmittalOld.objects.order_by('-tracking_id')

        return queryset