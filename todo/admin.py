from django.contrib import admin
from django.template.defaultfilters import escape
from dbe.todo.models import *


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "done_", "onhold_", "progress_", "priority", "difficulty", "onhold", "mark_done"]
    search_fields = ["name"]
    list_filter = ['priority', 'difficulty', "done"]

    def queryset(self, request):
        if request.user.is_superuser:
            return Item.objects.all()
        return Item.objects.filter(user=request.user)
            
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(ItemAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
            return False
        return True


class ItemInline(admin.TabularInline):
    model = Item


class DateAdmin(admin.ModelAdmin):
    list_display = ["datetime"]
    inlines = [ItemInline]

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """ Determines the HttpResponse for the add_view stage.  """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        msg = "Item(s) were added successfully."
        
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if request.POST.has_key("_continue"):
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if request.POST.has_key("_popup"):
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % pk_value)
              
        if request.POST.has_key("_popup"):
            return HttpResponse(
              '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");'
              '</script>' % (escape(pk_value), escape(obj)))
        elif request.POST.has_key("_addanother"):
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") %
                                                    force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            for item in Item.objects.filter(created=obj):
                if not item.user:
                    item.user = request.user
                    item.save()
            return HttpResponseRedirect(reverse("admin:todo_item_changelist"))
    

admin.site.register(Item, ItemAdmin)
admin.site.register(DateTime, DateAdmin)