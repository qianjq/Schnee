# Generated by Django 2.0.3 on 2018-11-14 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lenotes', '0006_auto_20181114_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='diary_log',
            field=models.TextField(default='2018-11-14 21:08:38.232230  Create diary'),
        ),
    ]