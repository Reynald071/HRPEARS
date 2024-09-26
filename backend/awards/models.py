import os
from django.db import models
from django.dispatch import receiver
from django.contrib import admin


class Awards(models.Model):
    name = models.CharField(max_length=500)
    category = models.ForeignKey('Awcategory', models.DO_NOTHING)
    year = models.IntegerField()
    level = models.ForeignKey('Awlevels', models.DO_NOTHING)
    badge = models.ForeignKey('Badges', models.DO_NOTHING)
    classification = models.ForeignKey('Classification', models.DO_NOTHING)
    uploaded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)
    nomination_start = models.DateField(blank=True, null=True)
    nomination_end = models.DateField(blank=True, null=True)
    is_nomination = models.IntegerField()
    status = models.BooleanField()

    @admin.display(description='Classification')
    def display_class_shortname(self):
        return self.classification.shortname

    class Meta:
        verbose_name_plural = 'Awards'
        db_table = 'aw_awards'


class AwEligibility(models.Model):
    eligibility = models.TextField(blank=True, null=True)
    awards = models.ForeignKey('Awards', models.DO_NOTHING)

    class Meta:
        db_table = 'aw_eligibility'


class AwEligibilityChecklist(models.Model):
    nominees = models.ForeignKey('Nominees', models.DO_NOTHING)
    eligibility = models.ForeignKey('AwEligibility', models.DO_NOTHING)

    class Meta:
        db_table = 'aw_eligibility_checklist'


class Badges(models.Model):
    url = models.FileField(upload_to='badges/%Y/%m')
    name = models.CharField(max_length=150)
    uploaded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = "Badges"
        db_table = 'aw_badges'


class Classification(models.Model):
    name = models.CharField(max_length=300)
    shortname = models.CharField(max_length=150, blank=True, null=True)
    status = models.IntegerField()
    uploaded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Classification'
        verbose_name_plural = "Classifications"
        db_table = 'aw_classification'


class Awlevels(models.Model):
    name = models.CharField(max_length=150)
    status = models.IntegerField()
    uploaded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Level'
        verbose_name_plural = "Levels"
        db_table = 'aw_level'


class Awcategory(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    uploaded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)
    icon = models.CharField(max_length=255)
    needs_title = models.BooleanField(verbose_name="Extra Field")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
        db_table = 'aw_category'


class Nominees(models.Model):
    datetime = models.DateTimeField()
    nominated_by = models.ForeignKey('Empprofile', models.DO_NOTHING, db_column='nominated_by_id',
                                     related_name='nominated_by')
    nominee = models.ForeignKey('Empprofile', models.DO_NOTHING, db_column='nominee_id')
    why = models.TextField(blank=True, null=True)
    awards = models.ForeignKey('Awards', models.DO_NOTHING)
    status = models.IntegerField()
    is_winner = models.IntegerField()
    title = models.CharField(max_length=512)

    class Meta:
        db_table = 'aw_nominees'


class Prizes(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=150)
    awards = models.ForeignKey('Awards', models.DO_NOTHING)

    class Meta:
        db_table = 'aw_prizes'


class Attachments(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='awards/%Y/%m')
    awards = models.ForeignKey('Awards', models.DO_NOTHING)

    class Meta:
        db_table = 'aw_attachments'


class Criteria(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    percentage = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField()
    awards = models.ForeignKey('Awards', models.DO_NOTHING)

    class Meta:
        db_table = 'aw_criteria'


class Deliberation(models.Model):
    criteria = models.ForeignKey('Criteria', models.DO_NOTHING)
    nominee = models.ForeignKey('Nominees', models.DO_NOTHING)
    grade = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey('Empprofile', models.DO_NOTHING)
    graded_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'aw_deliberation'


class AwGuidelines(models.Model):
    title = models.CharField(max_length=1024, blank=True, null=True)
    file = models.FileField(upload_to='awards/guidelines/')
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'aw_guidelines'


@receiver(models.signals.post_delete, sender=AwGuidelines)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

