from typing import Optional
import uuid
import cloudinary
from django.db import models
from django.utils.text import slugify

class Service(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False, unique=True)
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='services')  # Will upload to Cloudinary's "services" folder
    title = models.CharField(max_length=100, db_index=True)
    services_slug = models.SlugField(max_length=300, unique=True, blank=True, editable=False)
    description = models.TextField(db_index=True)
    technologies = models.ManyToManyField('Technologies', db_index=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['title']

    def save(self, *args, **kwargs):
        if self.image:
            upload_result = cloudinary.uploader.upload(self.image)
            # Save only the public ID, not the full URL
            self.image_pb_id = upload_result['public_id']
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'
    
        if not self.services_slug:
            self.services_slug = slugify(self.title or str(uuid.uuid4()))
    
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

class Technologies(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(db_index=True)

class ContactUS(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False, unique=True)
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
    