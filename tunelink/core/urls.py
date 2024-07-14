from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('signin',views.signin,name='signin'),
    path('settings',views.settings,name='settings'),
    path('profile/<str:pk>',views.profile,name='profile'),
    path('follow',views.follow,name='follow'),
    path('upload',views.upload,name="upload"),
    path('like-post',views.like_post,name='like-post'),
    path('first-follow',views.first_follow,name='first-follow'),
    path('search',views.search,name='search'),
    path('update_settings',views.update_settings,name="update_settings")

]