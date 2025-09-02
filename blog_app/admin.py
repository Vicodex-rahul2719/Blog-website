from django.contrib import admin
from blog_app.models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display=('id','category_name','created_at','updated_at')


class BlogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'Category', 'author', 'blog_image', 'status', 'is_featured', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields=('id','title','Category__category_name','status')
    list_editable=('is_featured','blog_image')



admin.site.register(Category,CategoryAdmin)
admin.site.register(Blogs,BlogsAdmin)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Feedback)
admin.site.register(ContactMessage)
admin.site.register(TeamMember)
admin.site.register(TeamGroupImage)

