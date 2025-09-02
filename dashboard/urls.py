from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    # path for dashboard
    path('',dashboard,name='dashboard'),
    
    # path for category
    path('dashboard/add_catagories/', add_catagories, name='add_catagories'),
    path('all_categories/',all_categories,name='all_categories'),
    path('dashboard/edit_catagories/<int:id>', edit_catagories, name='edit_catagories'),
    path('dashboard/delete_catagories/<int:id>', delete_catagories, name='delete_catagories'),

    # path for profile
    path('dashboard/profile/',dashboard, name='profile'),
    path('dashboard/edit_profile/<int:id>/',edit_profile, name='edit_profile'),
    path('dashboard/update_profile/<int:id>/',update_profile, name='update'),  # For form submission
    path('update_photo/<int:pk>/',update_photo, name='update_photo'),



    # path for posts/blogs
    path('add_blog/',add_blog,name='add_blog'),
    path("my_posts/",my_posts, name="my_posts"),
    path('my_post_all/',my_post_all,name='my_post_all'),
    path('dashboard/update_blog/<int:id>/', update_blog, name='update_blog'),
    path('dashboard/delete_blog/<int:id>/',delete_blog,name='delete_blog'),


    # path for users 
    path('users/',users,name='users'),
    path('all_users/',all_users,name='all_users'),
    path('add_users/',add_users,name='add_users'),
    path('dashboard/edit_users/<int:id>/',edit_users, name='edit_users'),
    path('dashboard/delete_users/<int:id>/',delete_users,name='delete_users'),


    # path for comments
    path('comments/',comments,name='comments'),
    path('all_comments/',all_comments,name='all_comments'),
    path("delete-comment/<int:id>/",delete_comment, name="delete_comment"),


    # like
    path('blog/<int:pk>/like/',like_blog, name='like_blog'),
    path('blog/<int:pk>/dislike/',dislike_blog, name='dislike_blog'),
    path('likes/',likes, name='likes'),
    path('all_likes/',all_likes, name='all_likes'),


    # feedbacks
    path('feedbacks/',feedbacks, name='feedbacks'),
    path('all_feedbacks/',all_feedbacks, name='all_feedbacks'),
    path('dashboard/delete_feedback/<int:id>/',delete_feedback,name='delete_feedback'),

   
    # update password
    path("changepassword",changepassword, name="changepassword"),
]