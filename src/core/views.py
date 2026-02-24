from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from core.models import Chat

User = get_user_model()


@login_required
def home_view(request, active_chat_uuid=None):
    """
    Home page:
    - Sidebar with all chats of the user
    - Button + form to create new chat
    - Right side: active chat messages if selected
    """
    # Handle "Create New Chat" form submission
    if request.method == "POST":
        participant_ids = request.POST.getlist("participants")
        is_group = len(participant_ids) > 1
        name = request.POST.get("name") if is_group else None

        # Create the chat
        chat = Chat.objects.create(name=name, is_group_chat=is_group)
        # Add current user as participant
        chat.participants.add(request.user)
        # Add selected participants
        participants = User.objects.filter(id__in=participant_ids)
        chat.participants.add(*participants)

        # Redirect to newly created chat
        return redirect("home_active_chat", active_chat_uuid=chat.uuid)

    # Get all chats where current user is participant
    chats = Chat.objects.filter(participants=request.user).order_by("-created_at")

    # Active chat (if URL has active_chat_uuid)
    active_chat = None
    if active_chat_uuid:
        active_chat = get_object_or_404(Chat, uuid=active_chat_uuid)
        if request.user not in active_chat.participants.all():
            active_chat = None  # Security check: user must be participant

    # All other users for creating chats
    users = User.objects.exclude(id=request.user.id)

    return render(
        request,
        "core/home.html",
        {
            "chats": chats,
            "users": users,
            "active_chat": active_chat,
        },
    )
