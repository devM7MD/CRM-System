# callcenter/models.py
from django.db import models

class CallLog(models.Model):
    CALL_STATUS = (
        ('completed', 'Completed'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('wrong_number', 'Wrong Number'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='call_logs')
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE)
    call_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # in seconds
    status = models.CharField(max_length=20, choices=CALL_STATUS)
    notes = models.TextField(blank=True)

class AgentPerformance(models.Model):
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField()
    calls_made = models.IntegerField(default=0)
    successful_confirmations = models.IntegerField(default=0)
    average_call_duration = models.IntegerField(default=0)  # in seconds
    
    class Meta:
        unique_together = ('agent', 'date')