from django_mysql.models.functions import SHA1
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.personnel.leave.serializers import LeaveSerializer, CTDOSerializer, LeaveCertificationTransactionSerializer, \
    CTDOBalanceSerializer
from backend.leave.models import LeaveCertificationTransaction
from backend.libraries.leave.models import LeaveApplication, CTDORequests, CTDOBalance
from backend.templatetags.tags import check_permission


class LeaveAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'leave') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class LeaveViews(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = LeaveApplication.objects.annotate(hash=SHA1('emp_id')).filter(
                hash=self.request.query_params.get('employee_id'),
                status=self.request.query_params.get('status')
            )
            return queryset
        else:
            queryset = LeaveApplication.objects.annotate(hash=SHA1('emp_id')).filter(hash=self.request.query_params.get('employee_id'))
            return queryset


class LeaveAdminViews(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated, LeaveAdminPermissions]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = LeaveApplication.objects.filter(
                date_of_filing__year=self.request.query_params.get('year'),
                status=self.request.query_params.get('status')
            )
            return queryset
        else:
            queryset = ''
            if self.request.query_params.get('year'):
                queryset = LeaveApplication.objects.filter(date_of_filing__year=self.request.query_params.get('year'))
            else:
                queryset = LeaveApplication.objects.all()

            return queryset


class CTDOViews(generics.ListAPIView):
    serializer_class = CTDOSerializer
    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = CTDORequests.objects.annotate(hash=SHA1('emp_id')).filter(
                hash=self.request.query_params.get('employee_id'),
                status=self.request.query_params.get('status')
            )
            return queryset
        else:
            queryset = CTDORequests.objects.annotate(hash=SHA1('emp_id')).filter(hash=self.request.query_params.get('employee_id'))
            return queryset


class CTDOAdminViews(generics.ListAPIView):
    serializer_class = CTDOSerializer
    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = CTDORequests.objects.filter(
                status=self.request.query_params.get('status')
            )
            return queryset
        else:
            queryset = CTDORequests.objects.order_by('-tracking_no')
            return queryset


class LeaveCertificationTransactionViews(generics.ListAPIView):
    serializer_class = LeaveCertificationTransactionSerializer
    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LeaveCertificationTransaction.objects.filter(
            emp_id=self.request.query_params.get('employee_id'), status=1
        )
        return queryset


class CTDOBalanceViews(generics.ListAPIView):
    serializer_class = CTDOBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CTDOBalance.objects.filter(emp_id=self.request.query_params.get('emp_id'))
        return queryset
