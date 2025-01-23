from django.contrib import admin
from core_control.models import CustomUser, AnonymousCookies, Service, ContactUS, Technologies, Portfolio, PortfolioImages, Profile, Education, Skills, Awards

class PortfolioImagesInline(admin.TabularInline):
    model = Portfolio.image.through  # Use the intermediate model
    extra = 1  # Number of empty forms to display

class PortfolioAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        portfolio = form.instance
        # Ensure unique images in the ManyToMany relationship
        unique_images = portfolio.image.all().distinct()
        portfolio.image.set(unique_images)

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(AnonymousCookies)
admin.site.register(Service)
admin.site.register(ContactUS)
admin.site.register(Technologies)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(PortfolioImages)
admin.site.register(Profile)
admin.site.register(Skills)
admin.site.register(Education)
admin.site.register(Awards)
