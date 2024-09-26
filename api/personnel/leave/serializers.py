from rest_framework import serializers

from backend.leave.models import LeaveCertificationTransaction
from backend.libraries.leave.models import LeaveApplication, CTDORequests, CTDOBalance


class LeaveSerializer(serializers.ModelSerializer):
    leavesubtype_name = serializers.CharField(source='leavesubtype.name', read_only=True)
    requested_by = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    inclusive_dates = serializers.CharField(source='get_inclusive', read_only=True, allow_null=True)
    date_of_filing = serializers.DateTimeField(format="%Y-%m-%d %H:%M %p", read_only=True)
    approved_date = serializers.DateTimeField(format="%b %d, %Y %H:%M %p", read_only=True)

    class Meta:
        model = LeaveApplication
        fields = ['id', 'tracking_no', 'leavesubtype_name', 'inclusive_dates', 'start_date', 'end_date',
                  'date_of_filing', 'status', 'requested_by', 'approved_date']


class CTDOSerializer(serializers.ModelSerializer):
    inclusive_dates = serializers.CharField(source='get_inclusive', read_only=True)
    requested_by = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    date_filed = serializers.DateTimeField(format="%b %d, %Y %H:%M %p", read_only=True)

    class Meta:
        model = CTDORequests
        fields = ['id', 'tracking_no', 'inclusive_dates', 'date_filed', 'status', 'requested_by']


class LeaveCertificationTransactionSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%b %d, %Y %H:%M %p", read_only=True)
    created_by = serializers.CharField(source='created_by.pi.user.get_fullname', read_only=True)
    type = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = LeaveCertificationTransaction
        fields = ['id', 'drn', 'date_created', 'created_by', 'title', 'type', 'emp_id']


class CTDOBalanceSerializer(serializers.ModelSerializer):
    date_expiry = serializers.DateField(format="%b %d, %Y", read_only=True)

    class Meta:
        model = CTDOBalance
        fields = ['id', 'days', 'hours', 'minutes', 'date_expiry', 'month_earned', 'status']