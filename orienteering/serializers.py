from rest_framework import serializers
from . import models
from django.utils import timezone
from rest_framework.validators import UniqueTogetherValidator
import pytz

class ParticipantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    def validate_username(self, value):
        if models.Participant.objects.filter(username=value).exists():
            raise serializers.ValidationError("Participant with this username already exists.")
        return value
    
    def create(self, validated_data):
        user = models.Participant(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            department=validated_data.get('department', ''),
            image=validated_data.get('image', None), 
            role=validated_data.get('role', 'Runner')
        ) 
        user.set_password(validated_data['password']) # Hashing the password is required when using access tokens
        user.save()
        return user
    class Meta:
        model = models.Participant
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'department', 'image', 'role', 'password']



class GroupRunnerSerializer(serializers.ModelSerializer):
    # members = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     view_name='participant-detail',
    #     read_only=True
    # )
    # members = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = models.GroupRunner
        fields = ['id', 'name', 'members', 'department']
        validators = [
            UniqueTogetherValidator(
                queryset=models.GroupRunner.objects.all(),
                fields=['name', 'department']
            )
        ]



class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Location
        fields = ['id', 'name', 'longitude', 'latitude']
    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be a value between -180 and 180.")
        return value

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be a value between -90 and 90.")
        return value
class RaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RaceType
        fields = '__all__'


class CheckPointSerializer(serializers.ModelSerializer):
    race_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.CheckPoint
        fields = ['id', 'number', 'longitude', 'latitude', 'race_id', 'score']
        validators = [
            UniqueTogetherValidator(
                queryset=models.CheckPoint.objects.all(),
                fields=['number', 'race_id']
            )
        ]
        
    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be a value between -180 and 180.")
        return value

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be a value between -90 and 90.")
        return value


class RaceSerializer(serializers.ModelSerializer):
    # event = serializers.HyperlinkedRelatedField(
    #     view_name='event-detail',
    #     read_only=True
    # )
    event_id = serializers.IntegerField(write_only=True)
    checkpoints = serializers.SerializerMethodField()
    now = serializers.SerializerMethodField()
    

    def get_now(self, obj):
        return timezone.now()
    
    def validate(self, attrs):
        # if attrs['time_limit'] > attrs['event'].end - attrs['event'].start:
        #     raise serializers.ValidationError("Time limit must be less than event duration")
        # if attrs['time_limit'] < 0:
        #     raise serializers.ValidationError("Time limit must be positive")
        
        return super().validate(attrs)
    
    def get_checkpoints(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.groups.filter(name='Coach').exists():
            # Logic for coach
            return CheckPointSerializer(obj.checkpoints, many=True).data
        elif user.groups.filter(name='Runner').exists():
            paris_tz = pytz.timezone('Europe/Paris')
            now = timezone.now()
            paris_now = now.astimezone(paris_tz)
            start = obj.event.start.astimezone(paris_tz)
            if  start > paris_now:
                # Don't show checkpoints
                return []
            else:
                # Logic for runner
                # return []
                return CheckPointSerializer(obj.checkpoints, many=True).data
        else:
            # Default logic
            return []

    class Meta:
        model = models.Race
        fields = ['id', 'name', 'event_id', 'time_limit', 'race_type', 'checkpoints', 'now']

class EventSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    location_id = serializers.IntegerField(write_only=True)
    group_runner_id = serializers.IntegerField(write_only=True)

    races = RaceSerializer(read_only=True, many=True)
    # coach = ParticipantSerializer(read_only=True)
    group_runner = GroupRunnerSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    # coach = serializers.HyperlinkedRelatedField(
    #     view_name='participant-detail',
    #     read_only=True
    # )
    # group_runner = serializers.HyperlinkedRelatedField(
    #     view_name='group-runner-detail',
    #     read_only=True
    # )
    # location = serializers.HyperlinkedRelatedField(
    #     view_name='location-detail',
    #     read_only=True
    # )
    def validate(self, attrs):
        if 'start' in attrs and 'end' in attrs:
            if attrs['start'] > attrs['end']:
                raise serializers.ValidationError("The start time cannot be later than the end time.")
        return attrs
        
    class Meta:
        model = models.Event
        fields = ['id', 'name', 'start', 'end', 'location', 'location_id', 'coach', 'races', 'group_runner', 'group_runner_id', 'publish', 'subtitle', 'description', 'image', 'department', 'is_finished']

class CheckPointRecordSerializer(serializers.ModelSerializer):
    race_runner_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.CheckPointRecord
        fields = ['id', 'number', 'longitude', 'latitude', 'is_correct', 'race_runner_id']
    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be a value between -180 and 180.")
        return value

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be a value between -90 and 90.")
        return value

class RaceRunnerSerializer(serializers.ModelSerializer):
    # runner = serializers.HyperlinkedRelatedField(
    #     view_name='participant-detail',
    #     read_only=True
    # )
    runner = ParticipantSerializer(read_only=True)
    runner_id = serializers.IntegerField(write_only=True)

    # race = serializers.HyperlinkedRelatedField(
    #     view_name='race-detail',
    #     read_only=True
    # )
    race = RaceSerializer(read_only=True)
    race_id = serializers.IntegerField(write_only=True)
    checkpoint_records = CheckPointRecordSerializer(many=True, read_only=True)
    correct_checkpoints = serializers.JSONField(required=False)

    def validate_correct_checkpoints(self, value):
        if not all(isinstance(i, int) for i in value):
            raise serializers.ValidationError("All items in correct_checkpoints must be integers")
        return value
    
    def validate(self, attrs):
        # if attrs['total_time'] < 0:
        #     raise serializers.ValidationError("Total time must be positive")
        if attrs['score'] < 0:
            raise serializers.ValidationError("Score must be positive")
        return super().validate(attrs)
    
    class Meta:
        model = models.RaceRunner
        fields = ['id', 'runner', 'runner_id', 'race', 'race_id', 'total_time', 'score', 'checkpoint_records',  'correct_checkpoints']

