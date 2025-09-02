from django import forms
# # from django.contrib.auth.models import User
from blog_app.models import Category
from blog_app.models import Profile ,Blogs # Assuming you have a Profile model
from django_ckeditor_5.widgets import CKEditor5Widget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name',]
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }



class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    
    class Meta:
        model = Profile
        fields = ['profile_image','designation','location','phone','website','email']





class BlogsForm(forms.ModelForm):
    blog_body = forms.CharField(widget=CKEditor5Widget())

    class Meta:
        model = Blogs
        fields = ['title','Category','blog_image','short_description','blog_body','status','is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control premium-input',
                'placeholder': 'Enter blog title',
            }),
            'Category': forms.Select(attrs={
                'class': 'form-select premium-select',
            }),
            'blog_image': forms.ClearableFileInput(attrs={
                'class': 'form-control premium-file',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select premium-select',
            }),
            'is_feacherd': forms.CheckboxInput(attrs={
                'class': 'form-check-input premium-checkbox',
            }),
        }


class AddUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','password1', 'password2', 'is_active', 'is_staff','is_superuser','groups','user_permissions']




class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        ]

