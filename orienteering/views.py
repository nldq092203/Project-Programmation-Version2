from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from .models import Participant, GroupRunner, Event, Location, RaceType, Race, CheckPoint, RaceRunner, CheckPointRecord
from .serializers import LocationSerializer, ParticipantSerializer, GroupRunnerSerializer, EventSerializer, RaceRunnerSerializer, RaceSerializer, CheckPointSerializer, RaceTypeSerializer, CheckPointRecordSerializer
from django_filters.rest_framework import DjangoFilterBackend
from . import filters
from datetime import timedelta
from django.utils import timezone
import datetime
from django.utils.duration import duration_string
import logging
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)


############################Authorization and Authentication#################################
# Register
class CustomParticipantCreateView(UserViewSet): 
    def create(self, request, *args, **kwargs):
        try:
            role = request.data.get('role', 'Runner')
            code_secret = request.data.get('secret_code')
            if not code_secret and role == 'Coach':
                return Response({"message": "Secret code is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            COACH_SECRET_CODE = settings.COACH_SECRET_CODE

            if role == 'Coach' and code_secret != COACH_SECRET_CODE:
                return Response({"message": "Invalid secret code."}, status=status.HTTP_400_BAD_REQUEST)
            response = super().create(request, *args, **kwargs)
            if response.status_code == status.HTTP_201_CREATED:
                user = Participant.objects.get(username=response.data['username'])
                if role == 'Coach':
                    group, created = Group.objects.get_or_create(name='Coach')
                    user.groups.add(group)
                elif role == 'Runner':
                    group, created = Group.objects.get_or_create(name='Runner')
                    user.groups.add(group)
                custom_data = {"message": "Participant created successfully", "data": response.data}  
                return Response(custom_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(e)
            error_message = str(e)
            if 'username' in error_message:
                error_message = 'A user with this username already exists.'
            return Response({"message": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
# Login
class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = super(CustomTokenCreateView, self)._action(serializer)
        username = serializer.validated_data.get('username')
        user = Participant.objects.get(username=username)
        role = user.groups.first().name if user.groups.exists() else 'Runner' 
        return Response({
            'message': 'Login successfully',
            'data': {
                'accessToken': token.data['auth_token'],
                'role': role,
                'user_id': user.id
            }
        })

# Logout
class CustomTokenDestroyView(TokenDestroyView):
    def post(self, request):
        utils.logout_user(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

# Request for resetting password when forgetting
class RequestPasswordResetView(UserViewSet):
    def reset_password(self, request, *args, **kwargs):
        super().reset_password(request, *args, **kwargs)
        return Response({'message': 'Send reset password request successful'},status=status.HTTP_200_OK)

# Confirm New Password
class ConfirmPasswordResetView(UserViewSet):
    def reset_password_confirm(self, request, *args, **kwargs):
        super().reset_password_confirm(request, *args, kwargs)
        return Response({'message': 'Confirm reset password successful'},status=status.HTTP_200_OK)

# Set New Password (Authenticated User)
class SetPassword(UserViewSet):
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        logout_session = self.request.data.get('logout_after_password_change', False)
        if logout_session:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response({'message': 'Set password successful', 'logout':logout_session},status=status.HTTP_200_OK)


class IsCoach(BasePermission):
    def has_permission(self,request, view):
        if request.user:
            return request.user.groups.filter(name="Coach")
        return False

class IsRunner(BasePermission):
    def has_permission(self,request, view):
        if request.user:
            return request.user.groups.filter(name="Runner")
        return False

class IsOwner(BasePermission):
    def has_object_permission(self,request, view, obj):
        return obj.username == request.user.username
    
class IsCoachOrAdminUser(BasePermission):
    def has_permission(self, request, view):
        return IsCoach().has_permission(request, view) or IsAdminUser().has_permission(request, view)
    
class IsCoachOrAdminUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return IsOwner().has_object_permission(request, view, obj) or IsCoach().has_permission(request, view) or IsAdminUser().has_permission(request, view)
    
class IsOwnerRaceRunner(BasePermission):
    """
    Custom permission to only allow owners of a race_runner to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow the owner of the RaceRunner object to view or edit it
        return obj.runner == request.user
    
############################################################################

############################App Logics for Coach############################

class LocationListView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer

    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def get_queryset(self):
        return Location.objects.all()
    
    def create(self, request, *args, **kwargs):
        location_serializer = LocationSerializer(data=request.data)
        if location_serializer.is_valid():
            location_serializer.save()
            return Response(location_serializer.data, status=status.HTTP_201_CREATED)
        return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsCoachOrAdminUser()]
    

class EventCoachView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_finished', 'department', 'group_runner__name', 'publish']
    ordering_fields = ['-start', 'start', 'end', '-end']

    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def get_queryset(self):
        user = self.request.user
        my_manage_events = Event.objects.filter(coach=user).order_by('-start')
        return my_manage_events
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['coach'] = self.request.user.id
        event_serializer = EventSerializer(data=data)

        if event_serializer.is_valid():
            event_serializer.save()
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)
        return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetailCoachView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    
    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def get_queryset(self):
        user = self.request.user
        my_manage_events = Event.objects.filter(coach=user).order_by('-start')
        return my_manage_events

class GroupRunnerCoachView(generics.ListCreateAPIView):
    serializer_class = GroupRunnerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.GroupRunnerFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsCoachOrAdminUser()]
    
    def get_queryset(self):
        return GroupRunner.objects.all()
    
    def create(self, request, *args, **kwargs):
        group_runner_serializer = GroupRunnerSerializer(data=request.data)
        if group_runner_serializer.is_valid():
            group_runner_serializer.save()
            return Response(group_runner_serializer.data, status=status.HTTP_201_CREATED)
        return Response(group_runner_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupRunnerDetailCoachView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupRunnerSerializer
    queryset = GroupRunner.objects.all()
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsCoachOrAdminUser()]

class ParticipantDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all()
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsOwner()]
class ParticipantListView(generics.ListAPIView):
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all()
    def get_permissions(self):
        return [IsAdminUser()]

class UpdatePublishEventView(generics.GenericAPIView):
    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def post(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        event_publish = event_publish = request.data.get('event_publish') == 'true'
        event = Event.objects.get(id=event_id)
        event.publish = event_publish
        event.save()
        publish = 'published' if event_publish else 'unpublished'
        return Response({'message': f'Event {publish} successfully'}, status=status.HTTP_200_OK)
    
class RaceTypeListView(generics.ListCreateAPIView):
    serializer_class = RaceTypeSerializer
    queryset = RaceType.objects.all()
    def get_permissions(self):
        return [IsCoachOrAdminUser()]

class RaceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RaceTypeSerializer
    queryset = RaceType.objects.all()
    def get_permissions(self):
        return [IsCoachOrAdminUser()]

class RaceCreateView(generics.CreateAPIView):
    serializer_class = RaceSerializer
    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['event_id'] = request.data.get('event_id')
        event = Event.objects.get(id=data['event_id'])
        data['name'] = request.data.get('name')
        time_limit_str = request.data.get('time_limit', '00:00:00')
        hours, minutes, seconds = map(int, time_limit_str.split(':'))
        data['time_limit'] = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if data['time_limit'] > event.end - event.start:
            return Response({'message': 'Time limit must be less than event duration'}, status=status.HTTP_400_BAD_REQUEST)
        if data['time_limit'].total_seconds() < 0:
            return Response({'message': 'Time limit must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        race_type_name = request.data.get('race_type_name', 'Memorize')
        data['race_type'] = RaceType.objects.get(name=race_type_name).id
        serializer = RaceSerializer(data=data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RaceDetailCoachView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RaceSerializer
    queryset = Race.objects.all()

    def get_permissions(self):
        return [IsCoachOrAdminUser()]

class CheckPointListView(generics.ListCreateAPIView):
    serializer_class = CheckPointSerializer
    queryset = CheckPoint.objects.all()

    def get_permissions(self):
        return [IsCoachOrAdminUser()]

class ScoreTotalView(APIView):
    def get_permissions(self):
        return [IsCoachOrAdminUser()]
    
    def get(self, request, *args, **kwargs):
        event_id = self.kwargs['pk']
        if not event_id:
            return Response({'message': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.get(id=event_id)
        response_data = []

        for runner in event.group_runner.members.all():
            race_runners = RaceRunner.objects.filter(runner=runner, race__event=event)
            total_time = sum((race_runner.total_time for race_runner in race_runners if race_runner.total_time is not None), timedelta())
            total_score = sum(race_runner.score for race_runner in race_runners if race_runner.score is not None)            

            response_data.append({
                'runner_id': runner.id,
                'runner_username': runner.username,
                'total_time': duration_string(total_time),  # Convert total time to datetime
                'total_score': total_score
            })

        return Response(response_data, status=status.HTTP_200_OK)
             



#############################################################################

############################App Logics for Runner############################
class MyEventRunnerView(generics.ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_finished', 'group_runner__name']
    ordering_fields = ['-start', 'start', 'end', '-end']
    def get_permissions(self):
        return [IsRunner()]
    
    def get_queryset(self):
        runner = self.request.user
        group_runners = GroupRunner.objects.filter(members=runner)
        my_participate_events = Event.objects.filter(group_runner__in=group_runners, publish=True).order_by('-start')
        return my_participate_events
    
class AllEventRunnerView(generics.ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_finished', 'department', 'group_runner__name']
    ordering_fields = ['-start', 'start', 'end', '-end']
    def get_permissions(self):
        return []
    
    def get_queryset(self):
        my_participate_events = Event.objects.filter(publish=True).order_by('-start')
        return my_participate_events

class EventDetailRunnerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    
    def get_permissions(self):
        return [IsRunner()]
    
    def get_queryset(self):
        my_manage_events = Event.objects.filter(publish=True).order_by('-start')
        return my_manage_events


class JoinGroupView(generics.GenericAPIView):
    serializer_class = GroupRunnerSerializer

    def get_permissions(self):
        return [IsCoachOrAdminUserOrOwner()]
    
    def post(self, request, *args, **kwargs):
        runner_id = request.data.get('runner_id')
        group_id = request.data.get('group_id')

        # Retrieve the runner and the group from the database
        runner = Participant.objects.get(id=runner_id)
        group = GroupRunner.objects.get(id=group_id)

        # Add the runner to the group
        group.members.add(runner)

        # Save the group
        group.save()

        return Response({'message': 'Runner successfully added to group'}, status=status.HTTP_200_OK)
    
class RaceDetailRunnerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RaceSerializer
    queryset = Race.objects.filter(event__publish=True)
    
    def get_permissions(self):
        return [IsRunner()]


class StartRaceView(APIView):
    def get_serializer_context(self):
        return {'request': self.request}
    
    def post(self, request, *args, **kwargs):
        race_id = request.data.get('race_id')
        if not race_id:
            return Response({'message': 'Race ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        race = Race.objects.filter(id=race_id, event__publish=True).first()
        if not race:
            return Response({'message': 'Race not found or not published'}, status=status.HTTP_404_NOT_FOUND)

        # Check if it's time to start the race
        if timezone.now() < race.event.start:
            return Response({'message': 'It is not yet time to start the race'}, status=status.HTTP_400_BAD_REQUEST)

        group_event = race.event.group_runner.members.all()
        if request.user not in group_event:
            return Response({'message': 'You have not joined this event'}, status=status.HTTP_400_BAD_REQUEST)
        race_runner = RaceRunner.objects.create(race=race, runner=request.user)
        serializer = RaceRunnerSerializer(race_runner, context=self.get_serializer_context())

        return Response({'message': 'Start run', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class RaceRunnerDetailView(generics.RetrieveAPIView):
    serializer_class = RaceRunnerSerializer
    queryset = RaceRunner.objects.all()

    def get_permissions(self):
        return [IsOwnerRaceRunner()]
    
        

class RecordCheckPointView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CheckPointRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            checkpoint_record = serializer.instance
            score = self.verify_checkpoint_record(checkpoint_record)
            checkpoint_record.race_runner.score += score
            checkpoint_record.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r

    def verify_checkpoint_record(self, checkpoint_record):
        race_runner = checkpoint_record.race_runner
        race = race_runner.race
        for checkpoint in race.checkpoints.all():
            if checkpoint_record.number == checkpoint.number:
                # Assuming checkpoint.longitude, checkpoint.latitude, checkpoint_record.longitude and checkpoint_record.latitude are float values
                distance = self.haversine(checkpoint.longitude, checkpoint.latitude, checkpoint_record.longitude, checkpoint_record.latitude)
                if distance <= 5: 
                    checkpoint_record.is_correct = True
                    checkpoint_record.save()

                    # Load the current correct_checkpoints
                    correct_checkpoints = race_runner.correct_checkpoints

                    if correct_checkpoints is None:
                        # If it's None, initialize it as an empty list
                        correct_checkpoints = []

                    # Append the new checkpoint number only if it's not already in the list
                    if checkpoint_record.number not in correct_checkpoints:
                        correct_checkpoints.append(checkpoint_record.number)

                    # Save it back to the race_runner
                    race_runner.correct_checkpoints = correct_checkpoints
                    race_runner.save()
                    return checkpoint.score  # The checkpoint_record is within the checkpoint's radius
                break
        return 0


# Logic to verify once at the end
# class EndRaceRunnerView(APIView):

#     NegativePointPerSecond = 0.1

#     def get_permissions(self):
#         return [IsOwnerRaceRunner()]
    
#     def patch(self, request, *args, **kwargs):
#         race_runner_id = request.data.get('race_runner_id')
#         try:
#             race_runner = RaceRunner.objects.get(id=race_runner_id)
#         except RaceRunner.DoesNotExist:
#             return Response({'message: Not found'}, status=status.HTTP_404_NOT_FOUND)
#         # if race_runner.is_finished:
#         #     return Response({'message': 'You have terminated your race'}, status=status.HTTP_400_BAD_REQUEST)
#         total_time = request.data.get('total_time')
#         if total_time is not None:
#             # Convert the total_time string to a timedelta object
#             hours, minutes, seconds = map(int, total_time.split(':'))
#             total_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
#             race_runner.total_time = total_time
#             race_runner.score = 0
#             for checkpoint_record in race_runner.checkpoint_records.all():
#                 score = self.verify_checkpoint_record(checkpoint_record)
#                 if checkpoint_record.is_correct:
#                     race_runner.score += score
#                     # Delete the checkpoint record
#                     checkpoint_record.delete()
            
#             negative_point = self.verify_total_time(total_time, race_runner)
#             # return Response({'score': race_runner.score, 'negative_point': negative_point}, status=status.HTTP_200_OK)
#             race_runner.score = max(0, race_runner.score - negative_point)
#             race_runner.is_finished = True

#         race_runner.save()
#         serializer = RaceRunnerSerializer(race_runner, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)       
    
#     def verify_checkpoint_record(self, checkpoint_record):
#         race_runner = checkpoint_record.race_runner
#         race = race_runner.race
#         for checkpoint in race.checkpoints.all():
#             if checkpoint_record.number == checkpoint.number:
#                 # Assuming checkpoint.location and checkpoint_record.location are Point objects
#                 distance = checkpoint.location.distance(checkpoint_record.location)
#                 if distance <= 5: 
#                     checkpoint_record.is_correct = True
#                     checkpoint_record.save()

#                     # Load the current correct_checkpoints
#                     correct_checkpoints = race_runner.correct_checkpoints

#                     if correct_checkpoints is None:
#                         # If it's None, initialize it as an empty list
#                         correct_checkpoints = []

#                     # Append the new checkpoint number
#                     correct_checkpoints.append(checkpoint_record.number)

#                     # Save it back to the race_runner
#                     race_runner.correct_checkpoints = correct_checkpoints
#                     race_runner.save()
#                     return checkpoint.score  # The checkpoint_record is within the checkpoint's radius
#                 break
#         return 0

#     def verify_total_time(self, total_time, race_runner):
#         time_limit = race_runner.race.time_limit
#         if total_time <= time_limit:
#             return 0
#         return (total_time.total_seconds() - time_limit.total_seconds()) * self.NegativePointPerSecond

class EndRaceRunnerView(APIView):
    
        NegativePointPerSecond = 0.1
    
        def get_permissions(self):
            return [IsOwnerRaceRunner()]
        
        def patch(self, request, *args, **kwargs):
            race_runner_id = request.data.get('race_runner_id')
            try:
                race_runner = RaceRunner.objects.get(id=race_runner_id)
            except RaceRunner.DoesNotExist:
                return Response({'message: Not found'}, status=status.HTTP_404_NOT_FOUND)
            if race_runner.is_finished:
                return Response({'message': 'You have terminated your race'}, status=status.HTTP_400_BAD_REQUEST)
            total_time = request.data.get('total_time')
            if total_time is not None:
                # Convert the total_time string to a timedelta object
                hours, minutes, seconds = map(int, total_time.split(':'))
                total_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                race_runner.total_time = total_time
                negative_point = self.verify_total_time(total_time, race_runner)
                # return Response({'score': race_runner.score, 'negative_point': negative_point}, status=status.HTTP_200_OK)
                race_runner.score = max(0, race_runner.score - negative_point)
                race_runner.is_finished = True

            race_runner.save()
            serializer = RaceRunnerSerializer(race_runner, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)    
           
        def verify_total_time(self, total_time, race_runner):
            time_limit = race_runner.race.time_limit
            if total_time <= time_limit:
                return 0
            return (total_time.total_seconds() - time_limit.total_seconds()) * self.NegativePointPerSecond

class MyScoreView(APIView):
    def get_permissions(self):
        return [IsRunner()]
    
    def get(self, request, *args, **kwargs):
        runner = request.user
        event_id = self.kwargs['pk']
        if not event_id:
            return Response({'message': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.get(id=event_id)
        race_runners = RaceRunner.objects.filter(runner=runner, race__event=event)
        if event.group_runner.members.filter(id=runner.id).count() == 0:
            return Response({'message': 'You have not joined this event'}, status=status.HTTP_400_BAD_REQUEST)

        total_time = sum((race_runner.total_time for race_runner in race_runners if race_runner.total_time is not None), timedelta())
        total_score = sum(race_runner.score for race_runner in race_runners if race_runner.score is not None)            

        return Response({'total_time':total_time, 'total_score': total_score}, status=status.HTTP_200_OK)
             