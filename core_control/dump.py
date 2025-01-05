

class PortfolioImages(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False,default="",  unique=True)
    media = models.ImageField(upload_to="portfolio", default="", db_index=True)
    tag = models.CharField(max_length=100, default="", db_index=True)
    image_pb_id = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self) -> str:
        
        return self.tag
    
    def save(self, *args, **kwargs):
        if self.image:
            upload_result = cloudinary_upload(self.media)
            # Save only the public ID, not the full URL
            self.image_pb_id = upload_result['public_id']
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'
    
        if not self.services_slug:
            self.services_slug = slugify(self.title or str(uuid.uuid4()))
    
        super().save(*args, **kwargs)


class Portfolio(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, editable=False,default="",  unique=True)
    image = models.ManyToManyField(PortfolioImages, db_index=True)
    description = models.TextField(default="", db_index=True)
    title = models.CharField(max_length=100, default="", db_index=True)
    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self._id:
            self._id = f'service_{uuid.uuid4()}'    
        super().save(*args, **kwargs)

