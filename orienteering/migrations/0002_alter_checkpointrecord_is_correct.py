# Generated by Django 5.0.6 on 2024-06-20 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orienteering', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkpointrecord',
            name='is_correct',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]