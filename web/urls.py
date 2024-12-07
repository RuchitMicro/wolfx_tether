from django.contrib import admin
from django.urls    import path

from web.views      import *
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    # Auth
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    
    # Terminal
    path('terminal/<int:host_id>/', terminal_view, name='terminal-view'),
    
    # Keep these last Blog Contents
    path('blog/',               BlogListView.as_view(), name ='Blog'),
    path('blog/<slug:slug>',    BlogListView.as_view(), name ='Blog'),
    path('<slug:slug>',         BlogDetailView.as_view(), name ='Blog-Detail'),
    
]
