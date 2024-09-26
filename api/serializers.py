from rest_framework import serializers

from backend.convocation.models import ConvocationEvent
from backend.models import RestFrameworkTrackingApirequestlog, AuthUserUserPermissions, \
    SMSLogs, AuthPermission, Patches, PortalSuccessLogs
from frontend.models import Feedback


class PortalConfigSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    key_name = serializers.CharField(read_only=True)
    counter = serializers.IntegerField(read_only=True)
    year = serializers.CharField(read_only=True)
    key_acronym = serializers.CharField(read_only=True)


class PermissionSerializer(serializers.ModelSerializer):
    total_user = serializers.CharField(source="count_user", read_only=True)

    class Meta:
        model = AuthPermission
        fields = ['id', 'name', 'codename', 'description', 'badge', 'total_user']


class UserPermissionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()
    position = serializers.CharField(source="user.get_position", read_only=True)

    class Meta:
        model = AuthUserUserPermissions
        fields = '__all__'

    @staticmethod
    def get_full_name(obj):
        return obj.user.get_fullname


class RestFrameworkTrackingSerializer(serializers.ModelSerializer):
    requested_at = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    full_name = serializers.SerializerMethodField(allow_null=True)
    path = serializers.CharField(read_only=True)
    remote_addr = serializers.CharField(read_only=True)
    method = serializers.CharField(read_only=True)
    status_code = serializers.CharField(read_only=True)

    class Meta:
        model = RestFrameworkTrackingApirequestlog
        fields = '__all__'

    @staticmethod
    def get_full_name(obj):
        return obj.user.get_fullname


class PatchesSerializer(serializers.ModelSerializer):
    release_date = serializers.DateField(format="%b %d, %Y", read_only=True)

    class Meta:
        model = Patches
        fields = '__all__'


class SMSSerializer(serializers.ModelSerializer):
    date_sent = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = SMSLogs
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='emp.pi.user.get_fullname')
    date = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'


class ConvocationSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%b %d, %Y", read_only=True)
    time = serializers.TimeField(format="%H:%M %p", read_only=True)

    class Meta:
        model = ConvocationEvent
        fields = ['id', 'date', 'time', 'status']


class PortalSuccessLogsSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p")

    class Meta:
        model = PortalSuccessLogs
        fields = '__all__'
