# Sport api for orienteering 

## All apis

### Djoser for registration, login, logout and password reset.
*** Use Token-Based Authentication, each action that required authentication have include Token in Header

1. Registration: POST request - {{baseURL}}/api/auth/users/ 
-> body: username + password + first_name + last_name + email + ....
-> response.data: email + username

2 separate mode : Coach and Runner
- Coach have to submit the valid code_secret (in Settings.py) to register -> Group: Coach
- other-> Group: Runner

2. Login: POST request - {{baseURL}}/api/auth/token/login/
-> body: username + password
-> response.data: accessToken
Save accessToken in client-side : Local Storage, Session Storage or Cookies

3. Logout: POST request - {{baseURL}}/api/auth/token/logout/
-> no body, Token included in Header 
-> response.status 200 -> delete the current token 
-> need to delete the token saved in client-side 

4. Reset Password : POST request - {{baseURL}}/api/auth/users/reset_password/
-> body: email
-> send an email with a password reset link to the specified email address 
(URL sent: PASSWORD_RESET_CONFIRM_URL - in settings.py)
-> response status 200

5. Reset Password Confirm: POST - {{baseURL}}/api/auth/users/reset_password_confirm/
-> body: new_password
-> response status 200

6. Set New Password: POST - {{baseURL}}/api/auth/users/set_password/
-> body: 
current_password + new_password + logout_after_password_change(optional)
Token included in Header
logout_after_password_change: Logout in all devices
-> response.status 200 -> change password
In settings.py
PASSWORD_CHANGED_EMAIL_CONFIRMATION
CREATE_SESSION_ON_LOGIN


### App Logics for Coach

#### Location 
- {{baseURL}}/api/locations/
    + GET-list: List all the locations in database
    + POST: Create a new location - body['name', 'longitude', 'latitude']
    start_point: POINT (-30.5 10)
- {{baseURL}}/api/locations/<int:pk>/
    + GET-retrieve: Retrieve the detail information of specific location
    + PUT or PATCH: Modify a specific location (name, 'longitude', 'latitude')
    + DELETE: Delete a specific location

#### GroupRunner
- {{baseURL}}/api/group-runners-coach/
    + GET-list: List all group_runners in database
    -> Can search by ['department', 'name']
    Ex: {{baseURL}}/api/group-runners-coach?department=MRI&name=TD2
    + POST: Create new group_runner - body['name', 'department']
- {{baseURL}}/api/group-runners-coach/<int:pk>/
    + GET-retrieve: Retrieve the detail information of specific group_runner
    + PUT or PATCH: Modify a specific group_runner (name, department)
    + DELETE: Delete a specific group_runner

#### Participant
- {{baseURL}}/api/participants/<int:pk>/
    + GET-retrieve: Retrieve the detail information of specific participant


#### Event
- {{baseURL}}/api/events-coach/
    + GET-list: List all events created by his own
    -> Can search by ['is_finished', 'department', 'group_runner__name', 'publish']
    Ex: {{baseURL}}/api/events-coach?is_finished=false&department=STI
    + POST: Create new events 
    body: name + start + end + ....
    response: data created
    publish = False by default

- {{baseURL}}/api/events-coach/<int:pk>
    + GET-retrieve: Retrieve a specific event
    + PUT or PATCH: Update a specific event
    + DELETE: Delete a specific event

- Publish or Unpublish an event - POST - {{baseURL}}/api/event-publish/
-> body: event_id + event_publish
-> response: message + status: 200

#### RaceType
- {{baseURL}}/api/race-types/
    + GET-list: List all race types
    + POST-create: Create new race type
    -> body: name + rule
- {{baseURL}}/api/race-types/<int:pk>
    + GET-retrieve: Retrieve a specific race type
    + PUT or PATCH: Update a specific race type
    + DELETE: Update a specific race types

#### Race
- Creat new Race for Event: POST - {{baseURL}}/api/create-race/
-> body: event_id + name + time_limit + race_type_name
-> response: corresponding race created

- {{baseURL}}/api/race-coach/<int:pk>/
    + GET - retrieve a specific race
    + PUT or PATCH - update a specific race - time_limit, race_type, name
    + DELETE - delete a specific race

#### CheckPoint

- Create a checkpoint - POST - {{baseURL}}/api/checkpoints/ 
-> body: number + longitude + latitude + race_id + score

#### Get all Score for Event
- GET - {{baseUYL}} - score-total/<int:pk>/
pk is event_id
-> Response List contains 'runner_id'+'runner_username'+'total_time'+'total_score' 
        "runner_id": 6,
        "runner_username": "quynh",
        "total_time": "00:30:40",
        "total_score": 41


### App Logics for Runner
#### Location
- {{baseURL}}/api/locations/<int:pk>/
    + GET: Retrieve the detail information of specific location
- {{baseURL}}/api/group-runners-coach/<int:pk>/
    + GET: Retrieve the detail information of specific group_runner

#### Participant
- {{baseURL}}/api/participants/<int:pk>/
    + PUT or PATCH: Participant can modify their own profile

#### Join Group
- POST - {{baseURL}}/api/join-group/
-> body: runner_id + group_id
-> response.message, status: 200

#### Event
- My events: GET - {{baseURL}}/api/my-event-runner/
- All published events: GET - {{baseURL}}/api/all-event-runner/
- Published events detail: GET - {{baseURL}}/api/event-detail-runner/<int:pk>/

#### Race
- Retrieve race of published event: GET - {{baseURL}}/api/race-runner/<int:pk>/

- Start a race: POST - {{baseURL}}/api/start-race/
-> Runner has joined the event can start to run and Create a RaceRunner
-> body: race_id
-> Response: corresponding RaceRunner

#### RaceRunner
- Retrieve RaceRunner status ( use to verify all the checkpoints have been recorded) - GET - {{baseURL}}/api/race-runner-status/<int:pk>/


#### CheckpointRecord
- Record a CheckPoint - POST - {{baseURL}}/api/record-checkpoint/
-> body: number + longitude + latitude + race_runner_id
-> All the logic to count score and save the correct checkpointrecord have been done

#### End RaceRunner
- PATCH - {{baseURL}}/api/end-race-runner
-> body: race_runner_id + total_time (record by the clock in FrontEnd)
race_runner_id : when start a race (above) all info about the RaceRunner created will be returned in the response so can save the race_runner_id as a variable to use during the RaceRunner taking place

-> response: data updated

#### MyScore 
- GET - {{baseURL}}/api/my-score/<int:pk>/ (pk is event_id)
-> Response
{
    "total_time": "1840.0",
    "total_score": 41
}

