import os

from dotenv import load_dotenv
from rest_framework import serializers

from backend.libraries.leave.models import LeavespentApplication
from backend.models import Empprofile, Position
from frontend.models import Ritodetails, Ritopeople

load_dotenv()

class MOTSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class PositionSerializer(serializers.ModelSerializer):
    head_count = serializers.CharField(source='get_head_count')

    class Meta:
        model = Position
        fields = ['id', 'name', 'acronym', 'head_count']


class RitodetailsSerializer(serializers.ModelSerializer):
    tracking_no = serializers.CharField(source='rito.tracking_no', read_only=True)
    claims = serializers.CharField(source='claims.name', read_only=True)
    means_of_transportation = serializers.CharField(source='mot.name', read_only=True)
    requested_by = serializers.CharField(source='rito.emp.id_number')
    passenger_count = serializers.CharField(source='get_count_passenger')
    status = serializers.CharField(source='get_travel_request_status')
    created_at = serializers.DateTimeField(source='rito.date', format="%Y-%m-%d %H:%M:%S %p")

    class Meta:
        model = Ritodetails
        fields = ['id', 'tracking_no', 'place', 'inclusive_from', 'inclusive_to', 'purpose', 'expected_output',
                  'claims', 'means_of_transportation', 'status', 'requested_by', 'passenger_count', 'created_at']


class RitoPeopleSerializer(serializers.ModelSerializer):
    id_number = serializers.CharField(source='name.id_number', read_only=True)
    first_name = serializers.CharField(source='name.pi.user.first_name', read_only=True)
    middle_name = serializers.CharField(source='name.pi.user.middle_name', read_only=True)
    last_name = serializers.CharField(source='name.pi.user.last_name', read_only=True)
    gender = serializers.CharField(source='get_requested_gender')
    area_of_assignment = serializers.CharField(source='name.aoa.name', read_only=True)
    position = serializers.CharField(source='name.position.name', read_only=True)

    class Meta:
        model = Ritopeople
        fields = ['id_number', 'last_name', 'first_name', 'middle_name', 'gender', 'position', 'area_of_assignment']


class EmployeeSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='id', read_only=True)
    username = serializers.CharField(source='pi.user.username', read_only=True)
    first_name = serializers.CharField(source='pi.user.first_name', read_only=True)
    middle_name = serializers.CharField(source='pi.user.middle_name', read_only=True)
    last_name = serializers.CharField(source='pi.user.last_name', read_only=True)
    contact = serializers.CharField(source='pi.mobile_no', read_only=True)
    area_of_assignment = serializers.CharField(source='aoa.name', read_only=True)
    position = serializers.CharField(source='position.name', read_only=True)
    division = serializers.CharField(source='section.div.div_name', read_only=True)
    section = serializers.CharField(source='section.sec_name', read_only=True)
    gender = serializers.CharField(source='get_gender', read_only=True)
    birthdate = serializers.CharField(source='pi.dob', read_only=True)
    image_path = serializers.SerializerMethodField('get_image_url')
    status = serializers.CharField(source='get_status', read_only=True)

    class Meta:
        model = Empprofile
        fields = ['employee_id', 'id_number', 'first_name', 'middle_name', 'last_name', 'username',
                  'contact', 'account_number', 'position', 'division', 'section', 'area_of_assignment',
                  'gender', 'birthdate', 'image_path', 'status']

    def get_image_url(self, obj):
        return '{}/{}'.format(os.getenv('SERVER_URL'), obj.picture.url)


class LeaveSpentApplicationSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(source='leaveapp.start_date', read_only=True)
    end_date = serializers.CharField(source='leaveapp.end_date', read_only=True)
    random_dates = serializers.ListField(source='get_random_dates')
    status = serializers.CharField(source='get_leave_status', read_only=True)
    leave_type = serializers.CharField(source='leaveapp.leavesubtype.name', read_only=True)
    reasons = serializers.CharField(source='get_leave_reasons', read_only=True)

    class Meta:
        model = LeavespentApplication
        fields = ['start_date', 'end_date', 'random_dates', 'leave_type', 'reasons', 'status']

