from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['topic','name','description']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','email','username','name','bio']