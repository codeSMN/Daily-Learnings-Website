from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Deck, Subject, Card, Queue, Profile, Friends, Message


class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'school', 'fav_subject')


class DeckAdmin(ModelAdmin):
    list_display = ('name', 'creator', 'subject', 'created', 'public')


class CardAdmin(ModelAdmin):
    list_display = ('deck', 'question', 'solution')


class QueueAdmin(ModelAdmin):
    list_display = ('deck', 'user', 'card', 'time', 'learn_status')


class FriendsAdmin(ModelAdmin):
    list_display = ('user_a', 'user_b')


class MessageAdmin(ModelAdmin):
    list_display = ('channel', 'recipient', 'type', 'title', 'message')


admin.site.register(Deck, DeckAdmin)
admin.site.register(Subject)
admin.site.register(Card, CardAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Friends, FriendsAdmin)
admin.site.register(Message, MessageAdmin)
