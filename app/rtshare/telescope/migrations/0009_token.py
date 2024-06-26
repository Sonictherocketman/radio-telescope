# Generated by Django 4.2 on 2024-04-17 23:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('telescope', '0008_remove_telescope_status_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='The exact time when a record was created.')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, help_text='The exact time when a record was last updated.')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='The unique identifier for this record.', unique=True)),
                ('key', models.CharField(max_length=40, unique=True)),
                ('telescope', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='telescope.telescope')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
