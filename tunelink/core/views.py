from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Profile, FollowersCount, Post, LikePost
from .api import song_search, get_token
from itertools import chain
from datetime import datetime,timedelta
import requests
import base64
import json
import time
from pprint import pprint
import os

import random
token,token_expiration = get_token()

# Create your views here.
@login_required(login_url='signin')
def index(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    user_following_list = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    
    for user in user_following:
        user_following_list.append(user.user)
    
    start_date = timezone.now() - timedelta(days=5)
    end_date = timezone.now()
    
    posts_user_following_list = [x for x in user_following_list]
    posts_user_following_list.append(request.user.username)

    queryset = Post.objects.none()
    for username in posts_user_following_list:
        feed_lists = Post.objects.filter(user=username,created_at__range=(start_date,end_date))
        queryset = queryset | feed_lists
    feed_list = list(queryset.order_by('-created_at'))
    
    

    feed_list_objects = []
    for post in feed_list:
        is_liked = LikePost.objects.filter(post_id=post.id,username=request.user.username).exists() 
        feed_list_objects.append({
            'post':post,
            'is_liked':is_liked,
        })


    # user suggestiions

    all_users = User.objects.all()

    suggestions = [x for x in list(all_users) if x != user_object]
    random.shuffle(suggestions)


    username_profile = []
    final_suggestion_profiles = []
    for user in suggestions[:5]:
        username_profile.append(user.id)
    for id in username_profile:
        curr_profile = Profile.objects.filter(id_user = id)
        final_suggestion_profiles.append(curr_profile)
        

    final_suggestion_profile_list = list(chain(*final_suggestion_profiles))
    
    
    posts = Post.objects.all()

    
    return render(request,'index.html',{'user_profile':user_profile,'posts':feed_list_objects,'suggested_users':final_suggestion_profile_list,'user_following_list':user_following_list,})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()

                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)

                random_pic_id = random.randint(1,1084)
                profile_image_url = f"https://picsum.photos/id/{random_pic_id}/200/300"

                new_profile = Profile.objects.create(user=user,id_user = user.id,profileimg = profile_image_url)
                new_profile.save()
                return redirect("index")

        else:
            messages.info(request,'Password Not Matching')
            return redirect('signup')


    return render(request,'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request,'signin.html')



@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signup')
def settings(request):
    user_profile = Profile.objects.get(user = request.user)
    if request.method == 'POST':
        
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            user_profile.profileimg = image
        
        bio = request.POST['bio']
        
        user_profile.bio = bio
        user_profile.save()
        return redirect('settings')


    return render(request,'settings.html',{'user_profile':user_profile})

@login_required(login_url='signup')
def profile(request,pk):
    
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(follower=follower,user=user):
        button_text = 'Unfollow'
    else:
        button_text = "Follow"

    user_posts = Post.objects.filter(user=pk).order_by('-created_at')[:5]
    context = {
        'user_object':user_object,
        'user_profile':user_profile,
        'button_text':button_text,
        'user_posts':user_posts
    }
    return render(request,'profile.html',context)

@login_required(login_url='signup')
def update_settings(request):
    if request.method== "POST":
        random_id = random.randint(1,1084)
        new_profile_image_url = f"https://picsum.photos/id/{random_id}/200/300"
        user_profile = Profile.objects.get(user=request.user)
        user_profile.profileimg = new_profile_image_url
        user_profile.save()
        return redirect('settings')  
    return redirect('settings')


@login_required(login_url='signup')
def follow(request):
    if request.method == 'POST':
        follower = User.objects.get(username = request.user)
        user = request.POST['user']
        if FollowersCount.objects.filter(follower=follower.username,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower.username,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower.username,user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='sign_up')
def first_follow(request):
    follower = User.objects.get(username = request.user)
    user = request.POST.get('suggested_user')

    if FollowersCount.objects.filter(follower=follower.username,user=user).first():
        delete_follower = FollowersCount.objects.get(follower=follower.username,user=user)
        delete_follower.delete()
        follow_text = "Follow"
    else:
        new_follower = FollowersCount.objects.create(follower=follower.username,user=user)
        new_follower.save()
        follow_text = "Unfollow"
    response = {
        "follow_text":follow_text,
    }
    return JsonResponse(response)    


@login_required(login_url='signup')
def upload(request):
    if request.method == "POST":
        user = request.user.username
        song = request.POST['song']
        artist = request.POST['artist']
        caption = request.POST['caption']
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now()
        if Post.objects.filter(user=request.user.username,created_at__range=(start_date,end_date)).exists():
            messages.info(request,"You already posted today!")
            return redirect('/')
        
        global token, token_expiration
        
        
        

        
        
        
        
        print(token)
        print(token_expiration)
        
        
        for attempt in range(6):  # Retry up to 3 times
            api_call = song_search(artist_name=artist, track=song, token=token)
            if 'error' in api_call and api_call['error']['status'] == 429:
                
                
                token, token_expiration = get_token()
                
                time.sleep(1)  # Wait before retrying
                continue
            break
        
        if ((len(api_call) == 0) or (not api_call['tracks']['items'])):
            messages.info(request,"Song or Artist Doesn't exist")
            return redirect('/')
        else:
            post_img = api_call['tracks']['items'][0]['album']['images'][2]['url']
            if api_call['tracks']['items'][0]['preview_url'] == None:
                snippit = "None"
            else:
                snippit = api_call['tracks']['items'][0]['preview_url']
            link = api_call['tracks']['items'][0]['external_urls']['spotify']
            song = api_call['tracks']['items'][0]['name']
            artist = api_call['tracks']['items'][0]['album']['artists'][0]['name'].title()
            new_post = Post.objects.create(user=user,song=song,artist=artist,caption=caption,snippit=snippit,post_img=post_img,link=link)
            new_post.save()
            x = True
            if x:
                
                token, token_expiration = get_token()
            return redirect('/')
    else:
        return redirect('/')
    
@login_required(login_url='signup')
def like_post(request):
    username= request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        user_liked = True
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        user_liked=False
    
    response = {
        'new_likes':post.no_of_likes,
        'user_liked':user_liked
    }
    return JsonResponse(response)
    

@login_required(login_url='signup')
def search(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        usersearched_object = User.objects.filter(username__icontains=username)
        usersearched_profiles = []

        for user in usersearched_object:
            if user != request.user:
                profile = Profile.objects.get(id_user = user.id)
                follower_count = FollowersCount.objects.filter(user=profile.user.username).count()
                if FollowersCount.objects.filter(user=profile.user.username,follower=request.user.username).exists():
                    button_text = "UnFollow"
                else:
                    button_text = "Follow"
                usersearched_profiles.append({
                    'profile':profile,
                    'follower_count':follower_count,
                    'button_text':button_text,
                })
        
    return render(request,'search.html',{'usersearched_profiles':usersearched_profiles,})