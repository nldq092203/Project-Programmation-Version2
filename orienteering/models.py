from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta

class Participant(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    ROLE_CHOICES = [
        ('Coach', 'Coach'),
        ('Runner', 'Runner'),
    ]
    department = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    group = models.ForeignKey(Group, related_name='custom_user_group', on_delete=models.CASCADE,  null=True)
    user_permission = models.ForeignKey(Permission, related_name='custom_user_permission', on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
class GroupRunner(models.Model):
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    members = models.ManyToManyField(Participant, related_name='member_group_runners', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

class Event(models.Model):
    name = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    coach = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='events')
    group_runner = models.ForeignKey(GroupRunner, on_delete=models.CASCADE, related_name='events')
    publish = models.BooleanField(default=False)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='event_images', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_finished = models.BooleanField(default=False)

class RaceType(models.Model):
    name = models.CharField(max_length=100)
    rule = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Race(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="races")
    time_limit = models.DurationField()
    race_type = models.ForeignKey(RaceType, on_delete=models.CASCADE, related_name='races')

class CheckPoint(models.Model):
    number = models.IntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='checkpoints')
    score = models.IntegerField(default=0, blank=True, null=True)

class CheckPointRecord(models.Model):
    number = models.IntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    is_correct = models.BooleanField(blank=True, null=True)
    race_runner = models.ForeignKey('RaceRunner', on_delete=models.CASCADE, related_name='checkpoint_records')
                        
class RaceRunner(models.Model):
    runner = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="race_runners")
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="race_runners")
    total_time = models.DurationField(blank=True, null=True, default=timedelta(0))
    score = models.IntegerField(default=0,blank=True, null=True)
    is_finished = models.BooleanField(default=False)
    correct_checkpoints = models.JSONField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.correct_checkpoints is None:
            self.correct_checkpoints = []
    




    
