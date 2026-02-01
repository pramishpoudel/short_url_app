from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from .forms import LoginForm, ShortURLForm
from .models import ShortURL
import qrcode
import io
import base64
from PIL import Image

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}!")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


def home(request):
    return render(request, 'home.html')


@login_required
def short_create(request):
    form = ShortURLForm(request.POST or None)
    default_expires = timezone.now() + timedelta(days=30)
    if request.method == 'POST' and form.is_valid():
        original_url = form.cleaned_data['original_url']
        custom_key = form.cleaned_data.get('custom_key')
        expires_at = form.cleaned_data.get('expires_at') or default_expires

        try:
            if custom_key:
                su = ShortURL(owner=request.user, original_url=original_url, key=custom_key, expires_at=expires_at)
            else:
                su = ShortURL(owner=request.user, original_url=original_url, expires_at=expires_at)
            su.save()
        except Exception as e:
            # catch IntegrityError or other DB errors (e.g., race collision)
            form.add_error('custom_key', 'Alias already in use; please choose another.')
            return render(request, 'shorts/create.html', {'form': form})

        messages.success(request, f'Short URL created: {su.short_path}')
        return redirect('short_list')

    # show default expires in form initial if you want (not necessary for creation page)
    return render(request, 'shorts/create.html', {'form': form, 'default_expires': default_expires})


@login_required
def short_list(request):
    qs = ShortURL.objects.filter(owner=request.user)
    return render(request, 'shorts/list.html', {'shorts': qs})


@login_required
def short_edit(request, pk):
    su = get_object_or_404(ShortURL, pk=pk)
    if su.owner != request.user:
        return HttpResponseForbidden()

    # default expiration (30 days) if none exists
    default_expires = timezone.now() + timedelta(days=30)
    initial_expires = su.expires_at or default_expires

    form = ShortURLForm(request.POST or None, initial={
        'original_url': su.original_url,
        'custom_key': su.key,
        'expires_at': initial_expires,
    }, exclude_pk=su.pk)

    if request.method == 'POST' and form.is_valid():
        original_url = form.cleaned_data['original_url']
        custom_key = form.cleaned_data.get('custom_key')
        expires_at = form.cleaned_data.get('expires_at') or default_expires
        # uniqueness is already validated by form using exclude_pk
        su.original_url = original_url
        su.key = custom_key or su.key
        su.expires_at = expires_at
        su.save()
        messages.success(request, 'Short URL updated.')
        return redirect('short_list')
    return render(request, 'shorts/edit.html', {'form': form, 'short': su, 'default_expires': default_expires})


@login_required
def short_delete(request, pk):
    su = get_object_or_404(ShortURL, pk=pk)
    if su.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        su.delete()
        messages.success(request, 'Short URL deleted.')
        return redirect('short_list')
    return render(request, 'shorts/delete.html', {'short': su})


@login_required
def short_regenerate(request, pk):
    su = get_object_or_404(ShortURL, pk=pk)
    if su.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        new_key = su.regenerate_key()
        messages.success(request, f'Key regenerated: {new_key}')
        return redirect('short_list')
    return render(request, 'shorts/regenerate.html', {'short': su})


def short_stats(request, pk):
    su = get_object_or_404(ShortURL, pk=pk)
    if su.owner != request.user:
        return HttpResponseForbidden()

    qr_data_uri = None
    try:
        url = request.build_absolute_uri(su.short_path)
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        data = base64.b64encode(buf.read()).decode('ascii')
        qr_data_uri = f"data:image/png;base64,{data}"
    except Exception:
        qr_data_uri = None

    return render(request, 'shorts/stats.html', {'short': su, 'qr_data_uri': qr_data_uri})


def redirect_view(request, key):
    su = get_object_or_404(ShortURL, key=key)
    if su.is_expired():
        raise Http404('This short link has expired.')
    # increment clicks atomically
    ShortURL.objects.filter(pk=su.pk).update(clicks=F('clicks') + 1)
    return redirect(su.original_url)
    
