# Generated by Django 3.0.5 on 2020-04-18 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0009_auto_20200418_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='ethnicity',
            field=models.CharField(choices=[('Bangladeshi', 'Bangladeshi'), ('ChineseIndian', 'ChineseIndian'), ('Sri Lankan', 'Sri Lankan')], default='Bangladeshi', max_length=15),
        ),
    ]
