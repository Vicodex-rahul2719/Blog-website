from django import forms
from blog_app.models import Feedback,Subscriber

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name','email', 'feedback']   # user field will be auto-assigned



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Email'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
    'class': 'form-control',
    'placeholder': 'Your Message',
    'rows': 6,   # increase height
}))
    



class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']


