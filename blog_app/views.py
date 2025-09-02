from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Category,Blogs,Comment,Profile,Feedback,TeamMember,TeamGroupImage
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout as auth_logout, login as auth_login
from django.db.models import Count
from blog_project.forms import FeedbackForm,ContactForm,SubscriberForm
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.


# home 
def home(request):
    categories = Category.objects.all()

    # Featured posts
    featured_posts = Blogs.objects.filter(is_featured=True, status='published') \
        .annotate(comment_count=Count('comment'))[:7]

    # Most commented posts
    most_commented = Blogs.objects.filter(
        is_featured=True,
        status="published"
    ).exclude(slug__isnull=True).exclude(slug="") \
     .annotate(comment_count=Count("comment")) \
     .order_by("-comment_count").first()

    # Latest posts
    latest_posts = Blogs.objects.filter(is_featured=False, status='published') \
        .annotate(comment_count=Count('comment'))[:7]

    # Feedback form handling
    form = FeedbackForm()
    if request.method == "POST" and "feedback_field_name" in request.POST:  # 👈 check if it's feedback form
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, "✅ Thank you for your feedback!")
            return redirect('home')
        else:
            messages.error(request, "❌ Please correct the errors in the form.")

    feedback_list = Feedback.objects.order_by('-created_at')[:16]

    return render(request, 'home.html', {
        'categories': categories,
        'featured_posts': featured_posts,
        'most_commented': most_commented,
        'latest_posts': latest_posts,
        'form': form,
        'feedback_list': feedback_list
    })








def contact(request):
    return render(request,'contact.html')
 
def specific_category(request,category_id):
    # c=Category.objects.all()
    post=Blogs.objects.filter(status='published',Category=category_id)
    # category=Category.objects.get(pk=category_id)
    category=get_object_or_404(Category,pk=category_id)
    return render(request,'specific_category.html',{'post':post,'category':category})


# all content for all category and single page
def blogs(request,slug):
    single_post=get_object_or_404(Blogs,slug=slug,status='published')
    f=Blogs.objects.filter(is_featured=True,status='published')[:7]

    if request.method == 'POST':
          # only save if not empty
        comment = Comment()
        comment.user = request.user
        comment.blog = single_post
        comment.comment = request.POST.get('comment')  # maps to your model field
        comment.save()
        messages.success(request,'Commented successfully')
        return HttpResponseRedirect(request.path_info)

    comments= Comment.objects.filter(blog = single_post)
    comments_count= comments.count()
    return render(request,'blogs.html',{'single_post':single_post,'f':f,'comments':comments,'comments_count':comments_count})



def all_blog(request):
    blog = Blogs.objects.annotate(comment_count=Count('comment'))  # ✅ add comment count
    return render(request, 'all_blog.html', {'blog': blog})


def all_category(request):
    categories=Category.objects.all()
    # post=Blogs.objects.filter(status='published',Category=category_id
    return render(request,'all_category.html',{'categories':categories,})


def featured_post(request):
    f = Blogs.objects.filter(is_featured=True, status='published') \
                     .annotate(comment_count=Count('comment'))
    return render(request, 'featured_post.html', {'f': f})


def latest_post(request):
   latest_post=Blogs.objects.filter(is_featured=False, status='published') \
                     .annotate(comment_count=Count('comment'))
   return render(request,'latest_post.html',{'latest_post':latest_post,})



# all feedback
def all_feedback(request):
    feedbacks = Feedback.objects.order_by('-created_at')  # show latest first
    total_feedback = feedbacks.count()

    return render(request, 'all_feedback.html', {
        'feedbacks': feedbacks,
        'total_feedback': total_feedback,
    })



# search functionality
# from django.db.models import Q, Count

def search(request):
    keyword = request.GET.get('keyword')
    blog = Blogs.objects.filter(
        Q(title__icontains=keyword) | 
        Q(short_description__icontains=keyword) | 
        Q(blog_body__icontains=keyword),
        status='published'
    ).annotate(comment_count=Count('comment'))   # ✅ add comment count

    return render(request, 'search.html', {
        'blog': blog,
        'keyword': keyword
    })


#  register with mail sending
def register(request):
    try:
        if request.method == 'POST':
            email = request.POST['email']
            fullname = request.POST['fullname']
            number = request.POST['number']
            password = request.POST['password']
            cpassword = request.POST['cpassword']

            if User.objects.filter(username=number).exists():
                messages.error(request, "Given Number already exists")
                return redirect("register")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Given Email already exists")
                return redirect("register")

            if password != cpassword:
                messages.error(request, "Password and confirm password are not same")
                return redirect("register")

            if len(number) != 10 or not number.isdigit():
                messages.error(request, "Enter a valid number")
                return redirect("register")

            if len(password) < 8:
                messages.error(request, "Password is too short")
                return redirect("register")

            # Create User
            user = User.objects.create_user(username=number, email=email, password=password)
            user.first_name = fullname
            user.save()

            # Create Profile only if it does not exist
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': number,
                    'designation': '',
                    'location': '',
                    'email': email
                }
            )

            # ✅ Send success mail
            subject = "Welcome to Premium Blog!"
            message = f"Hello {fullname},\n\nYou have successfully registered on our blog website.\n\nLogin and start writing blogs!\n\nRegards,\nPremium Blog Team"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            messages.success(request, "Successfully Registered. A confirmation mail has been sent to your email.")
            return redirect('/login/')

        else:
            return render(request, 'register.html')

    except Exception as e:
        return HttpResponse(str(e))




# login form



def login(request):
    try:
        if request.method == 'POST':
            number= request.POST['username']
            password = request.POST['password']

            # Check user existence by number or email
            try:
                user_obj = User.objects.get(username=number)
            except User.DoesNotExist:
                    messages.error(request, "Phone number does not match any account !")
                    return redirect('/login/')

            # Authenticate with username
            user = authenticate(username=user_obj.username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, "Successfully Logged In")
                return redirect('/dashboard/')
            else:
                messages.error(request, "Password is incorrect")
                return redirect('/login/')

        return render(request, 'login.html')
    except Exception as e:
        return HttpResponse(e)



# logout method
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request,'Successfully Logged Out')
        return redirect('/login/')
    
    return render(request,'login.html')







#  contact form with email sending on admin
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            subject = f"New Contact Form Submission from {name}"
            full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

            try:
                send_mail(
                    subject,
                    full_message,
                    settings.EMAIL_HOST_USER,
                    [settings.ADMIN_EMAIL],   # where the mail goes
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

            return redirect("contact")  # redirect back to same page
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})





#  about page
def about(request):
    team_members = TeamMember.objects.all()
    group_image = TeamGroupImage.objects.first()
    context = {
        'team_members': team_members,
        'group_image': group_image,  # optional model for group image
    }
    return render(request, 'about.html', context)


# subscribe
def subscribe(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()

            # Send confirmation email
            try:
                send_mail(
                    subject="Thank you for subscribing!",
                    message="You have successfully subscribed to our blog. Stay tuned for updates! 🚀",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[subscriber.email],
                    fail_silently=False,
                )
                messages.success(request, "✅ Subscribed successfully! Please check your email.")
            except Exception as e:
                # Email failed, but subscription still works
                messages.warning(request, f"⚠️ Subscribed, but email could not be sent. {e}")

            return redirect('home')  # Redirect back to home after subscription
        else:
            messages.error(request, "❌ Please correct the errors in the form.")
            return redirect('home')  # Redirect even if form invalid
    else:
        return redirect('home')




# policy
def policy(request):
    return render(request,'policy.html')