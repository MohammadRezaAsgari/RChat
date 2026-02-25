from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from core.models import Chat

User = get_user_model()


@login_required
def home_view(request, active_chat_uuid=None):

    if request.method == "POST":
        username = request.POST.get("username")

        if not username:
            messages.error(request, "Please enter a username.")
            return redirect("home")

        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("home")

        if other_user == request.user:
            messages.error(request, "You cannot chat with yourself.")
            return redirect("home")

        # Check if chat already exists
        existing_chat = (
            Chat.objects.filter(participants=request.user)
            .filter(participants=other_user, is_group_chat=False)
            .first()
        )

        if existing_chat:
            return redirect("home_active_chat", active_chat_uuid=existing_chat.uuid)

        # Create new private chat
        chat = Chat.objects.create(is_group_chat=False)
        chat.participants.add(request.user, other_user)

        return redirect("home_active_chat", active_chat_uuid=chat.uuid)

    chats = Chat.objects.filter(participants=request.user).order_by("-created_at")

    active_chat = None
    if active_chat_uuid:
        active_chat = get_object_or_404(Chat, uuid=active_chat_uuid)
        if request.user not in active_chat.participants.all():
            active_chat = None

    return render(
        request,
        "core/home.html",
        {
            "chats": chats,
            "active_chat": active_chat,
        },
    )
