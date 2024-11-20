from typing import Optional
import uuid
from cloudinary.uploader import upload as cloudinary_upload, destroy as cloudinary_destroy

from django.db import models
from django.utils.text import slugify


class Technologies(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, default="", editable=False, unique=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(db_index=True)

    def __str__(self):
        return self.title
    
class Service(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False,default="",  unique=True)
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='services')  # Will upload to Cloudinary's "services" folder
    title = models.CharField(max_length=100, db_index=True)
    services_slug = models.SlugField(max_length=300, unique=True, blank=True, editable=False)
    description = models.TextField(db_index=True)
    technologies = models.ManyToManyField(Technologies, db_index=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['title']

    def save(self, *args, **kwargs):
        if self.image:
            upload_result = cloudinary_upload(self.image)
            # Save only the public ID, not the full URL
            self.image_pb_id = upload_result['public_id']
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'
    
        if not self.services_slug:
            self.services_slug = slugify(self.title or str(uuid.uuid4()))
    
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title




class ContactUS(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False, default="", unique=True)
    name = models.CharField(max_length=100, db_index=True, default='')
    subject = models.CharField(max_length=100, db_index=True, default='')
    contact_no = models.PositiveBigIntegerField(db_index=True, default=0)
    email = models.EmailField(db_index=True, default='')
    message_detail = models.TextField(db_index=True, default='')
    date = models.DateTimeField(auto_now_add=True)
    file_assignment = models.FileField(upload_to='client/contact', null=True, blank=True, db_index=True)

    def __str__(self)->None:
        return f"Message has been sent by {self.name} at {self.date}"
    
    def save(self, *args, **kwargs):
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'
        super().save(*args, **kwargs)

class BlogPostImage(models.Model):
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
    images = models.ManyToManyField(BlogPostImage, related_name='blog_posts')
    title = models.CharField(max_length=200, db_index=True, default="")
    post_slug = models.SlugField(max_length=300, unique=True, blank=True, editable=False)
    content = models.TextField(default="")
    date_posted = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField('Comment', related_name='blog_posts')

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
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100, default="", db_index=True)

    class Meta:
        db_table = 'comments'
        ordering = ['name']

    def __str__(self):
        return f"Comment by {self.name}"


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default="", null=True)

    class Meta:
        db_table = 'users'
        ordering = ['name']

    def __str__(self):
        return self.name
