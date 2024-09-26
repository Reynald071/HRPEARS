from django.db import models
from backend.models import AuthUser, Empprofile
from frontend.models import Rito


class ApprovedRito(models.Model):
    rito = models.ForeignKey(Rito, models.DO_NOTHING)
    supervisor = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'pas_rito_approved'
