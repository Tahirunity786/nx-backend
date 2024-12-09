from django.db import models
from typing import Optional
import uuid
from cloudinary.uploader import upload as cloudinary_upload, destroy as cloudinary_destroy
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils.timezone import now


# Create your models here.
class BlogPostImageO(models.Model):
    image = models.ImageField(upload_to='services')
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Ensure the image is uploaded to Cloudinary
        if self.image and not self.image_pb_id:
            try:
                upload_result = cloudinary_upload(self.image)
                self.image_pb_id = upload_result.get('public_id')
            except Exception as e:
                raise RuntimeError(f"Error uploading image to Cloudinary: {e}")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Ensure the image is removed from Cloudinary
        if self.image_pb_id:
            try:
                cloudinary_destroy(self.image_pb_id)
            except Exception as e:
                raise RuntimeError(f"Error deleting image from Cloudinary: {e}")
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'blog_post_images'

    def __str__(self):
        return f"Image {self.image_pb_id or 'Unuploaded'}"


class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    images = models.ManyToManyField(BlogPostImageO, related_name='blog_postso')
    title = models.CharField(max_length=200, db_index=True, default="")
    post_slug = models.SlugField(max_length=300, unique=True, blank=True, editable=False)
    content = RichTextField()
    tag = models.CharField(max_length=100, default="")
    date_posted = models.DateField(auto_now_add=True)
    comments = models.ManyToManyField('Comment', related_name='blog_posts', blank=True)

    class Meta:
        db_table = 'blog_posts'
        ordering = ['-date_posted']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.post_slug:
            self.post_slug = slugify(self.title or str(uuid.uuid4()))
        
        super().save(*args, **kwargs)

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment_on_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, default='', null=True)
    user_name = models.CharField(max_length=100, db_index=True)
    user_email = models.EmailField(db_index=True, default='')
    user_subject = models.CharField(max_length=200, db_index=True, default='')
    user_message = models.TextField(default='', db_index=True)
    comment_on_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    date_posted = models.DateTimeField(auto_now_add=True)  # Use only auto_now_add=True

    class Meta:
        db_table = 'comments'
        ordering = ['id']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by {self.user_name or 'Unknown User'}"
