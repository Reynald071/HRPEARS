from rest_framework import serializers

from frontend.payroll_new.models import Payslip


class PayslipSerializer(serializers.ModelSerializer):
    emp_id_no = serializers.CharField(source='fldempid', read_only=True)
    emp_name = serializers.CharField(source='fldemp_name', read_only=True)
    pay_period = serializers.CharField(source='get_pay_period', read_only=True)
    date_posted = serializers.DateField(source='flddateposted', format="%b %d, %Y", read_only=True)

    class Meta:
        model = Payslip
        fields = ['id', 'fldpayroll_code', 'emp_id_no', 'emp_name', 'pay_period', 'fldgroupid', 'date_posted']
