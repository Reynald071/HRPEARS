from django.db import models

from backend.models import Empprofile


class ConvocationAttendance(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'convocation_attendance'


class ConvocationQRCode(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    qrcode = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'convocation_qrcode'


class ConvocationEvent(models.Model):
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'convocation_event'