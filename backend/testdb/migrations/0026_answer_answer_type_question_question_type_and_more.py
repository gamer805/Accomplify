# Generated by Django 5.0.7 on 2024-07-29 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testdb', '0025_auto_20240710_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answer_type',
            field=models.TextField(default='-'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.TextField(default='-'),
        ),
        migrations.AlterField(
            model_name='datasheet',
            name='data_file',
            field=models.FileField(upload_to='datasheets'),
        ),
    ]
