from django.contrib import admin
from .models import User, OfficialDocumentPic, SituationalDocumentPic, Location, FAQ, FAQCategory, Client

# Register your models here.

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Location)
admin.site.register(OfficialDocumentPic)
admin.site.register(SituationalDocumentPic)
admin.site.register(FAQ)
admin.site.register(FAQCategory)
