from rest_framework import serializers

from backend.pas.payroll.models import PayrollMovs


class PayrollMovSerializer(serializers.ModelSerializer):
    mov_type = serializers.CharField(source='mov_type.name', read_only=True)
    uploaded_by = serializers.CharField(source='uploaded_by.pi.user.get_fullname', read_only=True)
    date_uploaded = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    filename = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = PayrollMovs
        fields = '__all__'