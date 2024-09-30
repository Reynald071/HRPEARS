from django.db import models

from backend.models import Empprofile


class PasEmpPayrollNotification(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    dv_no = models.CharField(max_length=255, blank=True, null=True)
    date_sent = models.DateTimeField(blank=True, null=True)
    period_date = models.CharField(max_length=255, blank=True, null=True)
    sentby = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='sentby')
    purpose = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_emp_payroll_notification'