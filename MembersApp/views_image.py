# MembersApp/views.py - Add image management views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.images import ImageFile
from PIL import Image
import os
from .models import Master
from django_ledger.models import EntityModel


# MembersApp/views.py - Update member_images view

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Master

@login_required
def member_images(request, slug, pk=None):
    """Manage member images - with search first"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = None
    
    # If pk is provided, get that member
    if pk:
        member = get_object_or_404(Master, pk=pk)
    
    # Handle search
    search_query = request.GET.get('search', '')
    search_results = []
    
    if search_query:
        search_results = Master.objects.filter(
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(id__icontains=search_query)
        ).filter(is_deleted=False)[:20]
    
    # Handle POST (image upload)
    if request.method == 'POST' and member:
        # Handle image uploads
        if 'profile_image' in request.FILES:
            member.profile_image = request.FILES['profile_image']
            member.save()
            messages.success(request, "Profile image uploaded successfully!")
        
        if 'signature' in request.FILES:
            member.signature = request.FILES['signature']
            member.save()
            messages.success(request, "Signature uploaded successfully!")
        
        if 'id_card_front' in request.FILES:
            member.id_card_front = request.FILES['id_card_front']
            member.save()
            messages.success(request, "ID card front uploaded successfully!")
        
        if 'id_card_back' in request.FILES:
            member.id_card_back = request.FILES['id_card_back']
            member.save()
            messages.success(request, "ID card back uploaded successfully!")
        
        return redirect('MembersApp:member_images', pk=member.id)
    
    context = {
        'member': member,
        'search_query': search_query,
        'search_results': search_results,
    }
    return render(request, 'MembersApp/member_images.html', context)





@login_required
def view_member_images(request, slug, pk):
    """View-only display of member images (no upload/delete)"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk, is_deleted=False)
    
    context = {
        'member': member,
    }
    return render(request, 'MembersApp/view_member_images.html', context)


@login_required
def delete_image1(request, slug, pk, image_type):
    """Delete a specific image"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk)
    
    if request.method == 'POST':
        if image_type == 'profile':
            if member.profile_image:
                member.profile_image.delete()
                messages.success(request, "Profile image deleted!")
        elif image_type == 'signature':
            if member.signature:
                member.signature.delete()
                messages.success(request, "Signature deleted!")
        elif image_type == 'id_front':
            if member.id_card_front:
                member.id_card_front.delete()
                messages.success(request, "ID card front deleted!")
        elif image_type == 'id_back':
            if member.id_card_back:
                member.id_card_back.delete()
                messages.success(request, "ID card back deleted!")
        
        member.save()
    
    return redirect('MembersApp:member_images', pk=member.pk)

@login_required
def delete_member_image(request, slug, pk, image_type):
    """Delete a specific image from a member"""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Master, pk=pk, is_deleted=False)
    
    if request.method == 'POST':
        image_field = None
        image_name = ""
        
        if image_type == 'profile':
            image_field = member.profile_image
            image_name = "profile image"
        elif image_type == 'signature':
            image_field = member.signature
            image_name = "signature"
        elif image_type == 'id_front':
            image_field = member.id_card_front
            image_name = "ID card front"
        elif image_type == 'id_back':
            image_field = member.id_card_back
            image_name = "ID card back"
        
        if image_field:
            # Get the file path for logging (optional)
            file_path = image_field.path if hasattr(image_field, 'path') else None
            
            # Delete the file and clear the field
            image_field.delete()  # This deletes file AND clears field
            
            # Optional: Log the deletion
            print(f"Deleted {image_name} for member {member.full_name} (ID: {member.id})")
            if file_path:
                print(f"File deleted: {file_path}")
            
            messages.success(request, f"{image_name.capitalize()} deleted successfully!")
        else:
            messages.warning(request, f"No {image_name} found to delete")
        
        member.save()
    #    return redirect('MembersApp:member_images_view', pk=member.id)
        return redirect('MembersApp:view_member_images', pk=member.id)
#    return redirect('MembersApp:member_images_view', pk=member.id)
    return redirect('MembersApp:view_member_images', pk=member.id)