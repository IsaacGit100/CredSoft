

# Create your views here.

from django.utils import timezone
from SysSetup.models import SystemSettings

# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth import logout

# core/views.py
def login_view(request):
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"Request path: {request.path}")
    print(f"Request method: {request.method}")
    
    if request.user.is_authenticated:
        print("User already logged in, redirecting to dashboard")
        return redirect('/')
    
    if request.method == 'POST':
        print("POST request received")
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username attempted: {username}")
        
        user = authenticate(request, username=username, password=password)
        print(f"Authentication result: {user}")
        
        if user:
            login(request, user)
            print("Login successful, redirecting")
            return redirect('/')
        else:
            print("Login failed")
            messages.error(request, 'Invalid credentials')
    
    print("Showing login page")
    return render(request, 'login.html')



@login_required
def main_menu(request):
    """Main menu dashboard"""
    
    # Get company settings
    settings = SystemSettings.objects.first()
    company_name = settings.company_name if settings else "St Andrews Co-Operative Credit Union"
    
    # Get user info
    user_name = request.user.get_full_name() or request.user.username
    user_role = "Administrator" if request.user.is_superuser else "Staff"
    
    context = {
        'company_name': company_name,
        'current_date': timezone.now(),
        'current_time': timezone.now().strftime('%I:%M:%S %p'),
        'current_year': timezone.now().year,
        'user_name': user_name,
        'user_role': user_role,
    }
    return render(request, 'main_menu.html', context)

@login_required
def dashboard(request):
    """Main dashboard - requires login"""
    return render(request, 'dashboard.html')


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
#    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:login')

@login_required
def profile(request):
    """User profile page"""
    return render(request, 'core/profile.html')


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})

@login_required
def profile(request):
    """User profile"""
    return render(request, 'core/profile.html')

@login_required
def change_password(request):
    """Change password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})

def password_reset(request):
    pass