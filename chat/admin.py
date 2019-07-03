from django.contrib import admin
from chat.models import Message, UserProfile, Room

# Register your models here.
admin.site.register(Message)
admin.site.register(UserProfile)
admin.site.register(Room)
