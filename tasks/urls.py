from . import views
from django.urls import path
from .views import (
    task_list, create_task, update_task, delete_task,
    login_view, logout_view, register_view
)

urlpatterns = [
    path('', task_list, name='task_list'),
    path('create/', create_task, name='create_task'),
    path('update/<int:pk>/', update_task, name='update_task'),
    path('delete/<int:pk>/', delete_task, name='delete_task'),
    path('toggle/<int:pk>/', views.toggle_complete, name='toggle_complete'),
    path('update-due-date/<int:pk>/', views.update_due_date, name='update_due_date'),

    # Auth
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('task/<int:pk>/clear-due-date/', views.clear_due_date, name='clear_due_date'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),

]
