from django.contrib import admin
from django.urls    import path

from web.views      import *
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('terminal/', views.terminal_view, name='terminal'),

    # Keep these last Blog Contents
    path('blog/',               BlogListView.as_view(), name ='Blog'),
    path('blog/<slug:slug>',    BlogListView.as_view(), name ='Blog'),
    path('<slug:slug>',         BlogDetailView.as_view(), name ='Blog-Detail'),
    
]
