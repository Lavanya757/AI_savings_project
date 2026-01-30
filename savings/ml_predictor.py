import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

class SavingsPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        
    def prepare_features(self, financial_data, expenses):
        # Calculate monthly totals
        monthly_income = financial_data.income
        monthly_expenses = sum(expense.amount for expense in expenses)
        expense_ratio = float(monthly_expenses) / float(monthly_income) if monthly_income else 0
        
        # Create feature array
        features = np.array([[float(monthly_income), float(monthly_expenses), expense_ratio]])
        return self.scaler.fit_transform(features)
    
    def predict_savings(self, financial_data, expenses):
        features = self.prepare_features(financial_data, expenses)
        
        # Basic rule-based prediction
        monthly_income = float(financial_data.income)
        monthly_expenses = sum(float(expense.amount) for expense in expenses)
        
        # Calculate recommended savings based on the 50/30/20 rule
        # 50% needs, 30% wants, 20% savings
        recommended_savings = monthly_income * 0.2
        
        # Adjust based on expense ratio
        expense_ratio = monthly_expenses / monthly_income if monthly_income else 1
        if expense_ratio > 0.8:  # High expenses
            recommended_savings *= 0.5  # Reduce recommended savings
        elif expense_ratio < 0.6:  # Low expenses
            recommended_savings *= 1.2  # Increase recommended savings
            
        return round(recommended_savings, 2)
    
    def analyze_spending_patterns(self, expenses):
        categories = {}
        for expense in expenses:
            category = expense.category
            amount = float(expense.amount)
            categories[category] = categories.get(category, 0) + amount
            
        return categories
    
    def get_savings_alerts(self, financial_data, expenses):
        alerts = []
        monthly_income = float(financial_data.income)
        monthly_expenses = sum(float(expense.amount) for expense in expenses)
        expense_ratio = monthly_expenses / monthly_income if monthly_income else 1
        
        if expense_ratio > 0.8:
            alerts.append("Warning! Your expenses are too high this month. Consider reducing non-essential spending.")
        elif expense_ratio > 0.7:
            alerts.append("Your expenses are approaching a high level. Review your spending habits.")
            
        return alerts