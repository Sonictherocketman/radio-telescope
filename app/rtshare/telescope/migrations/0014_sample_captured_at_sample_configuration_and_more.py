# Generated by Django 5.0 on 2024-04-25 23:11

import django.core.files.storage
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telescope', '0013_alter_observation_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='captured_at',
            field=models.DateTimeField(blank=True, default=None, help_text='The timestamp when the data was collected.', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='configuration',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='samples', to='telescope.configuration'),
        ),
        migrations.AddField(
            model_name='sample',
            name='frequency',
            field=models.PositiveBigIntegerField(blank=True, default=None, help_text='The center frequency that was captured (in Hz).', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='gain',
            field=models.PositiveSmallIntegerField(blank=True, default=None, help_text='The amount of gain applied to the SDR.', null=True, validators=[django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='sample',
            name='ppm',
            field=models.PositiveSmallIntegerField(blank=True, default=None, help_text='The PPM offset used for the device (0 is none).', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='sample_rate',
            field=models.PositiveBigIntegerField(blank=True, default=None, help_text='The sample rate at which data was collected.', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='sample_size',
            field=models.PositiveBigIntegerField(blank=True, default=None, help_text='The number of samples in the record.', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='telescope',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='samples', to='telescope.telescope'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='data',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to='data/'),
        ),
    ]
