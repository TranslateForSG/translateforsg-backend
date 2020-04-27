# Generated by Django 3.0.5 on 2020-04-27 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0038_remove_category_parent_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Downloadable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.TextField(blank=True)),
                ('downloadable_file', models.FileField(upload_to='downloadables/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='translations.Language')),
            ],
        ),
    ]