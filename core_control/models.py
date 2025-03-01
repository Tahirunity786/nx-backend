import datetime
import uuid
import jwt
from cloudinary.uploader import upload as cloudinary_upload, destroy as cloudinary_destroy
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from django.conf import settings



class AnonymousCookies(models.Model):
    cookie = models.CharField(max_length=200, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.cookie:  # Generate a unique _id if not already set
            self.cookie = uuid.uuid4()
        super().save(*args, **kwargs)
    
    def __str__(self)->str:
        return f"{self.cookie}"

class CustomUser(models.Model):
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(db_index=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    admin = models.BooleanField(default=False)

    users_messaging_container = models.ManyToManyField('self', symmetrical=False, blank=True)
    chat_room_id = models.UUIDField(null=True)

    fcm_token = models.ForeignKey('TokenSaver', on_delete=models.CASCADE, db_index=True, null=True, blank=True, default='')

    def __str__(self)->str:
        return f"{self.first_name} {self.last_name}"
    

    def save(self, *args, **kwargs):
        if not self.chat_room_id:  # Generate a unique _id if not already set
            self.chat_room_id = uuid.uuid4()
        super().save(*args, **kwargs)

class TokenSaver(models.Model):
    token = models.CharField(max_length=300, db_index=True, default='',  null=True)



class Technologies(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False, unique=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(db_index=True)

    def save(self, *args, **kwargs):
        if not self._id:  # Generate a unique _id if not already set
            self._id = f'tech_{uuid.uuid4()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Service(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False,default="",  unique=True)
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='services', null=True, blank=True)  # Will upload to Cloudinary's "services" folder
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


class PortfolioImages(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False,default="",  unique=True)
    media = models.ImageField(upload_to="portfolio", default="", db_index=True)
    tag = models.CharField(max_length=100, default="", db_index=True)
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self) -> str:
        
        return self.tag
    
    def save(self, *args, **kwargs):
        if self.media:
            upload_result = cloudinary_upload(self.media)
            # Save only the public ID, not the full URL
            self.image_pb_id = upload_result['public_id']
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'
        super().save(*args, **kwargs)

class Portfolio(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(
        max_length=100, 
        editable=False, 
        default="", 
        unique=True  # Keep unique constraint
    )
    image = models.ManyToManyField(PortfolioImages, db_index=True)
    description = models.TextField(default="", db_index=True)
    title = models.CharField(max_length=100, default="", db_index=True)
    
    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'portfolio_{uuid.uuid4()}'
        super().save(*args, **kwargs)  # Save the Portfolio instance first

class Education(models.Model):
    college_name = models.CharField(max_length=100, default="", db_index=True)
    degree = models.CharField(max_length=100, default="", db_index=True)
    from_year = models.DateField(db_index=True)
    to_year = models.DateField(db_index=True)
    def __str__(self) -> str:
        return self.college_name


class Awards(models.Model):
    institue_name = models.CharField(max_length=100, default="", db_index=True)
    awar_name = models.CharField(max_length=100, default="", db_index=True)
    year = models.DateField(db_index=True)
    def __str__(self) -> str:
        return self.awar_name

class Skills(models.Model):
    skill_name = models.CharField(max_length=100, default="", db_index=True)
    def __str__(self) -> str:
        return self.skill_name


class Profile(models.Model):
    profile = models.ImageField(upload_to='profiles', db_index=True)
    slug = models.SlugField(
        max_length=100, 
        editable=False, 
        default="", 
        unique=True  # Keep unique constraint
    )
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=100, default="", db_index=True)
    bio = models.TextField(db_index=True)
    experience = models.TextField(db_index=True)
    education = models.ManyToManyField(Education, db_index=True)
    awards = models.ManyToManyField(Awards, db_index=True, blank=True)
    skills = models.ManyToManyField(Skills, db_index=True)
    def __str__(self) -> str:
            return self.full_name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'portfolio_{uuid.uuid4()}'

        if self.profile:
            upload_result = cloudinary_upload(self.profile)
            # Save only the public ID, not the full URL
            self.image_pb_id = upload_result['public_id']

        super().save(*args, **kwargs)  # Save the Portfolio instance first
