from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('api-token-auth', obtain_auth_token),
    path('auth/users/', 
         views.CustomParticipantCreateView.as_view({'get':'list', 'post': 'create'}), 
         name='participant-create'
         ),
    path('auth/token/login/', views.CustomTokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', views.CustomTokenDestroyView.as_view(), name='logout'),
    path('auth/users/reset_password/', views.RequestPasswordResetView.as_view({'post': 'reset_password'}), name='reset-password'),
    path('auth/users/reset_password_confirm/', views.ConfirmPasswordResetView.as_view({'post': 'reset_password-confirm'}), name='reset-password-confirm'),
    path('auth/users/set_password/', views.SetPassword.as_view({'post': 'set_password'}), name='set-password'),

    path('locations/', views.LocationListView.as_view(), name='locations'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location-detail'),
    path('group-runners-coach/', views.GroupRunnerCoachView.as_view(), name='group-runners'),
    path('group-runners-coach/<int:pk>/', views.GroupRunnerDetailCoachView.as_view(), name='group-runners-detail'),
    path('participants/<int:pk>/', views.ParticipantDetailView.as_view(), name='participant-detail'),
    path('participants/', views.ParticipantListView.as_view(), name='participants'),
    path('join-group/', views.JoinGroupView.as_view(), name='join-group'),
    path('events-coach/', views.EventCoachView.as_view(), name='events-coach'),
    path('events-coach/<int:pk>/', views.EventDetailCoachView.as_view(), name='events-coach-detail'),

    path('event-publish/', views.UpdatePublishEventView.as_view(), name='event-publish'),
    path('my-event-runner/', views.MyEventRunnerView.as_view(), name='my-event-runner'),
    path('all-event-runner/', views.AllEventRunnerView.as_view(), name='all-event-runner'),
    path('event-detail-runner/<int:pk>/', views.EventDetailRunnerView.as_view(), name='event-detail-runner'),
    path('race-types/', views.RaceTypeListView.as_view(), name='race-types'),
    path('race-types/<int:pk>/', views.RaceTypeDetailView.as_view(), name='race-types-detail'),
    path('create-race/', views.RaceCreateView.as_view(), name='create-race'),
    path('race-coach/<int:pk>/', views.RaceDetailCoachView.as_view(), name='race-detail-coach'),
    path('race-runner/<int:pk>/', views.RaceDetailRunnerView.as_view(), name='race-detail-runner'),
    path('start-race/', views.StartRaceView.as_view(), name='start-race'),
    path('race-runner-status/<int:pk>/', views.RaceRunnerDetailView.as_view(), name='race_runner_status'),
    path('record-checkpoint/', views.RecordCheckPointView.as_view(), name='record_checkpoint'),
    path('checkpoints/', views.CheckPointListView.as_view(), name='checkpoints'),
    path('end-race-runner/', views.EndRaceRunnerView.as_view(), name='end-race-runner'),
    path('score-total/<int:pk>/', views.ScoreTotalView.as_view(), name='score-total'),
    path('my-score/<int:pk>/', views.MyScoreView.as_view(), name='my-score'),
]