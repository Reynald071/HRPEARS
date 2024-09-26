# Generated by Django 3.2.16 on 2024-07-02 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppEligibility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('place', models.CharField(blank=True, max_length=500, null=True)),
                ('license_number', models.CharField(blank=True, max_length=500, null=True)),
                ('license_dov', models.DateField(blank=True, null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='applications/eligibility/%Y/%m')),
            ],
            options={
                'db_table': 'app_eligibility',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AppStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Application Status',
                'verbose_name_plural': 'Application Status',
                'db_table': 'app_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_no', models.CharField(blank=True, max_length=50, null=True)),
                ('date_of_app', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=150, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=150, null=True)),
                ('last_name', models.CharField(blank=True, max_length=150, null=True)),
                ('extension', models.CharField(blank=True, max_length=50, null=True)),
                ('sex', models.IntegerField(blank=True, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=11, null=True)),
                ('course', models.CharField(blank=True, max_length=255, null=True)),
                ('work_exp', models.CharField(blank=True, max_length=500, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=50, null=True)),
                ('street', models.CharField(blank=True, max_length=500, null=True)),
                ('tor', models.FileField(blank=True, null=True, upload_to='applications/tor/%Y/%m')),
                ('app_letter', models.FileField(blank=True, null=True, upload_to='applications/app-letter/%Y/%m')),
                ('pds', models.FileField(blank=True, null=True, upload_to='applications/pds/%Y/%m')),
                ('we_sheet', models.FileField(blank=True, null=True, upload_to='applications/we-sheet/%Y/%m')),
                ('cert_training', models.FileField(blank=True, null=True, upload_to='applications/cert-training/%Y/%m')),
                ('cert_employment', models.FileField(blank=True, null=True, upload_to='applications/cert-employment/%Y/%m')),
                ('ipcr', models.FileField(blank=True, null=True, upload_to='applications/ipcr/%Y/%m')),
                ('is_rejected', models.IntegerField(blank=True, default=0)),
                ('remarks', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'job_applications',
                'managed': False,
            },
        ),
    ]
