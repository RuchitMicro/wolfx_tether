"""
Django settings for wolfx_tether project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9)3dgg7ca0(0j+w6)dgb&w6kn*@3j1b=qbru#!4-5)ur#ni3%c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "unfold",                           # before django.contrib.admin
    "unfold.contrib.filters",           # optional, if special filters are needed
    "unfold.contrib.forms",             # optional, if special form elements are needed
    "unfold.contrib.import_export",     # optional, if django-import-export package is used
    "unfold.contrib.guardian",          # optional, if django-guardian package is used
    "unfold.contrib.simple_history",    # optional, if django-simple-history package is used
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'guardian',
    'channels',
    'simple_history',
    'import_export',
    'tinymce',
    
    'web'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wolfx_tether.urls'

LOGIN_REDIRECT_URL = 'admin'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.context_processor.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'wolfx_tether.wsgi.application'

ASGI_APPLICATION = 'wolfx_tether.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Django Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Django Guardian
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'web/static'),
]
STATIC_ROOT =  os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
UNFOLD = {
    "SITE_TITLE": 'Wolfx Tether Admin',
    "SITE_HEADER": 'Wolfx Tether Admin',
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    # # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    # "ENVIRONMENT": "sample_app.environment_callback",
    # "DASHBOARD_CALLBACK": "web.views.dashboard_callback",
    "THEME": "light", # Force theme: "dark" or "light". Will disable theme switcher
    # "LOGIN": {
    #     "image": lambda request: static("sample/login-bg.jpg"),
    #     "redirect_after": lambda request: reverse_lazy("admin:web_APP_MODEL_changelist"),
    # },
    # "STYLES": [
    #     lambda request: static("web/css/style.css"),
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/script.js"),
    # ],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    # "EXTENSIONS": {
    #     "modeltranslation": {
    #         "flags": {
    #             "en": "🇬🇧",
    #             "fr": "🇫🇷",
    #             "nl": "🇧🇪",
    #         },
    #     },
    # },
    "SIDEBAR": {
        "show_search": True,
        # "show_all_applications": True,
        "navigation": [
        {
            "title": ("Main"),
            "items": [
                {
                    "title": ("Dashboard"),
                    "icon": "dashboard",  
                    "link": reverse_lazy("admin:index"),
                },
                {
                    "title": ("Host"),
                    "icon": "dns",  
                    "link": reverse_lazy("admin:web_host_changelist"),
                },
                {
                    "title": ("SiteSetting"),
                    "icon": "settings",  
                    "link": reverse_lazy("admin:web_sitesetting_changelist"),
                },
                {
                    "title": ("ImageMaster"),
                    "icon": "image",  
                    "link": reverse_lazy("admin:web_imagemaster_changelist"),
                },
                {
                    "title": ("FileMaster"),
                    "icon": "file_copy",  
                    "link": reverse_lazy("admin:web_filemaster_changelist"),
                },
                {
                    "title": ("Head"),
                    "icon": "print",  # Icon for "print" is OK, consider "title" if it refers to headings.
                    "link": reverse_lazy("admin:web_head_changelist"),
                },
                {
                    "title": ("Contact"),
                    "icon": "contact_mail",  
                    "link": reverse_lazy("admin:web_contact_changelist"),
                },
            ],
        },
        {
            "title": ("Authentication and Authorization"),
            "separator": True,
            "items": [
                {
                    "title": ("Users"),
                    "icon": "person",  
                    "link": "/admin/auth/user/",
                },
                {
                    "title": ("Groups"),
                    "icon": "group",  
                    "link": "/admin/auth/group/",
                },
            ],
        },]
    }
}
