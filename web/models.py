# Code generated from Spectre
from django.db                          import models, IntegrityError
from django.db.models.aggregates        import Max
from django.contrib                     import admin
from django.contrib.sessions.models     import Session
from django.contrib.auth.models         import User
from django.db.models                   import Avg
from django.core.exceptions             import ValidationError
from django.core.serializers            import serialize
from django.conf                        import settings
from django.db.models.signals           import pre_save
from django.utils.html                  import format_html
from django.urls                        import reverse

# Timezone
from django.utils   import timezone

# Signals
from django.db.models.signals       import post_save
from django.dispatch                import receiver

# HTML Safe String  
from django.utils.safestring        import mark_safe

# Send mail Django's Inbuilt function
from django.core.mail               import send_mail
from django.template.loader         import render_to_string

# Json
import json

# Forms
from django                 import forms       

# Regex
import re

# Django Settings
from django.conf            import settings

# UUID
import uuid

# Django Validators
from django.core.validators import MaxValueValidator, MinValueValidator

# Urllib
import urllib.parse

# Simple History Model
from simple_history.models import HistoricalRecords

# Model Utils
from model_utils        import FieldTracker
from model_utils.fields import MonitorField, StatusField

# TinyMCE
from tinymce.models                 import HTMLField

# Encryption
import base64
import hashlib
from cryptography.fernet import Fernet




class CommonModel(models.Model):
    extra_params    =   models.JSONField        (blank=True, null=True)
    created_at      =   models.DateTimeField    (auto_now_add=True, blank=True, null = True)
    updated_at      =   models.DateTimeField    (auto_now=True, blank=True, null=True)
    created_by      =   models.CharField        (max_length=300, blank=True, null=True)
    updated_by      =   models.CharField        (max_length=300, blank=True, null=True)
    
    history                 =   HistoricalRecords(inherit=True)
    tracker                 =   FieldTracker()

    admin_meta      =   {}
    
    class Meta:
        abstract = True

    # Helper function to get json data of the model
    def get_json(self):
        # Serialize the model instance into JSON format
        data = serialize('json', [self], ensure_ascii=False)
        
        # Convert the serialized data into a Python object
        data = json.loads(data)
        
        # Return the first item in the list as we are serializing a single instance
        return data[0] if data else {}


# Global Settings
class SiteSetting(CommonModel):
    logo                    =   models.ImageField   (blank=True,null=True,upload_to='settings/')
    favicon                 =   models.FileField    (blank=True,null=True,upload_to='settings/')
    global_head             =   models.TextField    (blank=True,null=True, help_text='Common <head> data. It will appear in all pages.')

    address                 =   models.TextField    (blank=True,null=True,max_length=500)
    contact_number          =   models.CharField    (blank=True,null=True,max_length=13)
    email                   =   models.EmailField   (blank=True,null=True)
    gst                     =   models.CharField    (blank=True,null=True,max_length=15, help_text="GST Number")
    extra_contact_details   =   models.TextField           (blank=True,null=True)

    facebook                =   models.URLField     (blank=True,null=True,max_length=100)
    instagram               =   models.URLField     (blank=True,null=True,max_length=100)
    twitter                 =   models.URLField     (blank=True,null=True,max_length=100)
    linkedin                =   models.URLField     (blank=True,null=True,max_length=100)

    vision                  =   models.TextField    (blank=True,null=True)
    mission                 =   models.TextField    (blank=True,null=True)
    values                  =   models.TextField    (blank=True,null=True)
    brochure                =   models.FileField    (blank=True,null=True,upload_to='settings/')
    
    navigation_menu         =   models.JSONField    (blank=True, null=True)

    about_us                =   models.TextField       (blank=True,null=True)
    terms_and_conditions    =   models.TextField       (blank=True,null=True)
    privacy_policy          =   models.TextField       (blank=True,null=True)
    return_policy           =   models.TextField       (blank=True,null=True)
    disclaimer              =   models.TextField       (blank=True,null=True)

    robots                  =   models.FileField    (blank=True,null=True,upload_to='settings/')
    

    # JSON FIELD SCHEMA
    key_value_pair_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "navMenu": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/menuItem"
            }
            }
        },
        "definitions": {
            "menuItem": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier for the menu item."
                },
                "label": {
                    "type": "string",
                    "description": "Display text for the menu item."
                },
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL link for the menu item."
                },
                "children": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/menuItem"
                },
                "description": "Nested menu items under this menu item."
                }
            },
            "required": ["id", "label"],
            "additionalProperties": False
            }
        }
    }

        
    admin_meta = {
        "json_fields": {
            "navigation_menu": {"schema":  json.dumps(key_value_pair_schema)},
        }
    }
    
    def __str__(self):
        return 'Edit Site Settings'

    class Meta:
        verbose_name_plural = "Site Setting"
    
    def save(self, *args, **kwargs):
        super(SiteSetting, self).save(*args, **kwargs)


# Image Master
class ImageMaster(CommonModel):
    name                =   models.CharField        (max_length=300)
    image               =   models.ImageField       (upload_to="image_master/")
    
    created_at          =   models.DateTimeField    (auto_now_add=True, blank=True, null = True)
    updated_at          =   models.DateTimeField    (auto_now=True, blank=True, null=True)
    
    admin_meta = {
        'list_display': ['name', 'image','__str__', 'created_at', 'updated_at', 'created_by', 'updated_by',],   
    }

    def __str__(self):
        return mark_safe(
            '<div style="height:200px;width:200px;"><img src='+self.image.url+' style="object-fit:contain;height:100%;width:100%" alt=""></div>'
        )


# File Master
class FileMaster(CommonModel):
    name                =   models.CharField    (max_length=300)
    file                =   models.FileField    (upload_to='file_master/')

    created_at          =   models.DateTimeField    (auto_now_add=True, blank=True, null = True)
    updated_at          =   models.DateTimeField    (auto_now=True, blank=True, null=True)

    admin_meta = {
        'list_display': ['name', 'file', '__str__', 'created_at', 'updated_at', 'created_by', 'updated_by'],   
    }

    def __str__(self):
        return str(self.name)

# Contact
class Contact(CommonModel):
    full_name       =   models.CharField    (max_length=300)
    email_id        =   models.EmailField   (max_length=300)
    phone_number    =   models.CharField    (max_length=20)
    requirement     =   models.TextField       ()
    email_ok        =   models.BooleanField (default=False)

    journey_path    =   models.TextField    (blank=True, null=True, help_text='A complete url trace of user journey that lead them to fill the form.')
    
    created_at      =   models.DateTimeField    (auto_now_add=True, blank=True, null = True)
    updated_at      =   models.DateTimeField    (auto_now=True, blank=True, null=True)

    admin_meta = {
        'list_display': ['full_name', 'email_id', 'phone_number', 'created_at', 'updated_at',],
    }

    def __str__(self):
        return str(self.full_name)

    # Notification to Support about a new entry
    def send_mail_notification(self):
        msg_html = render_to_string('web/email/new_enquiry.html', {'Contact': self})
        send_mail(
            'New enquiry from WOLFx',
            'Hello',
            'support@wolfx.io',
            ['hello@wolfx.io'],
            fail_silently=True,
            html_message=msg_html,
        )

    # Notification to User
    def send_mail_greeting(self):
        msg_html = render_to_string('web/email/thank_you_for_contacting.html', {'Contact': self})
        send_mail(
            'WOLFx: Thank you for Contacting us',
            'Hello',
            'support@wolfx.io',
            ['hello@wolfx.io'],
            fail_silently=True,
            html_message=msg_html,
        )


class Host(CommonModel):
    HOST_ADDRESS_VALIDATOR = re.compile(
        r"^(?:(?:[a-zA-Z0-9-]+\.)+(?:[a-zA-Z]{2,})|(?:\d{1,3}\.){3}\d{1,3})$"
    )
    
    name            =   models.CharField    (max_length=300,null=True, help_text="Enter a unique name for the host.")
    host_address    =   models.CharField    (max_length=255,null=True,help_text="Enter an host_address(ip) or domain name for the host.",)
    port            =   models.IntegerField (default=22,null=True, help_text="Specify the port number for SSH connections (default is 22).")
    username        =   models.CharField    (max_length=300,null=True, help_text="Enter the username for authenticating with the host.")
    password        =   models.CharField    (max_length=300, blank=True, null=True, help_text="Enter the password for authentication and select use_credentials to Password")
    pem_file        =   models.FileField    (upload_to='pem_file/', blank=True, null=True, help_text="Upload a PEM file for key-based authentication and and select use_credentials to PEM File")
    use_credential  =   models.CharField    (max_length=10,choices=[("password", "Password"),("pem", "PEM File"),],default="password",help_text="Specify whether to use a password or PEM file for authentication.",)
    description     =   models.TextField    (blank=True, null=True, help_text="Provide a brief description or notes about the host.")

    encrypted_pem   = models.BinaryField(blank=True, null=True, help_text="Encrypted PEM file data.")
    
    admin_meta = {
        'list_display': ['name', 'host_address', 'port', 'username', 'created_at', 'updated_at','open_terminal'],
        'search_fields': ['name','host_address','port','username',],
        'list_filter': ['use_credential'],
        'radio_fields'  :{"use_credential": admin.VERTICAL}
        
    }
    
    def open_terminal(self):
        """
        Add a clickable link in the admin list view that redirects to the terminal view.
        """
        url = reverse('terminal-view', args=[self.id])  # Use the terminal-view URL pattern
        return format_html(f'<a href="{url}" target="_blank">Open Terminal</a>')

    open_terminal.short_description = "Action"

    @staticmethod
    def _get_fernet_key():
        """
        Derive a 32-byte Fernet key from the Django SECRET_KEY.
        """
        secret = settings.SECRET_KEY.encode('utf-8')
        sha = hashlib.sha256(secret).digest()
        fernet_key = base64.urlsafe_b64encode(sha)
        return fernet_key

    @staticmethod
    def encrypt_password(plain_text_password):
        """
        Encrypt the given plain text password using Fernet symmetric encryption.
        """
        if not plain_text_password:
            return plain_text_password
        fernet_key = Host._get_fernet_key()
        f = Fernet(fernet_key)
        encrypted = f.encrypt(plain_text_password.encode('utf-8'))
        return encrypted.decode('utf-8')

    @staticmethod
    def decrypt_password(encrypted_password):
        """
        Decrypt the given encrypted password using Fernet symmetric decryption.
        """
        if not encrypted_password:
            return encrypted_password
        try:
            fernet_key = Host._get_fernet_key()
            f = Fernet(fernet_key)
            decrypted = f.decrypt(encrypted_password.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception:
            return ""

    @staticmethod
    def encrypt_pem(pem_data):
        """
        Encrypt PEM data using Fernet symmetric encryption.
        """
        if not pem_data:
            return pem_data
        fernet_key = Host._get_fernet_key()
        f = Fernet(fernet_key)
        encrypted = f.encrypt(pem_data)
        return encrypted

    @staticmethod
    def decrypt_pem(encrypted_pem):
        """
        Decrypt PEM data using Fernet symmetric decryption.
        """
        if not encrypted_pem:
            return encrypted_pem
        try:
            fernet_key = Host._get_fernet_key()
            f = Fernet(fernet_key)
            decrypted = f.decrypt(encrypted_pem)
            return decrypted
        except Exception:
            return b""
        
    def __str__(self):
        return f"{self.name}: {self.host_address}"

# Signal to ensure password is always encrypted before saving
@receiver(pre_save, sender=Host)
def encrypt_host_credentials_before_save(sender, instance, **kwargs):
    """
    This signal ensures that whenever a Host is saved,
    its password and pem_file fields are stored in encrypted form.
    """
    
    """
    Validates if the input is a valid domain name or IP address.
    """
    if not Host.HOST_ADDRESS_VALIDATOR.match(instance.host_address):
        raise ValidationError(
            f"{instance.host_address} is not a valid IP address or domain name."
        )

    # Encrypt Password
    if instance.password:
        test_decrypt = Host.decrypt_password(instance.password)
        if test_decrypt == "":
            # Password is not encrypted yet
            instance.password = Host.encrypt_password(instance.password)

    # Encrypt PEM File
    if instance.pem_file:
        # Read the uploaded PEM file
        pem_content = instance.pem_file.read()
        if pem_content:
            # Encrypt the PEM data
            encrypted_pem = Host.encrypt_pem(pem_content)
            # Store the encrypted data
            instance.encrypted_pem = encrypted_pem
            # Clear the pem_file field
            instance.pem_file = None

    # Ensure that if pem_file is being cleared, encrypted_pem is also cleared
    if not instance.pem_file and not instance.encrypted_pem:
        instance.encrypted_pem = None
        

# Blog Models
class BlogCategory(CommonModel):
    category    =   models.CharField(max_length=100, unique=True)
    slug        =   models.SlugField(max_length=100, unique=True)
    image       =   models.FileField(blank=True, null=True, upload_to='blog_category/')
    parent      =   models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        # Recursively build the full category path
        if self.parent:
            return f"{self.parent} -> {self.category}"
        return self.category
    
    def clean(self):
        # Ensure that no cyclic dependencies are created
        if self.parent:
            parent = self.parent
            while parent is not None:
                if parent == self:
                    raise ValidationError("A category cannot be a parent of itself or one of its descendants.")
                parent = parent.parent

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['category']

class Blog(CommonModel):

    head_default='''<meta name="title" content=" ">
    <meta name="description" content=" ">
    <meta name="keywords" content=" ">
    <meta name="robots" content="index, follow">'''

    title               =   models.CharField        (max_length=200)
    sub_title           =   models.CharField        (max_length=200, blank=True ,null=True)
    thumbnail           =   models.ImageField       (upload_to="blog/")
    category            =   models.ForeignKey       (BlogCategory, null=True, on_delete=models.SET_NULL)
    featured_text       =   models.TextField           (null=True, blank=True)
    text                =   models.TextField           (null=True, blank=True)
    slug                =   models.SlugField        (unique=True)
    readtime            =   models.CharField        (max_length=200,null=True, blank=True)
    tags                =   models.TextField        (null=True, blank=True, default='all')
    head                =   models.TextField        (null=True, blank=True, default=head_default)
    
    order_by            =   models.IntegerField     (default=0)
    
    created_at          =   models.DateTimeField    (auto_now_add=True, blank=True, null=True)
    updated_at          =   models.DateTimeField    (auto_now=True, blank=True, null=True)
    created_by          =   models.CharField        (max_length=300)

    admin_meta =    {
        'list_display'      :   ("__str__","category","created_at","updated_at"),
        'list_editable'     :   ("category",),
        'list_per_page'     :   50,
        'list_filter'       :   ("category",),
        'inline'            :   [
            {'BlogImage': 'blog'}
        ]
    }

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "Blog"
        ordering = ['order_by'] #Sort in desc order

class BlogImage(CommonModel):
    blog                =   models.ForeignKey       (Blog, on_delete=models.CASCADE)
    image               =   models.ImageField       (upload_to="blog_images/")
    order_by            =   models.IntegerField     (default=0)

    def __str__(self):
        return str(self.blog)

    class Meta:
        verbose_name_plural = "Blog Image"
        ordering = ['order_by'] #Sort in desc order
    


# Dynamic Head
# Injects data inside <head> of a specific target url
# Used for SEO
class Head(CommonModel):
    target_url  =   models.URLField     (unique=True, help_text="Enter absolute URL of the target.  <br> Ex: https://wolfx.io/blog <br> https://wolfx.io/blog/ <br> https://wolfx.io/blog?category=UI-UX ")
    head        =   models.TextField    (help_text="Head Data")

    def __str__(self):
        return str(self.target_url)
