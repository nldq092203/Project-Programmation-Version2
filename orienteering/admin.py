from django.contrib import admin
from . import models

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'department', 'email', 'role']
    search_fields = ['username', 'first_name', 'last_name', 'department']
    list_filter = ['department']
    fieldsets = [
        (None, {'fields': ['username', 'password']}),
        ('Personal info', {'fields': ['first_name', 'last_name', 'department', 'image', 'email', 'role']}),
    ]

class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'longitude', 'latitude']
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': ['name', 'longitude', 'latitude']}),
    ]
class GroupRunnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    search_fields = ['name', 'department']
    filter_horizontal = ['members']

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'start', 'end', 'location', 'coach', 'group_runner', 'publish']
    search_fields = ['name', 'location', 'coach', 'group_runner']
    list_filter = ['publish']
    fieldsets = [
        (None, {'fields': ['name', 'start', 'end', 'location', 'coach', 'group_runner', 'publish']}),
        ('Description', {'fields': ['subtitle', 'description', 'image', 'department']}),
    ]

class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'time_limit', 'race_type']
    search_fields = ['name', 'event', 'race_type']
    list_filter = ['race_type']
    fieldsets = [
        (None, {'fields': ['name', 'event', 'time_limit', 'race_type']}),
    ]

class CheckPointAdmin(admin.ModelAdmin):
    list_display = ['number', 'longitude', 'latitude', 'race']
    search_fields = ['number', 'race']
    list_filter = ['race']

class RaceRunnerAdmin(admin.ModelAdmin):
    list_display = ['runner', 'race', 'total_time', 'score']
    search_fields = ['runner', 'race']
    list_filter = ['race', 'runner']

class RaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class CheckPointRecord(admin.ModelAdmin):
    list_display = ['number', 'longitude', 'latitude', 'is_correct']

admin.site.register(models.Participant, ParticipantAdmin)
admin.site.register(models.GroupRunner, GroupRunnerAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.CheckPoint, CheckPointAdmin)
admin.site.register(models.RaceRunner, RaceRunnerAdmin)
admin.site.register(models.RaceType, RaceTypeAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.CheckPointRecord, CheckPointRecord)
