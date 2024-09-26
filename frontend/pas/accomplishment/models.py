from django.db import models


class Dtr(models.Model):
    employeeid = models.IntegerField(primary_key=True)
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    verifytype = models.IntegerField(db_column='VerifyType', blank=True, null=True)  # Field name made lowercase.
    dev = models.IntegerField(db_column='Dev', blank=True, null=True)  # Field name made lowercase.
    station = models.BigIntegerField(db_column='Station', blank=True, null=True)  # Field name made lowercase.
    reclock = models.TextField(db_column='RecLock', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    serialcode = models.CharField(db_column='SerialCode', max_length=255, blank=True, null=True)  # Field name made lowercase.
    devsource = models.BigIntegerField(db_column='DevSource', blank=True, null=True)  # Field name made lowercase.
    emppic = models.TextField(db_column='EmpPic', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dtr'
        unique_together = (('employeeid', 'date', 'time'),)