from django.contrib import admin

# Register your models here.

from .models import Artist
from albums.models import Albums

@admin.display(description="Number of Albums")
def count_albums(obj):
    count = 0
    for album in obj.albums.all():
        if album.isApproved:
            count += 1
    return count

class AlbumsInline(admin.TabularInline):
    model = Albums
    extra = 1
    fields = ("name", "release_date", "cost", "isApproved")
    readonly_fields = ("created_at",)  # optional: show created_at but not editable
    show_change_link = True

class ArtistAdmin(admin.ModelAdmin):
    inlines = [AlbumsInline]
    list_display = ("stage_name", "social_link", count_albums)
    ordering = ("stage_name",)


admin.site.register(Artist, ArtistAdmin)
