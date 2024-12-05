# """
# URL configuration for mira project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib             import admin
# from django.urls                import path,include,re_path
# from django.conf.urls.static    import static   # static file config
# from django.conf                import settings # static file config


# urlpatterns = [
#     re_path(r'^admin/shell/', include('django_admin_shell.urls')),
#     re_path(r'^admin/', admin.site.urls),
#     path('',include('web.urls')),
# ]
# urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) # static file config


from django.urls import path
from web.custom_admin import TerminalAdmin
from django.contrib import admin

custom_admin_site = TerminalAdmin(name="custom_admin")

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # Use custom admin
]