# Generated by Django 3.0.5 on 2020-04-18 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0008_auto_20200418_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilitySlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='preferred_days',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='preferred_shifts',
        ),
        migrations.DeleteModel(
            name='DayOfWeek',
        ),
        migrations.DeleteModel(
            name='Shift',
        ),
        migrations.AddField(
            model_name='volunteer',
            name='availability_slots',
            field=models.ManyToManyField(blank=True, to='translations.AvailabilitySlot'),
        ),
    ]
