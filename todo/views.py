from django.http import HttpResponseRedirect
from todo.models import *

def item_action(request, action, pk):
    """Mark done, toggle onhold or delete a todo item."""
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
    """Toggle Done / Onhold on/off."""
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
    """Set task progress."""
    p = request.POST
    if "progress" in p:
        item = Item.objects.get(pk=pk)
        item.progress = int(p["progress"])
        item.save()
    return HttpResponse('')
