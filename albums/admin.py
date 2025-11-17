from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Albums, Song


class AlbumsAdminForm(forms.ModelForm):
    class Meta:
        model = Albums
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add help text for the boolean without changing the model field
        if "isApproved" in self.fields:
            self.fields["isApproved"].help_text = (
                "Approve the album if its name is not explicit"
            )


class RequiredSongInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # count forms that will be saved (not marked for deletion and with cleaned_data)
        valid_forms = 0
        for form in self.forms:
            # forms that weren't submitted/are empty may have empty cleaned_data
            cd = getattr(form, "cleaned_data", None)
            if not cd:
                continue
            if cd.get("DELETE", False):
                continue
            # this form will be saved (either existing or new)
            valid_forms += 1

        if valid_forms < 1:
            raise ValidationError(
                "An album must have at least one song. You cannot remove all songs."
            )


class SongInline(admin.TabularInline):
    model = Song
    formset = RequiredSongInlineFormset
    extra = 1
    fields = ("name", "image", "audio")
    show_change_link = True


class SongAdmin(admin.ModelAdmin):

    list_display = ("name", "album")


class AlbumsAdmin(admin.ModelAdmin):
    form = AlbumsAdminForm
    readonly_fields = ("created_at",)
    inlines = [SongInline]


admin.site.register(Albums, AlbumsAdmin)
admin.site.register(Song, SongAdmin)
