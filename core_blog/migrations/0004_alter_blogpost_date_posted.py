# Generated by Django 5.1.2 on 2024-12-01 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_blog', '0003_alter_blogpost_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='date_posted',
            field=models.DateField(auto_now_add=True),
        ),
    ]
