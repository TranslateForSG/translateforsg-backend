# Generated by Django 3.0.5 on 2020-04-20 06:21

from django.db import migrations


def copy_ordering(apps, schema_editor):
    Phrase = apps.get_model('translations', 'Phrase')

    from django.db.models import F
    Phrase.objects.all().update(
        order=F('id')
    )


class Migration(migrations.Migration):
    dependencies = [
        ('translations', '0015_auto_20200420_1421'),
    ]

    operations = [
        migrations.RunPython(copy_ordering)
    ]
