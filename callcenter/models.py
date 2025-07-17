# callcenter/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class CallCenterAgent(models.Model):
    """Call center agent profile"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('on_leave', 'On Leave'),
    )
    
    AVAILABILITY_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('break', 'On Break'),
        ('offline', 'Offline'),
        ('training', 'In Training'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='call_center_profile')
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="Employee ID")
    phone_extension = models.CharField(max_length=10, blank=True, verbose_name="Phone Extension")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='offline', verbose_name="Availability")
    max_concurrent_orders = models.PositiveIntegerField(default=5, verbose_name="Max Concurrent Orders")
    current_orders_count = models.PositiveIntegerField(default=0, verbose_name="Current Orders Count")
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_agents', verbose_name="Supervisor")
    team = models.CharField(max_length=100, blank=True, verbose_name="Team")
    skills = models.JSONField(default=list, verbose_name="Skills")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Call Center Agent"
        verbose_name_plural = "Call Center Agents"
        ordering = ['user__full_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

    def get_performance_today(self):
        """Get today's performance metrics"""
        today = timezone.now().date()
        return AgentPerformance.objects.filter(agent=self.user, date=today).first()

class AgentSession(models.Model):
    """Track agent login sessions"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('break', 'Break'),
        ('offline', 'Offline'),
    )
    
    agent = models.ForeignKey(CallCenterAgent, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField(default=timezone.now, verbose_name="Login Time")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Logout Time")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    workstation_id = models.CharField(max_length=50, blank=True, verbose_name="Workstation ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Last Activity")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Agent Session"
        verbose_name_plural = "Agent Sessions"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.agent.user.get_full_name()} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"

    def get_session_duration(self):
        """Calculate session duration"""
        end_time = self.logout_time or timezone.now()
        return end_time - self.login_time

class CallLog(models.Model):
    """Enhanced call log with comprehensive tracking"""
    CALL_STATUS = (
        ('completed', 'Completed'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('wrong_number', 'Wrong Number'),
        ('voicemail', 'Voicemail'),
        ('call_back', 'Call Back Requested'),
        ('escalated', 'Escalated'),
    )
    
    RESOLUTION_STATUS = (
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
        ('escalated', 'Escalated'),
        ('follow_up_required', 'Follow Up Required'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='call_logs')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_logs')
    call_time = models.DateTimeField(default=timezone.now, verbose_name="Call Time")
    duration = models.PositiveIntegerField(default=0, verbose_name="Duration (seconds)")
    status = models.CharField(max_length=20, choices=CALL_STATUS, verbose_name="Call Status")
    resolution_status = models.CharField(max_length=20, choices=RESOLUTION_STATUS, default='pending', verbose_name="Resolution Status")
    notes = models.TextField(blank=True, verbose_name="Call Notes")
    customer_satisfaction = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Customer Satisfaction")
    follow_up_date = models.DateTimeField(null=True, blank=True, verbose_name="Follow Up Date")
    escalation_reason = models.TextField(blank=True, verbose_name="Escalation Reason")
    call_recording_url = models.URLField(blank=True, verbose_name="Call Recording URL")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Call Log"
        verbose_name_plural = "Call Logs"
        ordering = ['-call_time']

    def __str__(self):
        return f"Call {self.order.order_number} - {self.agent.get_full_name()} - {self.call_time.strftime('%Y-%m-%d %H:%M')}"

    def get_duration_formatted(self):
        """Get formatted duration"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

class CustomerInteraction(models.Model):
    """Track all customer interactions"""
    INTERACTION_TYPE = (
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('chat', 'Live Chat'),
        ('follow_up', 'Follow Up'),
        ('escalation', 'Escalation'),
    )
    
    RESOLUTION_STATUS = (
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
        ('escalated', 'Escalated'),
        ('follow_up_required', 'Follow Up Required'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='customer_interactions')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE, verbose_name="Interaction Type")
    interaction_time = models.DateTimeField(default=timezone.now, verbose_name="Interaction Time")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="Duration (minutes)")
    resolution_status = models.CharField(max_length=20, choices=RESOLUTION_STATUS, default='pending', verbose_name="Resolution Status")
    interaction_notes = models.TextField(blank=True, verbose_name="Interaction Notes")
    customer_satisfaction = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Customer Satisfaction")
    follow_up_date = models.DateTimeField(null=True, blank=True, verbose_name="Follow Up Date")
    escalation_reason = models.TextField(blank=True, verbose_name="Escalation Reason")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Customer Interaction"
        verbose_name_plural = "Customer Interactions"
        ordering = ['-interaction_time']

    def __str__(self):
        return f"{self.interaction_type.title()} - {self.order.order_number} - {self.agent.get_full_name()}"

class OrderAssignment(models.Model):
    """Track order assignments to agents"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='call_center_assignments')
    assigned_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_orders')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_assignments_made', related_query_name='assignment_made')
    assignment_date = models.DateTimeField(default=timezone.now, verbose_name="Assignment Date")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Priority")
    expected_completion = models.DateTimeField(null=True, blank=True, verbose_name="Expected Completion")
    assignment_notes = models.TextField(blank=True, verbose_name="Assignment Notes")
    is_active = models.BooleanField(default=True, verbose_name="Active Assignment")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order Assignment"
        verbose_name_plural = "Order Assignments"
        ordering = ['-assignment_date']

    def __str__(self):
        return f"{self.order.order_number} - {self.assigned_agent.get_full_name()}"

class ManagerNote(models.Model):
    """Notes from managers to agents"""
    NOTE_TYPE = (
        ('instruction', 'Instruction'),
        ('reminder', 'Reminder'),
        ('priority', 'Priority'),
        ('escalation', 'Escalation'),
        ('feedback', 'Feedback'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='manager_notes')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_created')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_received')
    note_text = models.TextField(verbose_name="Note Text")
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE, default='instruction', verbose_name="Note Type")
    is_urgent = models.BooleanField(default=False, verbose_name="Urgent")
    is_read_by_agent = models.BooleanField(default=False, verbose_name="Read by Agent")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Read At")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manager Note"
        verbose_name_plural = "Manager Notes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Note from {self.manager.get_full_name()} to {self.agent.get_full_name()}"

class OrderStatusHistory(models.Model):
    """Track order status changes by agents"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='status_history')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_changes')
    previous_status = models.CharField(max_length=50, verbose_name="Previous Status")
    new_status = models.CharField(max_length=50, verbose_name="New Status")
    status_change_reason = models.TextField(blank=True, verbose_name="Status Change Reason")
    cancellation_reason = models.TextField(blank=True, verbose_name="Cancellation Reason")
    change_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Change Timestamp")
    customer_notified = models.BooleanField(default=False, verbose_name="Customer Notified")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"
        ordering = ['-change_timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.previous_status} → {self.new_status}"

class AgentPerformance(models.Model):
    """Enhanced agent performance metrics"""
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_records')
    date = models.DateField(verbose_name="Date")
    total_orders_handled = models.PositiveIntegerField(default=0, verbose_name="Total Orders Handled")
    orders_confirmed = models.PositiveIntegerField(default=0, verbose_name="Orders Confirmed")
    orders_cancelled = models.PositiveIntegerField(default=0, verbose_name="Orders Cancelled")
    orders_postponed = models.PositiveIntegerField(default=0, verbose_name="Orders Postponed")
    total_calls_made = models.PositiveIntegerField(default=0, verbose_name="Total Calls Made")
    successful_calls = models.PositiveIntegerField(default=0, verbose_name="Successful Calls")
    average_call_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Average Call Duration (minutes)")
    customer_satisfaction_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="Average Customer Satisfaction")
    resolution_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Resolution Rate (%)")
    first_call_resolution_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="First Call Resolution Rate (%)")
    total_work_time_minutes = models.PositiveIntegerField(default=0, verbose_name="Total Work Time (minutes)")
    break_time_minutes = models.PositiveIntegerField(default=0, verbose_name="Break Time (minutes)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent Performance"
        verbose_name_plural = "Agent Performances"
        unique_together = ('agent', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.agent.get_full_name()} - {self.date}"

    def get_confirmation_rate(self):
        """Calculate confirmation rate"""
        if self.total_orders_handled == 0:
            return 0
        return (self.orders_confirmed / self.total_orders_handled) * 100

    def get_cancellation_rate(self):
        """Calculate cancellation rate"""
        if self.total_orders_handled == 0:
            return 0
        return (self.orders_cancelled / self.total_orders_handled) * 100

class TeamPerformance(models.Model):
    """Team performance metrics"""
    team_name = models.CharField(max_length=100, verbose_name="Team Name")
    date = models.DateField(verbose_name="Date")
    total_agents = models.PositiveIntegerField(default=0, verbose_name="Total Agents")
    active_agents = models.PositiveIntegerField(default=0, verbose_name="Active Agents")
    total_orders_handled = models.PositiveIntegerField(default=0, verbose_name="Total Orders Handled")
    orders_confirmed = models.PositiveIntegerField(default=0, verbose_name="Orders Confirmed")
    orders_cancelled = models.PositiveIntegerField(default=0, verbose_name="Orders Cancelled")
    average_handle_time = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Average Handle Time (minutes)")
    team_confirmation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Team Confirmation Rate (%)")
    team_satisfaction_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Team Satisfaction Average")
    top_performer_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='top_performer_records', verbose_name="Top Performer")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Team Performance"
        verbose_name_plural = "Team Performances"
        unique_together = ('team_name', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.team_name} - {self.date}"