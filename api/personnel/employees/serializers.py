from rest_framework import serializers

from backend.ipcr.models import IPC_Rating
from backend.models import Empprofile, Section, PositionVacancy
from backend.pas.service_record.models import PasServiceRecord
from frontend.models import Workhistory
from landing.models import JobApplication


class WorkExperienceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    position = serializers.CharField(source='we.position.name', read_only=True)
    employment_status = serializers.CharField(source='we.empstatus.name', read_only=True)
    aoa = serializers.CharField(source='aoa.name', read_only=True, allow_null=True)
    salary_rate = serializers.CharField(source='we.salary_rate', read_only=True)
    sg_step = serializers.CharField(source='we.sg_step', read_only=True)
    we_from = serializers.CharField(source='we.we_from', read_only=True)
    we_to = serializers.CharField(source='we.we_to', read_only=True)
    we_inclusive = serializers.CharField(source='we.we_inclusive', read_only=True)

    class Meta:
        model = Workhistory
        fields = ['id', 'position', 'employment_status', 'aoa', 'salary_rate', 'sg_step', 'we_from', 'we_to', 'we_id',
                  'we_inclusive']


class EmployeeAdminSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(source='pi.user.get_last_name_title', read_only=True)
    first_name = serializers.CharField(source='pi.user.get_first_name_title', read_only=True)
    middle_name = serializers.CharField(source='pi.user.get_middle_name_title', read_only=True, allow_null=True)
    ext = serializers.CharField(source='pi.ext.name', read_only=True, allow_null=True)
    gender = serializers.CharField(source='pi.get_gender', read_only=True, allow_null=True)
    employment_status = serializers.CharField(source='empstatus.name', read_only=True, allow_null=True)
    position = serializers.CharField(source='position.name', read_only=True, allow_null=True)
    section = serializers.CharField(source='section.sec_name', read_only=True, allow_null=True)
    division = serializers.CharField(source='section.div.div_name', read_only=True, allow_null=True)
    status = serializers.CharField(source='pi.user.is_active', read_only=True)
    fund_source = serializers.CharField(source='fundsource.name', read_only=True)
    area_of_assignment = serializers.CharField(source='aoa.name', read_only=True)

    class Meta:
        model = Empprofile
        fields = ['id', 'pi_id', 'id_number', 'last_name', 'first_name', 'middle_name', 'ext', 'gender',
                  'employment_status', 'position', 'section', 'division', 'status', 'picture', 'fund_source',
                  'area_of_assignment']


class SectionSerializer(serializers.ModelSerializer):
    division = serializers.CharField(source='div.div_name', read_only=True)
    head_count = serializers.CharField(source='get_head_count', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'sec_name', 'division', 'head_count']


class IPCRSerializer(serializers.ModelSerializer):
    attachment = serializers.CharField(source='get_file', read_only=True)
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    date_added = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = IPC_Rating
        fields = ['id', 'year', 'semester', 'ipcr', 'file_id', 'attachment', 'full_name', 'date_added']


class ServiceRecordSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.pi.user.get_fullname', read_only=True)
    date_added = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = PasServiceRecord
        fields = ['id', 'date_added', 'drn', 'created_by']


class PositionVacancySerializer(serializers.ModelSerializer):
    position = serializers.CharField(source='position.name', read_only=True)
    aoa = serializers.CharField(source='aoa.name', read_only=True)
    # filled_by = serializers.CharField(source='filled_by.pi.user.get_fullname', read_only=True, allow_null=True)
    salary_grade = serializers.CharField(source='salary_grade.name', read_only=True)
    upload_by = serializers.CharField(source='upload_by.get_fullname', read_only=True)
    empstatus = serializers.CharField(source='empstatus.name', read_only=True)
    is_past_deadline = serializers.CharField(read_only=True)
    total_hired = serializers.CharField(source='get_total_hired', read_only=True)
    hired_employees = serializers.CharField(source='get_hired_employees', read_only=True)

    class Meta:
        model = PositionVacancy
        fields = ['id', 'number', 'item_number', 'position', 'empstatus', 'aoa', 'quantity', 'salary_rate',
                  'salary_grade', 'deadline', 'upload_by', 'deadline', 'is_past_deadline', 'total_hired',
                  'hired_employees']


class JobApplicationSerializer(serializers.ModelSerializer):
    vacancy = serializers.CharField(source='vacancy.get_position_with_status', read_only=True)
    date_of_app = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    status = serializers.CharField(source='app_status.name', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'tracking_no', 'vacancy', 'date_of_app', 'status', 'app_status_id', 'is_rejected']
