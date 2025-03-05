from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# custom user model
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# player model
class Player(models.Model):
    user = models.OneToOneField('core.CustomUser', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"Player: {self.user.email}"

# quiz models
class Quiz(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    option1 = models.CharField(max_length=100, default="Option 1")
    option2 = models.CharField(max_length=100, default="Option 2")
    option3 = models.CharField(max_length=100, default="Option 3")
    option4 = models.CharField(max_length=100, default="Option 4")
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A')

    def __str__(self):
        return self.question_text

class PlayerQuiz(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    timestamp = models.DateTimeField()

# task and badge models
class Task(models.Model):
    name = models.CharField(max_length=100)
    criteria = models.CharField(max_length=500)

class PlayerTask(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    times_completed = models.IntegerField(default=0)
    last_completed = models.DateTimeField()

class Badge(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    criteria = models.CharField(max_length=500)

class PlayerBadge(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

# walking challenge models
class WalkingTrip(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    distance = models.FloatField()  # km
    duration = models.IntegerField()  # seconds
    is_completed = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)
    track_points_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Walking Trip {self.session_id} by {self.player.user.email}"

class WalkingTrackPoint(models.Model):
    trip = models.ForeignKey(WalkingTrip, related_name="track_points", on_delete=models.CASCADE)
    lat = models.FloatField()
    lng = models.FloatField()
    timestamp = models.DateTimeField()
    speed = models.FloatField(null=True, blank=True)  # km/h

    def __str__(self):
        return f"Point {self.id} for Trip {self.trip.session_id}"

# DIY and like models
class DIYCreation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    photo_location = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    approved = models.BooleanField()

class Like(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    creation = models.ForeignKey(DIYCreation, on_delete=models.CASCADE)
