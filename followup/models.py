# followup/models.py
from django.db import models

class FollowupRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='followups')
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class CustomerFeedback(models.Model):
    RATING_CHOICES = (
        (1, '1 - Very Dissatisfied'),
        (2, '2 - Dissatisfied'),
        (3, '3 - Neutral'),
        (4, '4 - Satisfied'),
        (5, '5 - Very Satisfied'),
    )
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)