
from django.contrib import admin
from django.urls import path,include
from blog_app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),

    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('',home),
    path('home/',home,name="home"),
    path('contact/',contact,name='contact'),
    path('about/',about,name='about'),
    path('category/<int:category_id>/',specific_category,name='specific_category'),
    path('all_blog/',all_blog,name='all_blog'),
    path('all_category/',all_category,name='all_category'),
    path('featured_post/',featured_post,name='featured_post'),
    path('latest_post/',latest_post,name='latest_post'),
    # path('feedback/',feedback,name='feedback'),
    path('blog_app/search/',search,name='search'),
    path('blog_app<slug:slug>/',blogs,name='blogs'),
    path('register/',register,name="register"),
    path('login/',login,name='login'),
    path('logout/',logout,name='logout'),
    path('dashboard/',include('dashboard.urls')),
    path('feedback/',all_feedback, name='all_feedback'),

    # subscribe
    path("subscribe/",subscribe, name="subscribe"),
    path('policy/',policy,name='policy'),


    # Forgot Password
    path("password-reset/",
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html",
             email_template_name="password_reset_email.html",
             success_url=reverse_lazy("password_reset_done"),
         ),
         name="password_reset"),

    path("password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_done.html"),
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset_confirm.html",
             success_url=reverse_lazy("password_reset_complete")),
         name="password_reset_confirm"),

    path("reset/done/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password_reset_complete.html"),
         name="password_reset_complete"),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
