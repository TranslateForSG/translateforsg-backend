# Generated by Django 3.0.5 on 2020-04-17 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0005_auto_20200417_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
