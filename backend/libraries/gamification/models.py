from django.db import models
from django.utils import timezone

from backend.models import AuthUser


class GamifyLevels(models.Model):
    name = models.CharField(max_length=255, unique=True)
    value = models.IntegerField(unique=True)
    status = models.BooleanField(default=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    file = models.FileField(upload_to='badges/gamify')

    class Meta:
        db_table = 'gamify_levels'


class GamifyActivities(models.Model):
    activity = models.TextField()
    points = models.IntegerField()
    status = models.BooleanField(default=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    limit_per_day = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'gamify_activities'


class GamifyCurrentLevel(models.Model):
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)
    level = models.ForeignKey('GamifyLevels', models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'gamify_current_level'


class GamifyPoints(models.Model):
    activity = models.ForeignKey('GamifyActivities', models.DO_NOTHING)
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'gamify_points'
