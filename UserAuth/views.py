from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render

# Create your views here.

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from .models import UserProfile

def access_home(request):
    return render(request, 'access_home.html')

# UserAuth/views.py - Add this view
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """Main dashboard after login"""
    user = request.user
    role = user.profile.role if hasattr(user, 'profile') else 'VIEWER'
    
    # Get role display name
    role_display = dict(user.profile.USER_ROLES).get(role, 'View Only')
    
    context = {
        'user': user,
        'role': role,
        'role_display': role_display,
        'is_admin': user.is_superuser or role == 'ADMIN',
        'is_manager': role in ['MANAGER', 'ADMIN'],
        'is_cashier': role in ['CASHIER', 'MANAGER', 'ADMIN'],
        'is_loan_officer': role in ['LOAN_OFFICER', 'MANAGER', 'ADMIN'],
        'is_auditor': role in ['AUDITOR', 'MANAGER', 'ADMIN'],
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def user_profile(request):
    """View and edit own profile"""
    user = request.user
    
    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        profile = user.profile
        profile.phone = request.POST.get('phone', '')
        profile.theme = request.POST.get('theme', 'light')
        profile.items_per_page = int(request.POST.get('items_per_page', 50))
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('userauth:user_profile')
    
    return render(request, 'userauth/profile.html', {'user': user})

@login_required
def change_password(request):
    """Change user's own password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Check old password
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('userauth:change_password')
        
        # Check new passwords match
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('userauth:change_password')
        
        # Check password length
        if len(new_password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:change_password')
        
        # Set new password
        request.user.set_password(new_password1)
        request.user.save()
        
        # Keep user logged in
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Password changed successfully!")
        return redirect('userauth:user_profile')
    
    return render(request, 'userauth/change_password.html')

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_list(request):
    """List all users with search"""
    query = request.GET.get('q', '')
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('username')
    else:
        users = User.objects.all().order_by('username')
    
    return render(request, 'userauth/user_list.html', {
        'users': users,
        'query': query,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
    })

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)

def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        employee_id = request.POST.get('employee_id')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('userauth:user_create')
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('userauth:user_create')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:user_create')
        
        if employee_id and UserProfile.objects.filter(employee_id=employee_id).exists():
            messages.error(request, f"Employee ID '{employee_id}' already exists.")
            return redirect('userauth:user_create')
        
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        # Check if profile already exists
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if not created:
            messages.warning(request, f"User created but profile already existed.")
        else:
            # Update profile fields
            profile.role = role
            profile.phone = phone
            profile.save()
         
        messages.success(request, f"User '{username}' created successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'userauth/user_form.html', {
        'roles': UserProfile.USER_ROLES,
        'is_create': True
    })


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(User, pk=pk)
    return render(request, 'userauth/user_detail.html', {'user': user})

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_edit(request, pk):
    """Edit user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Update user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        # Update profile
        profile = user.profile
        profile.role = request.POST.get('role')
        profile.phone = request.POST.get('phone', '')
        profile.employee_id = request.POST.get('employee_id', '')
        profile.save()
        
        messages.success(request, f"User '{user.username}' updated successfully!")
        return redirect('user_list')
    
    return render(request, 'userauth/user_form.html', {
        'user': user,
        'roles': UserProfile.USER_ROLES,
        'is_create': False
    })

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow deleting yourself
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('userauth:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully!")
        return redirect('user_list')
    
    return render(request, 'userauth/user_confirm_delete.html', {'user': user})

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_toggle_status(request, pk):
    """Activate/Deactivate user"""
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow deactivating yourself
    if user == request.user:
        messages.error(request, "You cannot change your own status.")
        return redirect('userauth:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User '{user.username}' {status} successfully!")
    return redirect('userauth:user_list')

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_reset_password(request, pk):
    """Reset user's password"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user_reset_password', pk=user.id)
        
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('user_reset_password', pk=user.id)
        
        user.set_password(new_password)
        user.save()
        
        messages.success(request, f"Password for '{user.username}' reset successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'userauth/user_reset_password.html', {'user': user})


# UserAuth/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import random
import string
from .models import UserProfile


def is_superuser(user):
    return user.is_superuser


@login_required
def user_profile(request):
    """View and edit own profile"""
    user = request.user
    
    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.phone = request.POST.get('phone', '')
            profile.theme = request.POST.get('theme', 'light')
            profile.items_per_page = int(request.POST.get('items_per_page', 50))
            profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('userauth:user_profile')
    
    return render(request, 'users/profile.html', {'user': user})


@login_required
def change_password(request):
    """Change user's own password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Check old password
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('userauth:change_password')
        
        # Check new passwords match
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('userauth:change_password')
        
        # Check password length
        if len(new_password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:change_password')
        
        # Set new password
        request.user.set_password(new_password1)
        request.user.save()
        
        # Keep user logged in
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Password changed successfully!")
        return redirect('userauth:user_profile')
    
    return render(request, 'userauth/change_password.html')


# ============= PASSWORD RESET VIEWS =============
@login_required
def password_reset_request(request):
    """Request password reset"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate a random token
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            # Store token in session (or you could use Django's built-in PasswordResetTokenGenerator)
            request.session['reset_token'] = token
            request.session['reset_user_id'] = user.id
            
            # Send email (in development, just print to console)
            reset_url = request.build_absolute_uri(
                f"/reset-password/confirm/{user.id}/{token}/"
            )
            
            # In production, send actual email
            # send_mail(
            #     'Password Reset Request',
            #     f'Click the link to reset your password: {reset_url}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )
            
            # For development, print to console
            print(f"Password reset link: {reset_url}")
            
            messages.success(request, "Password reset instructions have been sent to your email.")
            return redirect('userauth:password_reset_done')
            
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
            return redirect('userauth:password_reset')
    
    return render(request, 'userauth/password_reset.html')

@login_required
def password_reset_confirm(request, user_id, token):
    """Confirm password reset and set new password"""
    # Verify token (simple session check - use better method in production)
    if request.session.get('reset_token') != token or request.session.get('reset_user_id') != user_id:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('userauth:password_reset')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        password1 = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('userauth:password_reset_confirm', user_id=user_id, token=token)
        
        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:password_reset_confirm', user_id=user_id, token=token)
        
        # Set new password
        user.set_password(password1)
        user.save()
        
        # Clear session
        del request.session['reset_token']
        del request.session['reset_user_id']
        
        messages.success(request, "Password reset successful! You can now log in.")
        return redirect('userauth:login')
    
    return render(request, 'users/password_reset_confirm.html', {'user': user})

@login_required
def password_reset_done(request):
    """Password reset email sent confirmation"""
    return render(request, 'users/password_reset_done.html')

@login_required
def password_reset_complete(request):
    """Password reset complete confirmation"""
    return render(request, 'users/password_reset_complete.html')


# ============= USER MANAGEMENT VIEWS =============

@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_list(request):
    """List all users with search"""
    query = request.GET.get('q', '')
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('username')
    else:
        users = User.objects.all().order_by('username')
    
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    
    return render(request, 'users/user_list.html', {
        'users': users,
        'query': query,
        'total_users': total_users,
        'active_users': active_users,
    })


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('userauth:user_create')
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('userauth:user_create')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:user_create')
        
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.phone = phone
        profile.save()
        
        messages.success(request, f"User '{username}' created successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'users/user_form.html', {
        'roles': UserProfile.USER_ROLES,
        'is_create': True
    })


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(User, pk=pk)
    return render(request, 'users/user_detail.html', {'user': user})


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_edit(request, pk):
    """Edit user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Update user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        # Update profile
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.role = request.POST.get('role')
            profile.phone = request.POST.get('phone', '')
            profile.save()
        else:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(
                user=user,
                role=request.POST.get('role'),
                phone=request.POST.get('phone', '')
            )
        
        messages.success(request, f"User '{user.username}' updated successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'users/user_form.html', {
        'user': user,
        'roles': UserProfile.USER_ROLES,
        'is_create': False
    })


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow deleting yourself
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('userauth:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'users/user_confirm_delete.html', {'user': user})


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_toggle_status(request, pk):
    """Activate/Deactivate user"""
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow deactivating yourself
    if user == request.user:
        messages.error(request, "You cannot change your own status.")
        return redirect('userauth:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User '{user.username}' {status} successfully!")
    return redirect('userauth:user_list')


@login_required
@permission_required('auth.can_manage_users', raise_exception=True)
def user_reset_password(request, pk):
    """Reset user's password"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('userauth:user_reset_password', pk=user.id)
        
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('userauth:user_reset_password', pk=user.id)
        
        user.set_password(new_password)
        user.save()
        
        messages.success(request, f"Password for '{user.username}' reset successfully!")
        return redirect('userauth:user_list')
    
    return render(request, 'users/user_reset_password.html', {'user': user})


from django.contrib.auth import login as auth_login

@login_required
def custom_login(request):
    if request.method == 'POST':
        # ... authenticate ...
        if user is not None:
            # Ensure profile exists before login
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
            auth_login(request, user)
            return redirect('dashboard')

@login_required
def custom_logout(request):
    """Custom logout that clears session and redirects"""
    # Log the user out
    logout(request)
    
    # Clear all session data
    request.session.flush()
    
    # Add a message
    messages.success(request, "You have been successfully logged out.")
    
    # Redirect to login page
    return redirect('userauth:login')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('userauth:password_change_done')


# UserAuth/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomPasswordChangeForm


@login_required
def change_password(request):
    """
    Allow users to change their password.
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session so user doesn't get logged out
            update_session_auth_hash(request, user)
            messages.success(request, " Your password has been changed successfully!")
            return redirect("userauth:change_password")
        else:
            messages.error(request, " Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    context = {
        "form": form,
        "title": "Change Password",
    }
    return render(request, "users/change_password.html", context)


# UserAuth/views.py (or any app you prefer)

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required
def logout_view(request):
    """
    Log out the user and redirect to login page.
    """
    logout(request)
    messages.success(request, " You have been logged out successfully.")
    return redirect("userauth:login")  # or redirect to your login page


# UserAuth/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required
def logout_confirm(request):
    """
    Show logout confirmation page.
    """
    if request.method == "POST":
        logout(request)
        messages.success(request, " You have been logged out successfully.")
        return redirect("userauth:login")

    return render(request, "userauth/logout_confirm.html")
