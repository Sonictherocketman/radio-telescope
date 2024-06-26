# Generated by Django 5.0 on 2024-06-14 23:22

from django.db import migrations


def copy_data(apps, schema_editor):

    # Observations

    Observation1 = apps.get_model('telescope', 'Observation')
    Observation2 = apps.get_model('observations', 'Observation')
    db_alias = schema_editor.connection.alias
    Observation2.objects.using(db_alias).bulk_create([
        Observation2(**values)
        for values in Observation1.objects.order_by('id').values(
            'uuid',
            'name',
            'created_at',
            'updated_at',
            'start_at',
            'end_at',
        )
    ])

    for observation1 in Observation1.objects.all():
        observation2 = Observation2.objects.get(uuid=observation1.uuid)
        observation2.telescopes.set(observation1.telescopes.all())

    # Configurations

    Configuration1 = apps.get_model('telescope', 'Configuration')
    Configuration2 = apps.get_model('observations', 'Configuration')
    db_alias = schema_editor.connection.alias
    Configuration2.objects.using(db_alias).bulk_create([
        Configuration2(**values)
        for values in Configuration1.objects.order_by('id').values(
            'uuid',
            'name',
            'created_at',
            'updated_at',
            'observation_id',
            'frequency',
            'sample_rate',
            'sample_size',
            'ppm',
            'gain',
        )
    ])

    # Samples

    Sample1 = apps.get_model('telescope', 'Sample')
    Sample2 = apps.get_model('observations', 'Sample')
    db_alias = schema_editor.connection.alias
    Sample2.objects.using(db_alias).bulk_create([
        Sample2(**values)
        for values in Sample1.objects.order_by('id').values(
            'uuid',
            'created_at',
            'updated_at',
            'observation_id',
            'telescope_id',
            'configuration_id',
            'frequency',
            'sample_rate',
            'sample_size',
            'ppm',
            'gain',
            'captured_at',
            'data',
        )
    ])

def no_op(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            copy_data,
            no_op,
        ),
    ]
