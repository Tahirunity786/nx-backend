# Generated by Django 5.1.2 on 2025-01-24 12:55

import ckeditor.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPostImageO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='services')),
                ('image_pb_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'blog_post_images',
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, default='', max_length=200)),
                ('post_slug', models.SlugField(blank=True, editable=False, max_length=300, unique=True)),
                ('content', ckeditor.fields.RichTextField()),
                ('tag', models.CharField(default='', max_length=100)),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('images', models.ManyToManyField(related_name='blog_postso', to='core_blog.blogpostimageo')),
            ],
            options={
                'db_table': 'blog_posts',
                'ordering': ['-date_posted'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_name', models.CharField(db_index=True, max_length=100)),
                ('user_email', models.EmailField(db_index=True, default='', max_length=254)),
                ('user_subject', models.CharField(db_index=True, default='', max_length=200)),
                ('user_message', models.TextField(db_index=True, default='')),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('comment_on_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core_blog.comment')),
                ('comment_on_post', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='core_blog.blogpost')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'db_table': 'comments',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='blog_posts', to='core_blog.comment'),
        ),
    ]
