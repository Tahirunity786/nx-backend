# Generated by Django 5.1.2 on 2024-11-02 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_control', '0002_service_delete_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image_pb_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]