# Generated by Django 5.1.2 on 2024-11-17 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_control', '0006_rename_contact_contactus'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactus',
            name='contact_no',
            field=models.PositiveBigIntegerField(db_index=True, default=0),
        ),
    ]