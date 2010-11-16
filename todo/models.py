from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.admin.models import User

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

    def __unicode__(self):
        return unicode(self.name)

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

