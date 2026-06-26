
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Message

def CreateRoom(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        room = request.POST.get('room', '').strip()

        if not username or not room:
            return render(request, 'index.html', {'error': 'Username and room required.'})

        room_obj, created = Room.objects.get_or_create(room_name=room)
        # redirect to room view (ensure urls name and args match)
        return redirect('room', room_name=room_obj.room_name, username=username)

    # render index page 
    return render(request, 'index.html')


def MessageView(request, room_name, username):
    # ensure room exists or 404
    get_room = get_object_or_404(Room, room_name=room_name)

    # POST fallback (works if you have a non-WS form)
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            # save message synchronously (HTTP path)
            Message.objects.create(room=get_room, sender=username, message=message_text)

    # fetch messages for display
    get_messages = Message.objects.filter(room=get_room).order_by('timestamp')

    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
    }
    # render the chat page
    return render(request, 'message.html', context)
