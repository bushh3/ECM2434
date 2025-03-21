from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Player(models.Model):
    user = models.OneToOneField('core.CustomUser', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
    
@receiver(post_save, sender=CustomUser)
def create_player_for_new_user(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'player'):
        Player.objects.create(user=instance)
        
class Profile(models.Model):
    user = models.OneToOneField('core.CustomUser', on_delete=models.CASCADE, related_name="profile")
    avatar_url = models.CharField(max_length=255, blank=True, null=True, default="avatars/fox.jpg")

    def __str__(self):
        return f"Profile of {self.user.email}"
        
class Quiz(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    option1 = models.CharField(max_length=100, default="Default Option 1")
    option2 = models.CharField(max_length=100, default="Default Option 2")
    option3 = models.CharField(max_length=100, default="Default Option 3")
    option4 = models.CharField(max_length=100, default="Default Option 4")
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A')

    def __str__(self):
        return self.question_text

class PlayerQuiz(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    timestamp = models.DateTimeField()

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

class WalkingData(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    distance = models.FloatField()

class DIYCreation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    photo_location = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    approved = models.BooleanField()

class Like(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    creation = models.ForeignKey(DIYCreation, on_delete=models.CASCADE)

class WalkingChallenge(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    distance = models.FloatField()
    duration = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)
    track_points = models.TextField(default="")  

    def set_track_points(self, points_list):
        formatted_points = ";".join([f"{point['lat']},{point['lon']}" for point in points_list])
        self.track_points = formatted_points

    def get_track_points(self):
        if not self.track_points:
            return []
        return [{"lat": float(lat), "lon": float(lon)} for lat, lon in (point.split(",") for point in self.track_points.split(";"))]

    def __str__(self):
        return f"Challenge {self.session_id} for {self.player.user.email}"

@receiver(post_save, sender=CustomUser)
def create_related_objects(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        Player.objects.get_or_create(user=instance)