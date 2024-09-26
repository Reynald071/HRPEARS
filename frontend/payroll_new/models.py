from django.db import models
from django.contrib import admin

from backend.models import Empprofile


class Payslip(models.Model):
    fldempid = models.CharField(max_length=11, blank=True, null=True)
    fldemp_name = models.CharField(max_length=64, blank=True, null=True)
    fldpay_period = models.CharField(max_length=24, blank=True, null=True)
    fldgroupid = models.CharField(max_length=11, blank=True, null=True)
    # EARN
    fldearn_desc1 = models.CharField(max_length=32, blank=True, null=True)
    fldearn_amt1 = models.FloatField(blank=True, null=True)
    fldearn_desc2 = models.CharField(max_length=32, blank=True, null=True)
    fldearn_amt2 = models.FloatField(blank=True, null=True)
    fldearn_desc3 = models.CharField(max_length=32, blank=True, null=True)
    fldearn_amt3 = models.FloatField(blank=True, null=True)
    fldearn_desc4 = models.CharField(max_length=32, blank=True, null=True)
    fldearn_amt4 = models.FloatField(blank=True, null=True)
    fldearn_desc5 = models.CharField(max_length=32, blank=True, null=True)
    fldearn_amt5 = models.FloatField(blank=True, null=True)
    # DEDUCT
    fldded_desc1 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt1 = models.FloatField(blank=True, null=True)
    fldded_desc2 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt2 = models.FloatField(blank=True, null=True)
    fldded_desc3 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt3 = models.FloatField(blank=True, null=True)
    fldded_desc4 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt4 = models.FloatField(blank=True, null=True)
    fldded_desc5 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt5 = models.FloatField(blank=True, null=True)
    fldded_desc6 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt6 = models.FloatField(blank=True, null=True)
    fldded_desc7 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt7 = models.FloatField(blank=True, null=True)
    fldded_desc8 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt8 = models.FloatField(blank=True, null=True)
    fldded_desc9 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt9 = models.FloatField(blank=True, null=True)
    fldded_desc10 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt10 = models.FloatField(blank=True, null=True)
    fldded_desc11 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt11 = models.FloatField(blank=True, null=True)
    fldded_desc12 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt12 = models.FloatField(blank=True, null=True)
    fldded_desc13 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt13 = models.FloatField(blank=True, null=True)
    fldded_desc14 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt14 = models.FloatField(blank=True, null=True)
    fldded_desc15 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt15 = models.FloatField(blank=True, null=True)
    fldded_desc16 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt16 = models.FloatField(blank=True, null=True)
    fldded_desc17 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt17 = models.FloatField(blank=True, null=True)
    fldded_desc18 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt18 = models.FloatField(blank=True, null=True)
    fldded_desc19 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt19 = models.FloatField(blank=True, null=True)
    fldded_desc20 = models.CharField(max_length=32, blank=True, null=True)
    fldded_amt20 = models.FloatField(blank=True, null=True)
    # ----
    fldremarks = models.CharField(max_length=128, blank=True, null=True)
    flddateposted = models.DateField(blank=True, null=True)
    fldslip_copy = models.SmallIntegerField(blank=True, null=True)
    fldtotal_earnings = models.FloatField(blank=True, null=True)
    fldtotal_deductions = models.FloatField(blank=True, null=True)
    fldpayroll_code = models.CharField(max_length=100, blank=True, null=True)

    @property
    def get_pay_period(self):
        return self.fldpay_period[:4] + '-' + self.fldpay_period[4:]

    @property
    def get_fields(self):
        return [(field.name, getattr(self, field.name)) for field in Payslip._meta.fields]

    class Meta:
        managed = False
        db_table = 'view_tblpayslip'


