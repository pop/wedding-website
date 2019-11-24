from django.contrib import admin
from .models import Guest, Party


class GuestInline(admin.TabularInline):
    model = Guest
    fields = ('first_name', 'last_name', 'email', 'is_attending')
    readonly_fields = ('first_name', 'last_name', 'email')


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'invitation_sent', 'rehearsal_dinner', 'invitation_opened',
                    'is_invited', 'is_attending')
    list_filter = ('is_invited', 'is_attending', 'rehearsal_dinner', 'invitation_opened')
    inlines = [GuestInline]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party', 'email', 'is_attending')
    list_filter = ('is_attending', 'party__is_invited', 'party__rehearsal_dinner')


admin.site.register(Party, PartyAdmin)
admin.site.register(Guest, GuestAdmin)
