# Generated by Django 5.1.2 on 2024-11-02 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(db_index=True, upload_to='services')),
                ('title', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField(db_index=True)),
            ],
        ),
    ]