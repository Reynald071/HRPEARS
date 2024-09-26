from colorfield.fields import ColorField
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html

from backend.models import AuthUser


class CalendarPermission(models.Model):
    type = models.ForeignKey('CalendarType', models.DO_NOTHING)
    emp = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'calendar_permission'


class CalendarType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)
    scope = models.IntegerField(default=1)
    color = ColorField(format='hexa')
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(description='Color')
    def display_color(self):
        return format_html(
            '<i class="fas fa-square-full" style="color:{}"></i>', self.color
        )

    @admin.display(description='Scope')
    def display_scope(self):
        if self.scope == 1:
            return format_html('<i class="fas fa-shield-alt" title="Private"></i>')
        else:
            return format_html('<i class="fas fa-globe" title="Public"></i>')

    @property
    def get_calendar_approvers(self):
        return CalendarPermission.objects.filter(type_id=self.id).values_list('emp_id', flat=True)

    class Meta:
        verbose_name = 'Type'
        verbose_name_plural = "Types"
        managed = False
        db_table = 'calendar_type'


class CalendarEvent(models.Model):
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime_real = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey('CalendarType', models.DO_NOTHING)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    remarks = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)

    @property
    def get_users_for_calendar_type(self):
        return CalendarPermission.objects.filter(type_id=self.type_id).values_list('emp_id', flat=True)

    @property
    def get_approved(self):
        return CalendarEventApproval.objects.filter(event_id=self.id).first()

    class Meta:
        db_table = 'calendar_event'


class CalendarShared(models.Model):
    type = models.ForeignKey('CalendarType', models.DO_NOTHING)
    emp = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'calendar_shared'


class CalendarEventApproval(models.Model):
    status_from = models.IntegerField()
    status_to = models.IntegerField()
    emp = models.ForeignKey(AuthUser, models.DO_NOTHING)
    remarks = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    event = models.ForeignKey('CalendarEvent', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'calendar_event_approval'
