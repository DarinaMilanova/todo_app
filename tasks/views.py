from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm, CustomRegisterForm, CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from datetime import timedelta

@login_required
def task_list(request):
    today = timezone.now().date()
    today_plus_2 = today + timedelta(days=2)
    tasks = Task.objects.filter(user=request.user)

    # Filtering
    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'incomplete':
        tasks = tasks.filter(completed=False)
    elif status == 'overdue':
        tasks = tasks.filter(due_date__lt=today, completed=False)
    elif status == 'upcoming':
        tasks = tasks.filter(due_date__gte=today, completed=False)

    # Search
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(title__icontains=query)

    # Sorting
    sort = request.GET.get('sort')
    sort_map = {
        'created_asc': 'created_at',
        'created_desc': '-created_at',
        'due_asc': 'due_date',
        'due_desc': '-due_date'
    }
    if sort:
        tasks = tasks.order_by(sort_map.get(sort, 'created_at'))

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'today': today,
        'today_plus_2': today_plus_2
    })
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/update_task.html', {'form': form})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect('task_list')
    return render(request, 'tasks/delete_task.html', {'task': task})


def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('task_list')
    else:
        form = CustomRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Logged in successfully.")
            return redirect('task_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'tasks/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('login')

@login_required
def toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

from datetime import datetime

@login_required
def update_due_date(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        due_date_str = request.POST.get('due_date')
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            task.due_date = None
        task.save()
    return redirect('task_list')



@login_required
def profile_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent logout
            messages.success(request, "Password changed successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'tasks/profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect('register')  # or 'login'
    return render(request, 'tasks/delete_account.html')


@login_required
def dashboard(request):
    today = timezone.now().date()
    user_tasks = Task.objects.filter(user=request.user)

    stats = {
        'total': user_tasks.count(),
        'completed': user_tasks.filter(completed=True).count(),
        'pending': user_tasks.filter(completed=False).count(),
        'overdue': user_tasks.filter(completed=False, due_date__lt=today).count(),
        'due_today': user_tasks.filter(completed=False, due_date=today).count()
    }

    return render(request, 'tasks/dashboard.html', {'stats': stats})


@login_required
def toggle_theme(request):
    current = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not current
    return JsonResponse({'dark_mode': not current})

@login_required
def clear_due_date(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.due_date = None
    task.save()
    return redirect('task_list')

