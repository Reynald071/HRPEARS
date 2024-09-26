from rest_framework import serializers

from backend.libraries.grievance.models import GrievanceQuery


class GrievanceSerializers(serializers.ModelSerializer):
    tracking_no = serializers.CharField(read_only=True)
    client_name = serializers.CharField(source='get_client_name', read_only=True)
    client_contactnumber = serializers.CharField(read_only=True)
    client_address = serializers.CharField(source='get_client_address', read_only=True)
    media_name = serializers.SerializerMethodField()
    datetime = serializers.DateTimeField(format="%b %d, %Y", read_only=True)
    get_employee_by_latest_status = serializers.CharField(source='get_latest_status.emp_id', read_only=True)
    get_latest_status_id = serializers.CharField(source='get_latest_status.gstatus_id', read_only=True)
    status = serializers.CharField(source='get_latest_status.gstatus.name', read_only=True)

    class Meta:
        model = GrievanceQuery
        fields = '__all__'

    @staticmethod
    def get_media_name(obj):
        return obj.gmedia.name