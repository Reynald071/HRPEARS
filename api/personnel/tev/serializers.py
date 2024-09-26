from rest_framework import serializers

from frontend.pas.tev.models import TransNamelist


class TevSerializers(serializers.ModelSerializer):
    dv_no = serializers.CharField(source='transaction.transaction.dv_no', read_only=True)
    dv_date = serializers.DateField(source='transaction.transaction.dv_date', format="%b %d, %Y", read_only=True)
    amt_budget = serializers.CharField(source='transaction.transaction.amt_budget', allow_null=True, read_only=True)
    amt_journal = serializers.CharField(source='transaction.transaction.amt_journal', allow_null=True, read_only=True)
    approval_date = serializers.CharField(source='transaction.transaction.approval_date', allow_null=True, read_only=True)
    check_issued = serializers.CharField(source='transaction.check_issued', read_only=True)
    check_released = serializers.CharField(source='transaction.check_issued', read_only=True)

    class Meta:
        model = TransNamelist
        fields = ['dv_no', 'name', 'purpose', 'amount', 'dv_date',
                  'amt_budget', 'amt_journal', 'approval_date', 'check_issued', 'check_released']