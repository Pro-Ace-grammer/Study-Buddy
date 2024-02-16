from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    name = models.CharField(max_length=200,null=True)
    email = models.EmailField(max_length=254,unique=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True,default='avatar.svg')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []





class Topic(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name



# This rooom will be a child of a topic
#below is the room table... which will contain the information about the room that are being created by the user
class Room(models.Model):
    host = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)  #One to many ... a topic can have multiple rooms... and if we set it to null we have to allow it to be null in the database as well so we say null=True
    name = models.CharField(max_length=150)
    description = models.TextField(null = True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants',blank=True)
    updated = models.DateTimeField( auto_now=True) # takes timestamp at every update
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):
        return self.description[:40]



#below table consist of the messages sent in each room
class Message(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # One to Many relationship
    body = models.TextField() #This will contain the message of the user
    updated = models.DateTimeField( auto_now=True) # takes timestamp at every update
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):
        return self.body[:20]