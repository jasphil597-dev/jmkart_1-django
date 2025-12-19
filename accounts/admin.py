from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


class AccountAdmin(UserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'username',
        'last_login',
        'date_joined',
        'is_active',
    )
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius:50%;">',
                obj.profile_picture.url,
            )
        return "-"

    thumbnail.short_description = 'Profile Picture'


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# ==============================================

# My code:

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import Account, UserProfile
# from django.utils.html import format_html

# # Register your models here.

# class AccountAdmin(UserAdmin):
#   list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
#   list_display_links = ('email', 'first_name', 'last_name') # this makes the email, first & last_name clickable
#   readonly_fields = ('last_login', 'date_joined')
#   ordering = ('-date_joined',) # this gives us descending list

#   filter_horizontal = ()
#   list_filter = ()
#   fieldsets = ()  # this maakes password read only

# class UserProfileAdmin(admin.ModelAdmin):
#     def thumbnail(self, object):
#         return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
#     thumbnail.short_description = 'Profile Picture'
#     list_display = ('thumbnail', 'user', 'city', 'state', 'country')

# admin.site.register(Account, AccountAdmin)
# admin.site.register(UserProfile, UserProfileAdmin)

