from rest_framework import serializers

from backend.models import DirectoryContact


class DirectoryListSerializers(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='get_contact_name')
    last_updated_by = serializers.CharField(source='last_updated_by.get_fullname')
    last_updated_on = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    email = serializers.CharField(source='get_email', allow_null=True)
    contact = serializers.CharField(source='get_contact', allow_null=True)
    address = serializers.CharField(source='get_address', allow_null=True)

    class Meta:
        model = DirectoryContact
        fields = ['id', 'contact_name', 'first_name', 'last_name', 'middle_name', 'company',
                  'job_title', 'last_updated_by', 'email', 'contact', 'address', 'last_updated_on']