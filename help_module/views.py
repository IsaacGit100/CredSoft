from django.shortcuts import render

# Create your views here.
# help_module/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import HelpCategory, HelpTopic, HelpArticle, HelpSearch, HelpFeedback, UserGuide

@login_required
def help_dashboard(request):
    """Main help dashboard"""
    categories = HelpCategory.objects.filter(is_active=True)
    featured_topics = HelpTopic.objects.filter(is_featured=True, is_active=True)[:6]
    popular_topics = HelpTopic.objects.filter(is_active=True).order_by('-views_count')[:5]
    recent_guides = UserGuide.objects.filter(is_published=True).order_by('-published_date')[:3]
    
    context = {
        'categories': categories,
        'featured_topics': featured_topics,
        'popular_topics': popular_topics,
        'recent_guides': recent_guides,
    }
    return render(request, 'help_module/dashboard.html', context)

@login_required
def help_search(request):
    """Search help content"""
    query = request.GET.get('q', '')
    
    if query:
        # Save search for analytics
        HelpSearch.objects.create(
            search_term=query,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Search in topics
        topics = HelpTopic.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(keywords__icontains=query)
        ).filter(is_active=True)
        
        # Search in articles
        articles = HelpArticle.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
        
        # Search in user guides
        guides = UserGuide.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        ).filter(is_published=True)
        
        # Combine results
        results = list(topics) + list(articles) + list(guides)
        
        # Update results count
        search = HelpSearch.objects.latest('search_date')
        search.results_count = len(results)
        search.save()
        
        context = {
            'query': query,
            'topics': topics,
            'articles': articles,
            'guides': guides,
            'total_results': len(results),
        }
    else:
        context = {
            'query': '',
            'topics': [],
            'articles': [],
            'guides': [],
            'total_results': 0,
        }
    
    return render(request, 'help_module/search_results.html', context)

@login_required
def help_category(request, category_slug):
    """View help by category"""
    category = get_object_or_404(HelpCategory, slug=category_slug, is_active=True)
    topics = category.topics.filter(is_active=True)
    
    # Filter by module if specified
    module = request.GET.get('module')
    if module:
        topics = topics.filter(module_name=module)
    
    paginator = Paginator(topics, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'module': module,
    }
    return render(request, 'help_module/category.html', context)

@login_required
def help_topic(request, topic_slug):
    """View help topic details"""
    topic = get_object_or_404(HelpTopic, slug=topic_slug, is_active=True)
    
    # Increment view count
    topic.views_count += 1
    topic.save()
    
    # Get related topics (same module or category)
    related_topics = HelpTopic.objects.filter(
        Q(module_name=topic.module_name) | Q(category=topic.category)
    ).exclude(id=topic.id).filter(is_active=True)[:5]
    
    context = {
        'topic': topic,
        'articles': topic.articles.all(),
        'related_topics': related_topics,
    }
    return render(request, 'help_module/topic.html', context)

@login_required
def module_help(request, module_name):
    """Get help specific to a module"""
    module_display = dict(HelpTopic._meta.get_field('module_name').choices).get(module_name, module_name)
    
    topics = HelpTopic.objects.filter(
        module_name=module_name,
        is_active=True
    )
    
    # Get quick start guide for this module
    quick_start = topics.filter(help_type='HOW_TO').first()
    
    # Get FAQs for this module
    faqs = topics.filter(help_type='FAQ')[:5]
    
    # Get user guides for this module
    guides = UserGuide.objects.filter(module_name=module_name, is_published=True)
    
    context = {
        'module_name': module_name,
        'module_display': module_display,
        'topics': topics,
        'quick_start': quick_start,
        'faqs': faqs,
        'guides': guides,
    }
    return render(request, 'help_module/module_help.html', context)

@login_required
def user_guide_detail(request, guide_slug):
    """View user guide"""
    guide = get_object_or_404(UserGuide, slug=guide_slug, is_published=True)
    
    context = {
        'guide': guide,
    }
    return render(request, 'help_module/user_guide.html', context)

@login_required
@require_POST
def help_feedback(request, topic_id):
    """Submit feedback on help topic"""
    topic = get_object_or_404(HelpTopic, id=topic_id)
    was_helpful = request.POST.get('was_helpful') == 'true'
    
    if was_helpful:
        topic.helpful_count += 1
    else:
        topic.not_helpful_count += 1
    topic.save()
    
    HelpFeedback.objects.create(
        help_topic=topic,
        user=request.user,
        was_helpful=was_helpful,
        comment=request.POST.get('comment', '')
    )
    
    return JsonResponse({'success': True})

@login_required
def help_contextual(request):
    """Get contextual help based on current page"""
    page = request.GET.get('page', '')
    section = request.GET.get('section', '')
    
    # Map page to help topic
    help_map = {
        'system_setup': 'SYSTEM_SETUP',
        'users': 'USERS',
        'members': 'MEMBERS',
        'chart_of_accounts': 'CHART_OF_ACCOUNTS',
        'loans': 'LOANS',
        'receipts_payments': 'RECEIPTS_PAYMENTS',
        'finance': 'FINANCE',
        'investments': 'INVESTMENTS',
    }
    
    module = help_map.get(page, '')
    
    if module:
        topic = HelpTopic.objects.filter(
            module_name=module,
            help_type='HOW_TO',
            is_active=True
        ).first()
        
        if topic:
            return JsonResponse({
                'title': topic.title,
                'content': topic.content[:500],
                'url': f'/help/topic/{topic.slug}/'
            })
    
    return JsonResponse({'error': 'No help available for this page'})