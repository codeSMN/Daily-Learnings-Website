from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=288, blank=True)
    school = models.CharField(max_length=255, blank=True)
    fav_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)


class Friends(models.Model):
    user_a = models.ForeignKey(User, related_name='friend_a', on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name='friend_b', on_delete=models.CASCADE)


class Message(models.Model):
    channel = models.ForeignKey(User, related_name='channel', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(choices=[('FRIEND-REQUEST', 'FRIEND-REQUEST'), ('MESSAGE', 'MESSAGE')], max_length=14)
    message = models.TextField()
    send_date = models.DateTimeField(auto_now_add=True)
    read_msg = models.BooleanField()


class Deck(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    user = models.ManyToManyField(User, related_name='user', blank=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    question = models.TextField()
    solution = models.TextField()

    def __str__(self):
        return self.question


class Queue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    time = models.CharField(max_length=6)
    next_time = models.DateTimeField(auto_now_add=True)
    learn_status = models.CharField(max_length=5)
