from rest_framework import serializers

from frontend.models import HazardReport


class HazardReportSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)

    class Meta:
        model = HazardReport
        fields = '__all__'
