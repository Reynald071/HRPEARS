from rest_framework import serializers

from backend.pas.transmittal.models import TransmittalNew, TransmittalOld


class TransmittalSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document_name.name', read_only=True)
    document_date = serializers.DateField(format="%Y-%m-%d")
    date_added = serializers.DateTimeField(format="%Y-%m-%d, %H:%M:%S %p")
    status = serializers.CharField(source='get_latest_status.status', read_only=True)
    date = serializers.CharField(source='get_latest_status.date', read_only=True)
    registered_by = serializers.CharField(source='get_latest_status.emp.pi.user.get_fullname', read_only=True)
    owner = serializers.CharField(source='emp.pi.user.get_fullname')
    date_approved = serializers.DateTimeField(source='get_latest_status.date_approved', format="%Y-%m-%d, %H:%M %p", read_only=True)

    class Meta:
        model = TransmittalNew
        fields = ['id', 'tracking_no', 'document_name', 'document_date', 'details', 'date_added',
                  'registered_by', 'status', 'date', 'owner', 'date_approved']


class TransmittalOldSerializer(serializers.ModelSerializer):
    date_received = serializers.DateField(format="%Y-%m-%d")
    date_added = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %p")

    class Meta:
        model = TransmittalOld
        fields = ['tracking_id', 'id_number', 'document_name', 'transaction_type', 'date_received', 'date_document',
                  'forwarded_to', 'details', 'date_added']
