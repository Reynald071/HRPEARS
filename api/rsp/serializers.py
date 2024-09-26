from rest_framework import serializers

from frontend.rsp.models import RspIntroLetter


class RSPIntroLetterSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.pi.user.get_fullname', read_only=True)
    date_created = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = RspIntroLetter
        fields = ['id', 'generated_drn', 'date_created', 'created_by', 'emp_id']