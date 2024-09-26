from rest_framework import serializers

from backend.documents.models import DtsTransaction, DtsDocument
from backend.models import AuthUserUserPermissions


class DtsTransactionSerializer(serializers.ModelSerializer):
    drn = serializers.CharField(source='document.get_drn', read_only=True)
    subject = serializers.CharField(source='document.has_attachment_and_subject', read_only=True)
    sender = serializers.CharField(source='document.sender', read_only=True)
    document_date = serializers.DateField(source='document.document_date', format="%b %d, %Y", read_only=True)
    date_saved = serializers.DateTimeField(source='document.date_saved', format="%b %d, %Y", read_only=True)
    trans_from = serializers.CharField(source='document.get_latest_status.trans_from.pi.user.get_fullname', read_only=True)
    trans_to = serializers.CharField(source='document.get_latest_status.trans_to.pi.user.get_fullname', read_only=True)
    action = serializers.IntegerField(source='document.get_latest_status.action', read_only=True)

    class Meta:
        model = DtsTransaction
        fields = ['document_id', 'drn', 'subject', 'sender', 'document_date', 'date_saved', 'trans_from', 'trans_to',
                  'action']


class DtsDocumentSerializer(serializers.ModelSerializer):
    drn = serializers.CharField(source='get_drn', read_only=True)
    subject = serializers.CharField(source='has_attachment_and_subject', read_only=True)
    doc_date = serializers.DateField(source='document_date', format="%b %d, %Y", read_only=True)
    doc_saved = serializers.DateTimeField(source='date_saved', format="%b %d, %Y", read_only=True)
    trans_from = serializers.CharField(source='get_latest_status.trans_from.pi.user.get_fullname',
                                       read_only=True)
    trans_to = serializers.CharField(source='get_latest_status.trans_to.pi.user.get_fullname', read_only=True)
    action = serializers.IntegerField(source='get_latest_status.action', read_only=True)

    class Meta:
        model = DtsDocument
        fields = ['id', 'drn', 'subject', 'sender', 'doc_date', 'doc_saved', 'trans_from', 'trans_to',
                  'action']


class DtsTransactionOthersSerializer(serializers.ModelSerializer):
    drn = serializers.CharField(source='document.get_drn', read_only=True)
    subject = serializers.CharField(source='document.has_attachment_and_subject', read_only=True)
    sender = serializers.CharField(source='document.sender', read_only=True)
    document_date = serializers.DateField(source='document.document_date', format="%b %d, %Y", read_only=True)
    date_saved = serializers.DateTimeField(source='document.date_saved', format="%b %d, %Y", read_only=True)
    trans_from = serializers.CharField(source='document.get_latest_status.trans_from.pi.user.get_fullname', read_only=True)
    trans_to = serializers.CharField(source='document.get_latest_status.trans_to.pi.user.get_fullname', read_only=True)
    action = serializers.IntegerField(source='document.get_latest_status.action', read_only=True)

    class Meta:
        model = DtsTransaction
        fields = ['document_id', 'drn', 'subject', 'sender', 'document_date', 'date_saved', 'trans_from',
                  'trans_to', 'action']


class DtsDocumentCustodianSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.get_fullname', read_only=True)
    division = serializers.CharField(source='user.get_division', read_only=True)
    section = serializers.CharField(source='user.get_section', read_only=True)

    class Meta:
        model = AuthUserUserPermissions
        fields = ['fullname', 'division', 'section']
