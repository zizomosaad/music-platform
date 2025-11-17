from django.contrib import admin

# Register your models here.
from ..albums.models import Albums
from ..artists.models import Artist

class AlbumsAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)

admin.site.register(Albums, AlbumsAdmin)
admin.site.register(Artist)
