from django.db import models

from backend.infimos.models import TransPayeename


class TransNamelist(models.Model):
    namelist_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(TransPayeename, models.DO_NOTHING, to_field='transaction_id')
    id_number = models.CharField(max_length=15, db_collation='latin1_swedish_ci', blank=True, null=True)
    name = models.CharField(max_length=100, db_collation='latin1_swedish_ci', blank=True, null=True)
    purpose = models.TextField(db_collation='latin1_swedish_ci', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ppa_code = models.CharField(max_length=50, db_collation='latin1_swedish_ci', blank=True, null=True)
    charge_code = models.CharField(max_length=50, db_collation='latin1_swedish_ci', blank=True, null=True)
    set_code = models.CharField(max_length=50, db_collation='latin1_swedish_ci', blank=True, null=True)
    ppa_id = models.IntegerField(blank=True, null=True)
    charge_id = models.IntegerField(blank=True, null=True)
    set_id = models.IntegerField(blank=True, null=True)
    employee_id = models.IntegerField(blank=True, null=True)
    userlog = models.CharField(max_length=20, db_collation='latin1_swedish_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trans_namelist'