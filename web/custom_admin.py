from django.urls import path
from django.contrib.admin import AdminSite
from django.shortcuts import render

class TerminalAdmin(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('terminal/', self.admin_view(self.terminal_view), name='terminal'),
        ]
        return custom_urls + urls

    def terminal_view(self, request):
        return render(request, 'admin/terminal.html')  # Template for terminal widget
