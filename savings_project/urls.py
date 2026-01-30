from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from savings import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', views.logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('add-income/', views.add_income, name='add_income'),
    path('edit-income/<int:id>/', views.edit_income, name='edit_income'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('edit-expense/<int:id>/', views.edit_expense, name='edit_expense'),
    path('set-goal/', views.set_savings_goal, name='set_goal'),
    path('add-savings/', views.add_savings, name='add_savings'),
    path('login/', auth_views.LoginView.as_view(template_name='savings/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('delete-income/<int:id>/', views.delete_income, name='delete_income'),
    path('delete-expense/<int:id>/', views.delete_expense, name='delete_expense'),
    path('edit-savings/', views.edit_savings, name='edit_savings'),
    path('profile/', views.profile, name='profile'),
    path('budget/', views.budget, name='budget'),
    path('edit-budget/<int:id>/', views.edit_budget, name='edit_budget'),

    # Password reset views
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='savings/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='savings/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='savings/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='savings/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
