from django.shortcuts import render

# Create your views here.
# LoginApp/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import MemberLoginHistory, AdminLoginHistory
from MembersApp.models import Master

@staff_member_required
def member_login_history(request, member_id=None):
    """View login history for members"""
    
    if member_id:
        member = get_object_or_404(Master, pk=member_id)
        login_history = member.login_history.all()
        title = f"Login History - {member.full_name}"
    else:
        member = None
        login_history = MemberLoginHistory.objects.select_related('member').all()
        title = "All Member Login History"
    
    # Filters
    status = request.GET.get('status')
    if status:
        login_history = login_history.filter(login_status=status)
    
    date_from = request.GET.get('date_from')
    if date_from:
        login_history = login_history.filter(login_time__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        date_to_end = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        login_history = login_history.filter(login_time__lte=date_to_end)
    
    device = request.GET.get('device')
    if device:
        login_history = login_history.filter(device_type=device)
    
    search = request.GET.get('search')
    if search:
        login_history = login_history.filter(
            Q(member__full_name__icontains=search) |
            Q(member__member_id__icontains=search) |
            Q(ip_address__icontains=search)
        )
    
    # Statistics
    stats = {
        'total': login_history.count(),
        'successful': login_history.filter(login_status='SUCCESS').count(),
        'failed': login_history.filter(login_status='FAILED').count(),
        'unique_members': login_history.values('member').distinct().count(),
        'today': login_history.filter(login_time__date=timezone.now().date()).count(),
    }
    
    # Pagination
    paginator = Paginator(login_history.order_by('-login_time'), 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'login_history': page_obj,
        'member': member,
        'title': title,
        'stats': stats,
        'status_choices': MemberLoginHistory.LOGIN_STATUS,
        'device_choices': [('Mobile', 'Mobile'), ('Desktop', 'Desktop'), ('Tablet', 'Tablet')],
    }
    return render(request, 'LoginApp/member_login_history.html', context)


@staff_member_required
def admin_login_history(request):
    """View admin/staff login history"""
    
    login_history = AdminLoginHistory.objects.select_related('user').all()
    
    # Filters
    status = request.GET.get('status')
    if status:
        login_history = login_history.filter(login_status=status)
    
    date_from = request.GET.get('date_from')
    if date_from:
        login_history = login_history.filter(login_time__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        date_to_end = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        login_history = login_history.filter(login_time__lte=date_to_end)
    
    search = request.GET.get('search')
    if search:
        login_history = login_history.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(ip_address__icontains=search)
        )
    
    # Statistics
    stats = {
        'total': login_history.count(),
        'successful': login_history.filter(login_status='SUCCESS').count(),
        'failed': login_history.filter(login_status='FAILED').count(),
        'unique_users': login_history.values('user').distinct().count(),
        'today': login_history.filter(login_time__date=timezone.now().date()).count(),
    }
    
    # Pagination
    paginator = Paginator(login_history.order_by('-login_time'), 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'login_history': page_obj,
        'title': 'Admin Login History',
        'stats': stats,
        'status_choices': AdminLoginHistory.LOGIN_STATUS,
    }
    return render(request, 'LoginApp/admin_login_history.html', context)


@staff_member_required
def login_dashboard(request):
    """Login history dashboard"""
    
    # Member stats
    member_stats = {
        'total': MemberLoginHistory.objects.count(),
        'today': MemberLoginHistory.objects.filter(login_time__date=timezone.now().date()).count(),
        'failed': MemberLoginHistory.objects.filter(login_status='FAILED').count(),
        'unique': MemberLoginHistory.objects.values('member').distinct().count(),
    }
    
    # Admin stats
    admin_stats = {
        'total': AdminLoginHistory.objects.count(),
        'today': AdminLoginHistory.objects.filter(login_time__date=timezone.now().date()).count(),
        'failed': AdminLoginHistory.objects.filter(login_status='FAILED').count(),
        'unique': AdminLoginHistory.objects.values('user').distinct().count(),
    }
    
    # Recent logins
    recent_member_logins = MemberLoginHistory.objects.select_related('member').all()[:10]
    recent_admin_logins = AdminLoginHistory.objects.select_related('user').all()[:10]
    
    context = {
        'member_stats': member_stats,
        'admin_stats': admin_stats,
        'recent_member_logins': recent_member_logins,
        'recent_admin_logins': recent_admin_logins,
        'today': timezone.now(),
    }
    return render(request, 'LoginApp/login_dashboard.html', context)

from LoginApp.models import MemberLoginHistory
from django.utils import timezone


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from MembersApp.models import Master

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def member_login(request):
    """Custom login view for members (using Master model)"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Attempt to find member by username (or email, or member ID)
        try:
            # Adjust the lookup to match your Member model's identifier field
            # For example, using `member_id` or `email_address` or `username` field.
            # I'll assume you have a unique `member_number` field.
            from django.db.models import Q
            member = Master.objects.filter(
                Q(member_id=username) | Q(email_address=username)
            ).first()
        except Master.DoesNotExist:
            member = None

        # Verify password (assuming you have a password field in Master)
        if member and member.check_password(password):  # You need a `check_password` method on Master
            # Record successful login
            MemberLoginHistory.objects.create(
                member=member,
                username_attempted=username,
                login_time=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                login_status='SUCCESS',
            )
            request.session['member_id'] = member.id
            messages.success(request, f"Welcome back, {member.full_name}!")
            return redirect('member_dashboard')  # change to your member dashboard URL
        else:
            # Record failed login attempt
            MemberLoginHistory.objects.create(
                member=None,
                username_attempted=username,
                login_time=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                login_status='FAILED',
                failure_reason='Invalid username or password',
            )
            messages.error(request, "Invalid login credentials.")
            return redirect('member_login')

    # GET request – show login form
    return render(request, 'LoginApp/member_login.html')

