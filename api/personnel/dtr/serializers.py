from rest_framework import serializers

from backend.models import WfhTime


class DTRTimeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %p", read_only=True)
    date = serializers.DateTimeField(source="datetime", format="%Y-%m-%d", read_only=True)
    time = serializers.DateTimeField(source="datetime", format="%H:%M:%S %p", read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = WfhTime
        fields = '__all__'

    @staticmethod
    def get_type(obj):
        return obj.type.type_desc