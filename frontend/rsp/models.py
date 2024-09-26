from django.db import models

from backend.models import Empprofile


class RspIntroLetter(models.Model):
    content = models.TextField(blank=True, null=True)
    emp_id = models.IntegerField(blank=True, null=True)
    generated_drn = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    status = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'rsp_intro_letter'