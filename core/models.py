from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Gamekeeper(User):
    isStaff = True

class Player(User):
    points = models.IntegerField(default=0)

class Quiz(models.Model):
    title = models.CharField(max_length=200)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    correct = models.BooleanField()

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