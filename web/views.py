from django.shortcuts           import redirect, render,get_object_or_404
from django.views               import View                                                         # Importing django class based view
from django.views.generic       import CreateView, TemplateView, ListView, UpdateView, DetailView   # Importing django generic class based view
from django.http                import Http404

from django.contrib.auth.mixins     import LoginRequiredMixin
from django.contrib.auth.forms      import AuthenticationForm, UserCreationForm
from django.contrib.auth.views      import LoginView, LogoutView
from django.views.generic           import CreateView
from django.urls                    import reverse_lazy
from django.contrib.auth            import login, authenticate
from django.contrib.auth.decorators import login_required

from web.models                 import *

from django.shortcuts import render



class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "web/index.html"
    
    def get(self, request, *args, **kwargs):
        # Fetch all hosts
        all_hosts = Host.objects.all()
        # Filter hosts by checking if the user has 'view_host' permission on each
        # This ensures only permitted hosts are displayed to the logged-in user.
        permitted_hosts = [h for h in all_hosts if request.user.has_perm('view_host', h)]

        return render(request, 'web/index.html', {'hosts': permitted_hosts})


class LoginView(LoginView):
    template_name               = 'web/auth/login.html'
    authentication_form         = AuthenticationForm
    redirect_authenticated_user = True

class LogoutView(LogoutView):
    template_name               = 'web/auth/logged_out.html'




@login_required
def terminal_view(request, host_id):
    """
    Display the terminal page for a given host.
    Only allow this view if the user is logged in and has the 'view_host' permission
    on that specific host instance.
    """
    host = get_object_or_404(Host, pk=host_id)

    # Check if the current logged-in user has 'view_host' permission on this host
    if not request.user.has_perm('view_host', host):
        # If not permitted, return a 403 response
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have the required permission to view this host.")

    return render(request, 'web/terminal.html', {'host_id': host_id, 'host': host,'websocket_url': settings.WEBSOCKET_URL})









class BlogListView(ListView):
    model           = Blog
    paginate_by     = 12
    template_name   = "web/blog.html"
    ordering        = ['order_by']

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogListView, self).get_queryset()

        # If no slug is passed then set slug value as all
        try:
            if self.kwargs['slug']:
                pass
        except KeyError:
            self.kwargs['slug'] = 'all'


        try:
            BlogCategory.objects.get(slug=self.kwargs['slug'])
            pass
        except:
            raise Http404("Blog Category does not exist")

        if self.kwargs['slug']=='all':
            qs  =   qs
        else:
            qs  =   qs.filter(category__slug=self.kwargs['slug'])
            
        if self.request.GET.get('q'):
            qs  =   qs.filter(title__icontains=self.request.GET.get('q'))
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = BlogCategory.objects.get(slug=self.kwargs['slug'])
        context['all_category'] = BlogCategory.objects.all()
        context['settings'] = SiteSetting.objects.all().first()
        return context


class BlogDetailView(View):
    template_name = "web/blog-detail.html"

    def get(self, request, slug, *args, **kwargs):

        try:
            blog    =   Blog.objects.get(slug=slug)
            tags    =   [t for t in blog.tags.split(',')]   
        except Blog.DoesNotExist:
            raise Http404("Page not found")

        # contact_form    =   ContactForm()
        
        context =   {
            # 'contact_form': contact_form,
            'blog': blog,
            'tags': tags,
            'settings': SiteSetting.objects.all().first(),
        }

        return render(request, self.template_name, context)




# Django Unfold Admin
def dashboard_callback(request, context):

    # if(closing.object.get(date=yesterday_date).exists()):
    # do nothing
    # else
    # incoming_money_total = get all incoming money of yesterday
    # outgoing_money_total = get all outgoing money of yesterday
    # yesterday_closing_balance = incoming_money_total - outgoing_money_total
    # total_balance = 
    # closing.object.create(date=yesterday_date, closing_balance=yesterday_closing_balance)


    context.update({
        "custom_variable": "value",
        "cards": [
            {"title": "Card 1", "metric": "Metric 1"},
            {"title": "Card 2", "metric": "Metric 2"},
            {"title": "Card 3", "metric": "Metric 3"},
        ],
        "navigation": [
            {"title": "Dashboard", "link": "/", "icon": "dashboard"},
            {"title": "Users", "link": "/admin/users", "icon": "people"},
        ],
        "filters": [
            {"title": "Filter 1", "link": "/filter1"},
            {"title": "Filter 2", "link": "/filter2"},
        ],
    })
    return context