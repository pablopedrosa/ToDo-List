import re
from django.conf import settings
from django.template import RequestContext
from django.contrib.sites.models import Site, RequestSite
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login as auth_login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.simple import direct_to_template
from dbe.todo.forms import RegistrationForm
from dbe.todo.models import Item, User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse 

def login(request, template_name='admin/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            
            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL
            
            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)
        registration_form = RegistrationForm()
    
    request.session.set_test_cookie()
    
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    
    return render_to_response(template_name, {
        'form': form,
        'regform': registration_form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))


def index (request):
    if not request.POST and ('_auth_user_id' not in request.session or ('_auth_user_id' in request.session and not request.session['_auth_user_id'])):
        form = RegistrationForm()
        
        return render_to_response('index.html', {
            'form': form,
        })
    else:
        if request.POST:
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
        else:
            user = User.objects.get(pk=request.session['_auth_user_id'])

        if user is not None:
            if user.is_active:
                if '_auth_user_id' not in request.session or ('_auth_user_id' in request.session and not request.session['_auth_user_id']):
                    login(request, user)
                    
                try:
                    p = Item.objects.filter(user = user.pk)
                except Item.DoesNotExist:
                    raise Http404
                
                return render_to_response('main.html', {'user': user, 'authenticated': user.is_authenticated(), 'items': p})
            else:
                return direct_to_template(request, 'inactive_account.html')
        else:
            return direct_to_template(request, 'invalid_login.html')


def mylogout(request):
    logout(request)
    return HttpResponseRedirect('/')


def item_action(request, action, pk):
    item = Item.objects.get(pk=pk)
    
    if action == "done":
        item.done = True
        item.save()
    elif action == "delete":
        item.delete()
    elif action == "onhold":
        item.onhold = not item.onhold 
        item.save()
    
    return HttpResponseRedirect(reverse("admin:todo_item_changelist"))


def onhold_done(request, mode, action, pk):
    item = Item.objects.get(pk=pk)

    if action == "yes":
        if mode == "done": item.done = True
        elif mode == "onhold": item.onhold = True
    elif action == "no":
        if mode == "done": item.done = False
        elif mode == "onhold": item.onhold = False

    item.save()
    return HttpResponse('')


def progress(request, pk):
    p = request.POST
    if "progress" in p:
        item = Item.objects.get(pk=pk)
        item.progress = int(p["progress"])
        item.save()
    return HttpResponse('')


def signup(request, success_url=None, extra_context=None):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            basic_group = Group.objects.get(name='Basicos')
            new_user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password1'])
            new_user.is_staff = True
            new_user.groups.add(basic_group)
            new_user.save()
            authenticate(username=request.POST['username'], password=request.POST['password1'])

            if success_url is None:
                return render_to_response('signup.html')
            else:
                return render_to_response('invalid_login.html')
    else:
        return redirect('/');
    
    return render_to_response('index.html', {'form': form})


@login_required
def itemindex(request):
    return HttpResponseRedirect(reverse("admin:todo_item_changelist"))


def barchart(request):
    if not request.POST:
        return render_to_response('graphs/items.html', {'user': request.user, 'authenticated': request.user.is_authenticated()})
    else:
        #instantiate a drawing object
        import mycharts
        d = mycharts.MyBarChartDrawing()
    
        #extract the request params of interest.
        #I suggest having a default for everything.
        if 'height' in request.GET:
            d.height = int(request.GET['height'])
        if 'width' in request.GET:
            d.width = int(request.GET['width'])
        
        if 'numbers' in request.GET:
            strNumbers = request.POST['numbers']
            numbers = map(int, {1,2,4,5})    
            d.chart.data = [numbers]   #bar charts take a list-of-lists for data
    
        if 'title' in request.GET:
            d.title.text = request.GET['title']
      
    
        #get a GIF (or PNG, JPG, or whatever)
        binaryStuff = d.asString('png')
        return HttpResponse(binaryStuff, 'image/png')
