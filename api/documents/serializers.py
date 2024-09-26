from rest_framework import serializers

from backend.documents.models import Docs201Files, DocsIssuancesFiles
from frontend.rso.models import RsoAttachment


class Document201Serializers(serializers.ModelSerializer):
    file = serializers.CharField(source='file.url', read_only=True)
    upload_by = serializers.SerializerMethodField()

    class Meta:
        model = Docs201Files
        fields = ['id', 'name', 'file', 'year', 'upload_by', 'upload_by_id']

    @staticmethod
    def get_upload_by(obj):
        return obj.upload_by.pi.user.get_fullname


class DocumentIssuancesSerializers(serializers.ModelSerializer):
    issuances_name = serializers.CharField(source='issuances_type.name', read_only=True)
    filename = serializers.CharField(source='get_filename', read_only=True)
    file = serializers.CharField(source='file.url', read_only=True)
    date_time = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = DocsIssuancesFiles
        fields = ['id', 'issuances_name', 'filename', 'file', 'year', 'date_time']


class RSOAttachmentSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="type.name", read_only=True)
    attachment_name = serializers.CharField(source='get_filename', read_only=True)
    attachment = serializers.CharField(source='attachment.url', read_only=True)
    date_uploaded = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = RsoAttachment
        fields = ['id', 'year', 'rso_no', 'type', 'title', 'attachment', 'attachment_name', 'date_uploaded']