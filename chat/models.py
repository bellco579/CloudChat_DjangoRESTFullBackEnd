from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
import datetime

from django.core.cache import cache



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    resiver = GenericForeignKey('content_type', 'object_id')
    message = models.CharField(max_length=1200)

    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    def __str__(self):
        return "%s, %s" % (self.message, self.resiver)

    class Meta:
        ordering = ('timestamp',)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    message = GenericRelation(Message, related_query_name="Private")

    def __str__(self):
        return self.user.username

    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UsersProfiles"

class Room(models.Model):

    name = models.CharField(max_length=100)
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    invited = models.ManyToManyField(User, verbose_name="members", related_name="invited_user")
    date = models.DateTimeField("Дата создания", auto_now_add=True)

    message = GenericRelation(Message, related_query_name="Group")

    def __str__(self):
        return "%s, %s, %s, %s " % (self.name, self.message, self.invited, self.creater)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
