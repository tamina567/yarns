# Generated by Django 2.2.1 on 2019-05-13 06:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0003_auto_20190513_0521'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date_joined'),
            preserve_default=False,
        ),
    ]
