from rest_framework import serializers

from backend.certificates.models import CertTransaction


class CertificationTransactionSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%b %d, %Y %H:%M %p", read_only=True)
    cert_type = serializers.CharField(source='certtemp.name', read_only=True)
    created_by = serializers.CharField(source='created_by.pi.user.get_fullname', read_only=True)

    class Meta:
        model = CertTransaction
        fields = ['id', 'date_created', 'created_by', 'cert_type']