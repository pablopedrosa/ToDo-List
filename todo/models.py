from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.admin.models import User
from django.conf import settings

class DateTime(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.datetime.strftime("%d de %b, %Y, %H:%M"))


class Item(models.Model):
    name = models.CharField(max_length=60)
    created = models.ForeignKey(DateTime)
    priority = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=0)
    done = models.BooleanField(default=False)
    onhold = models.BooleanField(default=False)
    user = models.ForeignKey(User, blank=True, null=True)
    progress = models.IntegerField(default=0)

    def progress_(self):
        return """
            <div id="progress_cont_%s" class="progress_cont">
                <div id="progress_btns_%s" class="progress_btns">
                    <ul>
                        <li>10</li>
                        <li>20</li>
                        <li>30</li>
                        <li>40</li>
                        <li>50</li>
                        <li>60</li>
                        <li>70</li>
                        <li>80</li>
                        <li>90</li>
                        <li>100</li>
                    </ul>
                </div>
                <div id="progress_on_%s" class="progress_on">&nbsp;</div>
                <div id="progress_%s" style="visibility: hidden"></div>
            </div>
            """ % (self.pk, self.pk, self.pk, self.pk)
    
    progress_.allow_tags = True


    def mark_done(self):
        output = "&nbsp;<a href='%s'><img title='Delete' src='/media/img/admin/icon_deletelink.gif' alt='Delete' /></a>" % reverse("todo.views.item_action", args=["delete", self.pk]) 
        return output

    def onhold_(self):
        if self.onhold:
            btn = "<div id='onhold_%s'><img class='btn' src='%simg/admin/icon-yes.gif' /></div>"
        else:
            btn = "<div id='onhold_%s'><img class='btn' src='%simg/admin/icon-no.gif' /></div>"
        return btn % (self.pk, '/media/')
    onhold_.allow_tags = True
    onhold_.admin_order_field = "onhold"

    def done_(self):
        if self.done:
            btn = "<div id='done_%s'><img class='btn' src='%simg/admin/icon-yes.gif' /></div>"
        else:
            btn = "<div id='done_%s'><img class='btn' src='%simg/admin/icon-no.gif' /></div>"
        return btn % (self.pk, '/media/')
    done_.allow_tags = True
    done_.admin_order_field = "done"
    
    mark_done.short_description = "";
    mark_done.allow_tags = True


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "done_", "onhold_", "progress_", "priority", "difficulty", "onhold", "created", "user", "mark_done"]
    search_fields = ["name"]
    list_filter = ['priority', 'difficulty', "created", "done"]


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