from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Deck, Card, Profile, Message


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions', 'password']


class CreateDeckForm(ModelForm):
    class Meta:
        model = Deck
        fields = '__all__'
        exclude = ['creator']


class CardForm(ModelForm):
    class Meta:
        model = Card
        fields = '__all__'


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['channel', 'send_date', 'read_msg']
