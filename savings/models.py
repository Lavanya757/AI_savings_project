from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('bill', 'Bill'),
        ('budget', 'Budget'),
        ('goal', 'Goal'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    due_date = models.DateField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.message[:20]}"

class FinancialData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s income on {self.date}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('groceries', 'Groceries'),
        ('bills', 'Bills'),
        ('entertainment', 'Entertainment'),
        ('transport', 'Transport'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s savings goal: {self.target_amount}"

class SavingsPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    confidence_score = models.FloatField()

    def __str__(self):
        return f"Prediction for {self.user.username}: {self.predicted_amount}"

class Budget(models.Model):
    CATEGORY_CHOICES = Expense.CATEGORY_CHOICES

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s budget for {self.category} in {self.month.strftime('%B %Y')}"

class MonthlySavings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s savings of {self.amount} for {self.month.strftime('%B %Y')}"
