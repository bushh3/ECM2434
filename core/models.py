from django.db import models

from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # username = models.CharField(max_length=50, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Player(models.Model):
    user = models.OneToOneField('core.CustomUser', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

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

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # 自动生成 Profile

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()