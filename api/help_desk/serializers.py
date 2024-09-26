from rest_framework import serializers

from frontend.models import DeskServices


class DeskServicesTransactionSerializer(serializers.ModelSerializer):
    services_name = serializers.CharField(source='classification.name', read_only=True)
    assigned_by = serializers.CharField(source='assigned_emp.pi.user.get_fullname', read_only=True, allow_null=True)
    requested_by = serializers.CharField(source='get_requester', read_only=True)
    date_requested = serializers.DateTimeField(source='date_time', format="%b %d, %Y %H:%M:%S %p", read_only=True)
    latest_transaction = serializers.CharField(source='get_latest_transaction.status', read_only=True)

    class Meta:
        model = DeskServices
        fields = ['id', 'tracking_no', 'assigned_by', 'services_name', 'purpose', 'date_requested',
                  'latest_transaction', 'requested_by', 'others']
