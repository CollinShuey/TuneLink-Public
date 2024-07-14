from django.db import models
from django.contrib.auth import get_user_model
import uuid
import datetime
# Create your models here.
User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True,max_length=100)
    profileimg = models.TextField(max_length=100)
    
    def __str__(self):
        return self.user.get_username()
    
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True,default = uuid.uuid4)
    user = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    no_of_likes = models.IntegerField(default=0)
    # not default
    caption = models.TextField(max_length=200)
    post_img = models.CharField()
    link = models.CharField()
    song = models.CharField()
    artist = models.CharField()
    snippit = models.CharField()




    def __str__(self):
        return self.user
    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username=models.CharField(max_length=100)

    def __str__(self):
        return self.username
