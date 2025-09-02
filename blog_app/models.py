from django.db import models
from django.contrib.auth.models import User
# from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field



# from cloudinary.models import CloudinaryField

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural='categories'


    def __str__(self):
        return self.category_name
 
    
STATUS_CHOICE=(
    ('draft','Draft'),
    ('published','Published')
)

class Blogs(models.Model):
    title = models.CharField(max_length=500, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    Category = models.ForeignKey('Category', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_image = models.ImageField(null=True, blank=True, upload_to='blogs_image')
    short_description = models.CharField(max_length=2000, default='No description')
    blog_body = CKEditor5Field('Text', config_name='default')
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='draft')
    is_featured = models.BooleanField(default=False)  # ✅ Correct spelling
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # 👍 Likes
    liked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_blogs',
        blank=True
    )

    # 👎 Dislikes
    disliked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_blogs',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'blogs'

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.liked_users.count()

    def total_dislikes(self):
        return self.disliked_users.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Blogs, self).save(*args, **kwargs)
    




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(blank=True, null=True, upload_to='profile_image')
    designation = models.CharField(max_length=255, blank=True, null=True)  # Changed from TextField
    location = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)  # Added phone field
    website = models.URLField(max_length=255, blank=True, null=True)
    email=models.CharField(max_length=20,blank=True,null=True)
    blogs_published = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    



# comments class 
class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    blog= models.ForeignKey(Blogs,on_delete=models.CASCADE)
    comment=models.TextField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
     return self.comment
    


# feedback model
class Feedback(models.Model):
    name = models.CharField(max_length=255, default="Guest")   # <-- use CharField for names
    email = models.CharField(max_length=200, blank=True, null=True)
    feedback = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.feedback
    


class LikeDislike(models.Model):
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user')




class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

    class Meta:
        verbose_name_plural = 'contctmassage'



# members means about us

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='team/')
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    bg_gradient = models.CharField(max_length=100, default='linear-gradient(135deg,#ff416c,#ffb347)')

    def __str__(self):
        return self.name



# group image
class TeamGroupImage(models.Model):
    title = models.CharField(max_length=100, default="Our Team")
    image = models.ImageField(upload_to='group_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# subscribe
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
