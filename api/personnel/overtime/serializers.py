from rest_framework import serializers

from frontend.pas.overtime.models import OvertimeDetails, Overtime


class OvertimeDetailsSerializer(serializers.ModelSerializer):
    claims = serializers.CharField(source='claims.name', read_only=True)
    employee_list = serializers.CharField(source='get_employee', read_only=True)

    class Meta:
        model = OvertimeDetails
        fields = ['place', 'start_date', 'end_date', 'nature_of_ot', 'claims', 'employee_list']


class OvertimeSerializer(serializers.ModelSerializer):
    hash_id = serializers.CharField(source='get_hash_id', read_only=True)
    date_requested = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %p", read_only=True)
    employee_list = serializers.CharField(source='get_all_employee', read_only=True)

    class Meta:
        model = Overtime
        fields = ['id', 'hash_id', 'tracking_no', 'employee_list', 'date_requested', 'status']