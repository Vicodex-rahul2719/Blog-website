from django.shortcuts import render,HttpResponse,redirect
from blog_app.models import Blogs,Category,Profile,Comment,Feedback
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . forms import CategoryForm,BlogsForm
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from .forms import AddUserForm,EditUserForm
# from django.http import JsonResponse
from blog_app.models import LikeDislike
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# Create your views here.

# views.py
@login_required(login_url='/login/')
def dashboard(request):
    # Get or create a profile for the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Count the user's blogs
    my_posts_count = Blogs.objects.filter(author=request.user).count() if request.user.is_authenticated else 0
    
    # If the profile was just created, you can set defaults if needed
    if created:
        profile.profile_image = None  # or set a default image
        profile.save()

    # Render the dashboard template
    return render(request, 'dashboard.html', {'profile': profile, 'my_posts_count': my_posts_count})



@login_required(login_url="/login/")  
def edit_profile(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, 'edit_profile.html', {'profile': profile})
  
@login_required(login_url="/login/")   
def update_profile(request, id):
    profile = get_object_or_404(Profile, id=id)

    if request.method == 'POST':
        # Update User fields
        profile.user.first_name = request.POST.get('fullname')
        profile.user.email = request.POST.get('email')  # optional if using profile.email
        profile.user.save()

        # Update Profile fields
        profile.website = request.POST.get('website')
        profile.designation = request.POST.get('designation')
        profile.location = request.POST.get('location')
        profile.email = request.POST.get('email') 
        profile.phone = request.POST.get('phone') # optional if you want separate Profile email
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return redirect('edit_profile', id=profile.id)

# update profile photo
@login_required(login_url="/login/") 
def update_photo(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile.profile_image = request.FILES['profile_image']
        profile.save()
        messages.success(request, "Profile image updated successfully!")
        return redirect('profile')  # replace 'profile' with your profile view name
    
    messages.error(request, "Failed to update profile image.")
    return redirect('profile')



#  add blog
@login_required(login_url='/login/')
def add_blog(request):
    if request.method == "POST":
        form = BlogsForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user  
            blog.slug = slugify(form.cleaned_data["title"])  # ✅ fixed typo
            blog.save()
            messages.success(request, "Blog added successfully")
            return redirect("my_posts")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = BlogsForm()

    return render(request, "add_blog.html", {"form": form})


# edit blog
@login_required(login_url='/login/')
def update_blog(request, id):
    blog = get_object_or_404(Blogs, id=id)

    # Check if the logged-in user is the author
    if blog.author != request.user:
        messages.error(request, "You are not allowed to update this blog!")
        return redirect('my_posts')  # or any page you want to redirect

    if request.method == "POST":
        form = BlogsForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully")
            return redirect('my_posts')
    else:
        form = BlogsForm(instance=blog)

    return render(request, "update_blog.html", {"form": form, "blog": blog})


@login_required(login_url='/login/')
def delete_blog(request,id): 
    blog = get_object_or_404(Blogs,id=id)
    blog.delete()
    messages.success(request,'Blog deleted successfully')
    return redirect('my_posts')



# def my_posts(request):
#     blog_count=Blogs.objects.all().count()
#     draft_count = Blogs.objects.filter(status='draft').count()
#     my_posts_count = Blogs.objects.filter(author=request.user).count() if request.user.is_authenticated else 0
#     return render(request,'my_posts.html',{'blog_count':blog_count,'my_posts_count': my_posts_count,'draft_count':draft_count})



# add categories on dashboard updated code with redundency remove
@login_required(login_url='/login/')
def add_catagories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            
            # check duplicates properly
            if Category.objects.filter(category_name__iexact=category_name).exists():
                messages.error(request, 'This Category already exists.')
            else:
                form.save()
                messages.success(request, 'Category added successfully!')
                return redirect('add_catagories')
    else:
        form = CategoryForm()

    # categories list
    categories = Category.objects.annotate(blog_count=Count('blogs'))[:12]
    categories_count=Category.objects.all().count()

    context = {
        'categories': categories,
        'form': form,
        'categories_count':categories_count,
    }
    return render(request, 'add_catagories.html', context)



# showing all categories on dashboard
@login_required(login_url='/login/')
def all_categories(request):
    categories = Category.objects.annotate(blog_count=Count('blogs'))
    categories_count=Category.objects.all().count()
    context={
        'categories':categories,
        'categories_count':categories_count
    }
    return render(request,'all_categories.html',context)


# edit category on dashboard
@login_required(login_url='/login/')
def edit_catagories(request, id):
    category = get_object_or_404(Category, id=id)  # ✅ always define
    
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect("add_catagories")
    else:
        form = CategoryForm(instance=category)

    return render(request, "edit_catagories.html", {"form": form, "category": category})

# delete category
@login_required(login_url='/login/')
def delete_catagories(request,id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request,'Category deleted successfully')
    return redirect('add_catagories')






# my posts / blogs methods
@login_required(login_url='/login/')
def my_posts(request):
    # Get only posts created by the logged-in user, with comment count
    posts = Blogs.objects.filter(author=request.user) \
        .annotate(comment_count=Count('comment')) \
        .order_by('-id')[:3]  # latest posts first

    context = {
        'posts': posts,
    }
    return render(request, 'my_posts.html', context)


@login_required(login_url='/login/')
def my_post_all(request):
    # Get only posts created by the logged-in user
    posts = Blogs.objects.filter(author=request.user)\
        .annotate(comment_count=Count('comment')) \
        .order_by('-id')[:3]  # latest posts first
    my_posts_count = posts.count()  # count of the user's posts

    context = {
        'posts': posts,
        'my_posts_count': my_posts_count,
    }
    return render(request, 'my_post_all.html', context)




# users
@login_required(login_url='/login/')
def users(request):
    users=User.objects.all()[:12]
    context={
        'users':users
    }
    return render(request,'users.html',context)


# all users
@login_required(login_url='/login/')
def all_users(request):
    users=User.objects.all()
    total_users = users.count()
    context={
        'users':users,
        'total_users':total_users
    }
    return render(request,'all_users.html',context)


# add users
@login_required(login_url='/login/')
def add_users(request):
    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ New user added successfully!')
            return redirect("users")  # redirect to users list
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = AddUserForm()
    
    context = {
        'form': form
    }
    return render(request, 'add_users.html', context)

# edit users
@login_required(login_url='/login/')
def edit_users(request,id):
    users = get_object_or_404(User,id=id)  # ✅ always define
    
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=users)
        if form.is_valid():
            form.save()
            messages.success(request, 'User informations updated successfully')
            return redirect("users")
    else:
        form = EditUserForm(instance=users)

    return render(request, "edit_users.html", {"form": form, "users": users})

# delete users
@login_required(login_url='/login/')
def delete_users(request,id):
    users = get_object_or_404(User, id=id)
    users.delete()
    messages.success(request,'User deleted successfully')
    return redirect('users')





# comments
def comments(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # Admin or superuser sees all comments
            admin_comments = Comment.objects.filter(user__is_staff=True).select_related('blog').order_by('-created_at')[:3]
            user_comments = Comment.objects.filter(user__is_staff=False).select_related('blog').order_by('-created_at')[:3]
            comment_count = admin_comments.count() + user_comments.count()
            context = {
                'admin_comments': admin_comments,
                'user_comments': user_comments,
                'comment_count': comment_count
            }
        else:
            # Normal user → assign to 'comments' (not 'user_comments')
            comments = Comment.objects.filter(user=request.user).select_related('blog').order_by('-created_at')[:6]
            comment_count = comments.count()
            context = {
                'comments': comments,
                'comment_count': comment_count
            }
    else:
        context = {
            'admin_comments': Comment.objects.none(),
            'user_comments': Comment.objects.none(),
            'comment_count': 0
        }

    return render(request, 'comments.html', context)





def all_comments(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # Separate admin and user comments
            admin_comments = Comment.objects.filter(user__is_staff=True).select_related('blog').order_by('-created_at')
            user_comments = Comment.objects.filter(user__is_staff=False).select_related('blog').order_by('-created_at')
            comment_count = admin_comments.count() + user_comments.count()
        else:
            # Normal user → only their own comments
            admin_comments = Comment.objects.none()
            user_comments = Comment.objects.filter(user=request.user).select_related('blog').order_by('-created_at')
            comment_count = user_comments.count()
    else:
        admin_comments = Comment.objects.none()
        user_comments = Comment.objects.none()
        comment_count = 0

    return render(request, 'all_comments.html', {
        'admin_comments': admin_comments,
        'user_comments': user_comments,
        'comment_count': comment_count
    })


#  delete comments
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if request.user == comment.user or request.user.is_staff or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You are not allowed to delete this comment.")
    return redirect("comments")



# like
# @login_required
# def like_blog(request, pk):
#     blog = get_object_or_404(Blogs, pk=pk)
#     user = request.user

#     if blog.disliked_users.filter(pk=user.pk).exists():
#         blog.disliked_users.remove(user)

#     if blog.liked_users.filter(pk=user.pk).exists():
#         blog.liked_users.remove(user)
#     else:
#         blog.liked_users.add(user)

#     return redirect(request.META.get('HTTP_REFERER', '/home/')) # 👈 Replace with your blog detail URL name
@login_required
def like_blog(request, pk):
    blog = get_object_or_404(Blogs, pk=pk)
    user = request.user

    # Remove dislike if exists
    blog.disliked_users.remove(user)
    LikeDislike.objects.filter(blog=blog, user=user, is_like=False).delete()

    # Toggle like
    if blog.liked_users.filter(pk=user.pk).exists():
        blog.liked_users.remove(user)
        LikeDislike.objects.filter(blog=blog, user=user, is_like=True).delete()
    else:
        blog.liked_users.add(user)
        LikeDislike.objects.update_or_create(
            blog=blog,
            user=user,
            defaults={'is_like': True}
        )

    return redirect(request.META.get('HTTP_REFERER', '/home/'))




# @login_required
# def dislike_blog(request, pk):
#     blog = get_object_or_404(Blogs, pk=pk)
#     user = request.user

#     if blog.liked_users.filter(pk=user.pk).exists():
#         blog.liked_users.remove(user)

#     if blog.disliked_users.filter(pk=user.pk).exists():
#         blog.disliked_users.remove(user)
#     else:
#         blog.disliked_users.add(user)

#     return redirect(request.META.get('HTTP_REFERER', '/home/'))

@login_required
def dislike_blog(request, pk):
    blog = get_object_or_404(Blogs, pk=pk)
    user = request.user

    # Remove like if exists
    blog.liked_users.remove(user)
    LikeDislike.objects.filter(blog=blog, user=user, is_like=True).delete()

    # Toggle dislike
    if blog.disliked_users.filter(pk=user.pk).exists():
        blog.disliked_users.remove(user)
        LikeDislike.objects.filter(blog=blog, user=user, is_like=False).delete()
    else:
        blog.disliked_users.add(user)
        LikeDislike.objects.update_or_create(
            blog=blog,
            user=user,
            defaults={'is_like': False}
        )

    return redirect(request.META.get('HTTP_REFERER', '/home/'))



# likes for users and admins
@login_required
def likes(request):
    if request.user.is_staff or request.user.is_superuser:
        admin_likes = LikeDislike.objects.filter(user__is_staff=True, is_like=True)
        admin_dislikes = LikeDislike.objects.filter(user__is_staff=True, is_like=False)
        user_likes = LikeDislike.objects.filter(user__is_staff=False, is_like=True)
        user_dislikes = LikeDislike.objects.filter(user__is_staff=False, is_like=False)
    else:
        admin_likes = admin_dislikes = user_likes = user_dislikes = None
        my_likes = LikeDislike.objects.filter(user=request.user)

    context = {
        'admin_likes': admin_likes,
        'admin_dislikes': admin_dislikes,
        'user_likes': user_likes,
        'user_dislikes': user_dislikes,
        'my_likes': my_likes if not request.user.is_staff else None,
    }
    return render(request, 'likes.html', context)


@login_required
def all_likes(request):
    if request.user.is_staff or request.user.is_superuser:
        admin_likes = LikeDislike.objects.filter(user__is_staff=True, is_like=True)
        admin_dislikes = LikeDislike.objects.filter(user__is_staff=True, is_like=False)
        user_likes = LikeDislike.objects.filter(user__is_staff=False, is_like=True)
        user_dislikes = LikeDislike.objects.filter(user__is_staff=False, is_like=False)

        # Counts
        admin_likes_count = admin_likes.count()
        admin_dislikes_count = admin_dislikes.count()
        user_likes_count = user_likes.count()
        user_dislikes_count = user_dislikes.count()

        # Total counts (global)
        total_likes_count = LikeDislike.objects.filter(is_like=True).count()
        total_dislikes_count = LikeDislike.objects.filter(is_like=False).count()

        my_likes = None  # Admins don't need personal likes shown

        # For admins, user totals not needed
        my_total_likes_count = None
        my_total_dislikes_count = None

    else:
        admin_likes = admin_dislikes = user_likes = user_dislikes = None
        admin_likes_count = admin_dislikes_count = user_likes_count = user_dislikes_count = None

        my_likes = LikeDislike.objects.filter(user=request.user)

        # Total counts for normal user = counts for *their* likes/dislikes only
        my_total_likes_count = LikeDislike.objects.filter(user=request.user, is_like=True).count()
        my_total_dislikes_count = LikeDislike.objects.filter(user=request.user, is_like=False).count()

        # For normal user, no global totals shown
        total_likes_count = None
        total_dislikes_count = None

    context = {
        'admin_likes': admin_likes,
        'admin_dislikes': admin_dislikes,
        'user_likes': user_likes,
        'user_dislikes': user_dislikes,
        'my_likes': my_likes,

        # Individual group counts
        'admin_likes_count': admin_likes_count,
        'admin_dislikes_count': admin_dislikes_count,
        'user_likes_count': user_likes_count,
        'user_dislikes_count': user_dislikes_count,

        # Total counts for admins (global)
        'total_likes_count': total_likes_count,
        'total_dislikes_count': total_dislikes_count,

        # Total counts for normal user (their own)
        'my_total_likes_count': my_total_likes_count,
        'my_total_dislikes_count': my_total_dislikes_count,
    }
    return render(request, 'all_likes.html', context)






# feedbacks
def feedbacks(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')[:12]
    return render(request, 'feedbacks.html', {'feedbacks': feedbacks})

# all feedback
def all_feedbacks(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    feedback_count = feedbacks.count()
    return render(request, 'all_feedbacks.html', {
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
    })


#  delete feedback
def delete_feedback(request,id):
    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, id=id)
        feedback.delete()
        messages.success(request, "Feedback deleted successfully.")
        return redirect('feedbacks')  # Redirect to the feedback list page
    else:
        messages.error(request, "Invalid request method for deletion.")
        return redirect('feedbacks')
    


# change password
@login_required
def changepassword(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # save new password
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, "✅ Your password was changed successfully.")
            return redirect("profile")  # change 'profile' to any page you want after success
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "changepassword.html", {"form": form})
