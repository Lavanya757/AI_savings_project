from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import FinancialData, Expense, SavingsGoal, SavingsPrediction, Budget, MonthlySavings
from .ml_predictor import SavingsPredictor
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import json
from django.db.models.functions import TruncMonth
from django.db.models import Sum

@login_required
def dashboard(request):
    financial_data = FinancialData.objects.filter(user=request.user).last()
    expenses = Expense.objects.filter(user=request.user)
    savings_goal = SavingsGoal.objects.filter(user=request.user).last()
    
    predictor = SavingsPredictor()
    
    if financial_data:
        predicted_savings = predictor.predict_savings(financial_data, expenses)
        spending_patterns_dict = predictor.analyze_spending_patterns(expenses)
        spending_patterns = json.dumps(spending_patterns_dict, separators=(',', ':'))
        alerts = predictor.get_savings_alerts(financial_data, expenses)
        
        SavingsPrediction.objects.create(
            user=request.user,
            predicted_amount=predicted_savings,
            confidence_score=0.8
        )
    else:
        predicted_savings = 0
        spending_patterns = json.dumps({})
        alerts = []
    
    total_expenses = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    expense_category_data = expenses.values('category').annotate(total=models.Sum('amount'))
    expense_category_dict = {item['category']: float(item['total']) for item in expense_category_data}
    
    remaining_amount = 0
    if financial_data:
        remaining_amount = float(financial_data.income) - float(total_expenses)
        if savings_goal:
            remaining_amount -= float(savings_goal.current_amount)
    context = {
        'financial_data': financial_data,
        'expenses': expenses,
        'savings_goal': savings_goal,
        'predicted_savings': predicted_savings,
        'spending_patterns': spending_patterns,
        'alerts': alerts,
        'total_expenses': total_expenses,
        'expense_category_data': expense_category_dict,
        'remaining_amount': remaining_amount,
    }
    income_monthly = FinancialData.objects.filter(user=request.user).annotate(month_trunc=TruncMonth('date')).values('month_trunc').annotate(total_income=Sum('income')).order_by('month_trunc')
    expense_monthly = Expense.objects.filter(user=request.user).annotate(month_trunc=TruncMonth('date')).values('month_trunc').annotate(total_expense=Sum('amount')).order_by('month_trunc')
    savings_monthly = MonthlySavings.objects.filter(user=request.user).annotate(month_trunc=TruncMonth('month')).values('month_trunc').annotate(total_savings=Sum('amount')).order_by('month_trunc')
    
    income_data = {item['month_trunc'].strftime('%Y-%m'): float(item['total_income']) for item in income_monthly}
    expense_data = {item['month_trunc'].strftime('%Y-%m'): float(item['total_expense']) for item in expense_monthly}
    
    savings_history = []
    cumulative_savings = 0.0
    savings_goal_amount = float(savings_goal.target_amount) if savings_goal else 0.0
    for item in savings_monthly:
        month_str = item['month_trunc'].strftime('%Y-%m')
        cumulative_savings += float(item['total_savings'])
        savings_history.append({'month': month_str, 'cumulative_savings': cumulative_savings})
        # Removed break to include all months including previous months
        # if cumulative_savings >= savings_goal_amount:
        #     break
    
    savings_data = {entry['month']: entry['cumulative_savings'] for entry in savings_history}
    
    budgets = Budget.objects.filter(user=request.user).order_by('-month')
    budget_progress = []
    for budget in budgets:
        spent = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__year=budget.month.year,
            date__month=budget.month.month
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        progress = (spent / budget.monthly_budget) * 100 if budget.monthly_budget > 0 else 0
        budget_progress.append({
            'category': budget.category,
            'month': budget.month.strftime('%Y-%m'),
            'monthly_budget': budget.monthly_budget,
            'spent': spent,
            'progress': progress,
        })

    import datetime
    from django.utils import timezone
    notifications = []

    seven_days_ago = timezone.now().date() - datetime.timedelta(days=7)
    recent_expenses = Expense.objects.filter(user=request.user, date__gte=seven_days_ago)
    for expense in recent_expenses:
        notifications.append({
            'message': f"Recent bill: {expense.category} of ₹{expense.amount} on {expense.date.strftime('%Y-%m-%d')}",
            'type': 'bill',
        })

    for budget in budget_progress:
        if budget['progress'] >= 90:
            notifications.append({
                'message': f"Budget alert: {budget['category'].title()} spending is at {budget['progress']:.2f}%",
                'type': 'budget',
            })

    if savings_goal and savings_goal.target_date:
        days_to_goal = (savings_goal.target_date - timezone.now().date()).days
        if 0 <= days_to_goal <= 7:
            notifications.append({
                'message': f"Savings goal deadline approaching in {days_to_goal} day(s).",
                'type': 'goal',
            })

    context.update({
        'income_data': json.dumps(income_data),
        'expense_data': json.dumps(expense_data),
        'savings_data_dict': savings_data,
        'savings_data': json.dumps(savings_data),
        'budget_progress': budget_progress,
        'notifications': notifications,
        'savings_history': savings_history,
        'savings_goal_amount': savings_goal_amount,
        'savings_data_chart': json.dumps(savings_data),
    })
    
    return render(request, 'savings/dashboard.html', context)

@login_required
def savings_history(request):
    savings_goal = SavingsGoal.objects.filter(user=request.user).last()
    savings_monthly = MonthlySavings.objects.filter(user=request.user).annotate(month_trunc=TruncMonth('month')).values('month_trunc').annotate(total_savings=Sum('amount')).order_by('month_trunc')

    savings_history = []
    cumulative_savings = 0.0
    savings_goal_amount = float(savings_goal.target_amount) if savings_goal else 0.0
    for item in savings_monthly:
        month_str = item['month_trunc'].strftime('%Y-%m')
        cumulative_savings += float(item['total_savings'])
        savings_history.append({'month': month_str, 'cumulative_savings': cumulative_savings})
        if cumulative_savings >= savings_goal_amount:
            break

    context = {
        'savings_history': savings_history,
        'savings_goal': savings_goal,
        'savings_goal_amount': savings_goal_amount,
        'savings_data': json.dumps({entry['month']: entry['cumulative_savings'] for entry in savings_history}),
    }
    return render(request, 'savings/savings_history.html', context)

@login_required
def transaction_history(request):
    incomes = FinancialData.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    context = {
        'incomes': incomes,
        'expenses': expenses,
    }
    return render(request, 'savings/transaction_history.html', context)

@login_required
def delete_income(request, id):
    income_record = get_object_or_404(FinancialData, id=id, user=request.user)
    income_record.delete()
    messages.success(request, 'Income record deleted successfully.')
    return redirect('transaction_history')

@login_required
def delete_expense(request, id):
    expense_record = get_object_or_404(Expense, id=id, user=request.user)
    expense_record.delete()
    messages.success(request, 'Expense record deleted successfully.')
    return redirect('transaction_history')

@login_required
def edit_income(request, id):
    income_record = get_object_or_404(FinancialData, id=id, user=request.user)
    if request.method == 'POST':
        income = request.POST.get('income')
        if income:
            income_record.income = income
            income_record.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please enter a valid income amount.')
    context = {'income_record': income_record}
    return render(request, 'savings/edit_income.html', context)

@login_required
def edit_expense(request, id):
    expense_record = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        if amount and category:
            expense_record.amount = amount
            expense_record.category = category
            expense_record.description = description
            expense_record.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please enter valid amount and category.')
    context = {'expense_record': expense_record}
    return render(request, 'savings/edit_expense.html', context)

@login_required
def add_income(request):
    if request.method == 'POST':
        income = request.POST.get('income')
        if income:
            FinancialData.objects.create(
                user=request.user,
                income=income
            )
            messages.success(request, 'Income added successfully!')
        return redirect('dashboard')
    incomes = FinancialData.objects.filter(user=request.user).order_by('-date')
    return render(request, 'savings/add_income.html', {'incomes': incomes})

@login_required
def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        
        if amount and category:
            Expense.objects.create(
                user=request.user,
                amount=amount,
                category=category,
                description=description
            )
            messages.success(request, 'Expense added successfully!')
        return redirect('dashboard')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'savings/add_expense.html', {'expenses': expenses})

@login_required
def set_savings_goal(request):
    if request.method == 'POST':
        target_amount = request.POST.get('target_amount')
        target_date = request.POST.get('target_date')
        
        if target_amount and target_date:
            SavingsGoal.objects.create(
                user=request.user,
                target_amount=target_amount,
                target_date=datetime.strptime(target_date, '%Y-%m-%d')
            )
            messages.success(request, 'Savings goal set successfully!')
        return redirect('dashboard')
    return render(request, 'savings/set_goal.html')

@login_required
def add_savings(request):
    from decimal import Decimal
    from datetime import datetime
    savings_goal = SavingsGoal.objects.filter(user=request.user).last()
    if request.method == 'POST':
        saved_amount = request.POST.get('saved_amount')
        month_str = request.POST.get('month')
        if saved_amount and savings_goal and month_str:
            try:
                month_date = datetime.strptime(month_str, '%Y-%m')
                from .models import MonthlySavings
                MonthlySavings.objects.create(
                    user=request.user,
                    month=month_date,
                    amount=Decimal(saved_amount)
                )
                savings_goal.current_amount += Decimal(saved_amount)
                savings_goal.save()
                messages.success(request, 'Savings updated successfully!')
            except Exception as e:
                messages.error(request, f'Error saving monthly savings: {e}')
        else:
            messages.error(request, 'Please set a savings goal first and enter valid amount and month.')
        return redirect('dashboard')
    return render(request, 'savings/add_savings.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'savings/register.html', {'form': form})

@login_required
def edit_savings(request):
    from decimal import Decimal
    savings_goal = SavingsGoal.objects.filter(user=request.user).last()
    if not savings_goal:
        messages.error(request, 'No savings goal set. Please set a savings goal first.')
        return redirect('dashboard')
    if request.method == 'POST':
        new_amount = request.POST.get('current_amount')
        if new_amount:
            try:
                savings_goal.current_amount = Decimal(new_amount)
                savings_goal.save()
                messages.success(request, 'Savings amount updated successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error updating savings: {e}')
        else:
            messages.error(request, 'Please enter a valid amount.')
    context = {'savings_goal': savings_goal}
    return render(request, 'savings/edit_savings.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your profile and password have been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'savings/profile.html', context)

@login_required
def budget(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-month')
    if request.method == 'POST':
        category = request.POST.get('category')
        monthly_budget = request.POST.get('monthly_budget')
        month = request.POST.get('month')
        if category and monthly_budget and month:
            month_date = datetime.strptime(month, '%Y-%m')
            Budget.objects.create(
                user=request.user,
                category=category,
                monthly_budget=monthly_budget,
                month=month_date
            )
            messages.success(request, 'Budget set successfully.')
            return redirect('budget')
        else:
            messages.error(request, 'Please fill all fields correctly.')
    context = {
        'budgets': budgets,
        'categories': Budget.CATEGORY_CHOICES,
    }
    return render(request, 'savings/budget.html', context)

@login_required
def edit_budget(request, id):
    budget = get_object_or_404(Budget, id=id, user=request.user)
    if request.method == 'POST':
        category = request.POST.get('category')
        monthly_budget = request.POST.get('monthly_budget')
        month = request.POST.get('month')
        if category and monthly_budget and month:
            try:
                month_date = datetime.strptime(month, '%Y-%m')
                budget.category = category
                budget.monthly_budget = monthly_budget
                budget.month = month_date
                budget.save()
                messages.success(request, 'Budget updated successfully.')
                return redirect('budget')
            except Exception as e:
                messages.error(request, f'Error updating budget: {e}')
        else:
            messages.error(request, 'Please fill all fields correctly.')
    context = {
        'budget': budget,
        'categories': Budget.CATEGORY_CHOICES,
    }
    return render(request, 'savings/edit_budget.html', context)
