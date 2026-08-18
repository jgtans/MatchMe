from django.contrib import admin

from .models import DateInvite, ProfilePhoto, ProfileReaction, ViewHistory

admin.site.register(ProfilePhoto)
admin.site.register(ProfileReaction)
admin.site.register(ViewHistory)
admin.site.register(DateInvite)
