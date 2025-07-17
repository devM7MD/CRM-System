from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class BugReport(models.Model):
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Bug Title'))
    description = models.TextField(verbose_name=_('Bug Description'))
    reporter = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('Reporter'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_('Status'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('Priority'))
    page_url = models.URLField(blank=True, verbose_name=_('Page URL'))
    browser_info = models.CharField(max_length=500, blank=True, verbose_name=_('Browser Information'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    discord_message_id = models.CharField(max_length=100, blank=True, verbose_name=_('Discord Message ID'))

    class Meta:
        verbose_name = _('Bug Report')
        verbose_name_plural = _('Bug Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.reporter.get_full_name()}"

class BugReportImage(models.Model):
    bug_report = models.ForeignKey(BugReport, on_delete=models.CASCADE, related_name='images', verbose_name=_('Bug Report'))
    image = models.ImageField(upload_to='bug_reports/', verbose_name=_('Image'))
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name=_('Uploaded At'))

    class Meta:
        verbose_name = _('Bug Report Image')
        verbose_name_plural = _('Bug Report Images')

    def __str__(self):
        return f"Image for {self.bug_report.title}"
