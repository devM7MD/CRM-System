from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Notification(models.Model):
    """Notification model for user notifications."""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    # Optional link to related object
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, 
                                    null=True, blank=True, verbose_name=_('Content Type'))
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Object ID'))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        
    def __str__(self):
        return self.title
        
    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
        
    @property
    def timestamp(self):
        """Return the created_at timestamp for template compatibility."""
        return self.created_at
