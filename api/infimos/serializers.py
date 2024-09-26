from django.db.models import Q
from rest_framework import serializers

from backend.infimos.models import TransPayeename, InfimosHistoryTracking
from backend.pas.payroll.models import PayrollTimelineWorkFlow


class InfimosSerializers(serializers.ModelSerializer):
    dv_no = serializers.CharField(source='transaction.dv_no', read_only=True)
    accountable = serializers.CharField(source='transaction.accountable', read_only=True)
    payee = serializers.CharField(source='transaction.payee', read_only=True)
    modepayment = serializers.CharField(source='transaction.modepayment', read_only=True)
    amt_certified = serializers.CharField(source='transaction.amt_certified', read_only=True)
    dv_date = serializers.DateField(source='transaction.dv_date', format="%b %d, %Y", read_only=True)
    amt_budget = serializers.CharField(source='transaction.amt_budget', allow_null=True, read_only=True)
    amt_journal = serializers.CharField(source='transaction.amt_journal', allow_null=True, read_only=True)
    approval_date = serializers.CharField(source='transaction.approval_date', allow_null=True, read_only=True)
    check_issued = serializers.CharField(allow_null=True, read_only=True)
    check_released = serializers.CharField(allow_null=True, read_only=True)
    payroll_preparation = serializers.CharField(source='get_payroll_preparation', read_only=True)
    payroll_review_approval = serializers.CharField(source='get_payroll_review_approval', read_only=True)
    payroll_transmission = serializers.CharField(source='get_payroll_transmission', read_only=True)
    payroll_signing = serializers.CharField(source='get_payroll_signing', read_only=True)

    class Meta:
        model = TransPayeename
        fields = ['transaction_id', 'dv_no', 'accountable', 'payee', 'modepayment', 'amt_certified', 'dv_date',
                  'amt_budget', 'amt_journal', 'approval_date', 'check_issued', 'check_released',
                  'payroll_preparation', 'payroll_review_approval', 'payroll_transmission', 'payroll_signing']


class InfimosHistoryTrackingSerializers(serializers.ModelSerializer):
    payroll_type = serializers.CharField(source='get_payroll_type')
    latest_payroll_status = serializers.SerializerMethodField()
    latest_payroll_assignee = serializers.SerializerMethodField()

    def get_latest_payroll_status(self, obj):
        payroll_status = obj.get_payroll_latest_status()
        return payroll_status['status'] if payroll_status else ''

    def get_latest_payroll_assignee(self, obj):
        try:
            payroll_status = obj.get_payroll_latest_status()
            return payroll_status['assignee'] if payroll_status else ''
        except Exception as e:
            PayrollTimelineWorkFlow.objects.filter(Q(id=obj.get_payroll_latest_status.id), ~Q(timeline_id=1)).delete()

    class Meta:
        model = InfimosHistoryTracking
        fields = ['id', 'dv_no', 'date_from', 'date_to', 'description', 'amount_certified', 'accountable', 'latest_payroll_status',
                  'latest_payroll_assignee', 'payroll_type']