from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room,Topic, Message
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm,UserForm
from django.db.models import Q



def login_user(request):

    page = 'login'

    # If someone tries to go to login page even after logging in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User Not found !")
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exists !")

    context = {'page':page}
    return render(request, 'base/login_register.html', context)



def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration!!')

    return render(request, 'base/login_register.html',{'form':form})


def home(request):
    # if the .get() is not None then the value of ?q= is taken 
    # or else it is set to an empty string
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # This will return all the topics that atleast contain anything in q
    # if its an empty string then it will return all the values
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(host__username__icontains = q) |
        Q(description__icontains = q)
        )
    
    room_count = Room.objects.all().count()
    topics = Topic.objects.all()[:5]
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains = q) |
        Q(room__name__icontains = q)
        )
   
    return render(request, "base/home.html", {
        'rooms':rooms, 
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages})



def room(request,pk):
    room = Room.objects.get(id=pk)

    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk = room.id)
    return render(request, 'base/room.html', {
        'room':room,
        'room_messages':room_messages,
        'participants':participants})



def userProfile(reqeust,pk):
    user = User.objects.get(id=pk)
    # to get the rooms associated to the particular user
    rooms = user.room_set.all()
    room_count = rooms.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics,'room_count':room_count}
    return render(reqeust,'base/profile.html',context)


# To restrict this page for the users who are not logged in we can just put a decorator 
@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic =topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    return render(request, 'base/room_form.html',{'form':form,'topics':topics})



@login_required(login_url='/login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('<h2>You are not allowed here !!</h2>')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    return render(request, 'base/room_form.html', {'form':form,'topics':topics,'room':room})



@login_required(login_url='/login')
def delete_room(request,pk):
    room = Room.objects.get(id = pk)

    # This is to make sure that only the authenticated user gets to delete their own room ... not of others nither get their own room deleted by someon else
    if request.user != room.host:
        return HttpResponse('<h2>You are not allowed here !!</h2>')
    
    if request.method =='POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})



@login_required(login_url='/login')
def delete_message(request,pk):
    message = Message.objects.get(id = pk)

    # This is to make sure that only the authenticated user gets to delete their own room ... not of others nither get their own room deleted by someon else
    if request.user != message.user:
        return HttpResponse('<h2>You are not allowed here !!</h2>')
    
    if request.method =='POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':message})




@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk = user.id)
    return render(request,'base/update-user.html',{'form':form})



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    room_count = Room.objects.all().count()
    return render(request,'base/topics.html',{'topics':topics,'room_count':room_count})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})