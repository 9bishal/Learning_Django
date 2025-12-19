from django.shortcuts import render, get_object_or_404, redirect
from .models import UserDetail
from .forms import UserDetailForm

# Create your views here.

def user_form(request):
    if request.method == 'POST':
        form = UserDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserDetailForm()
    return render(request, 'details/user_form.html', {'form': form})

def user_list(request):
    users = UserDetail.objects.all()
    return render(request, 'details/user_list.html', {'users': users})

def user_edit(request, pk):
    user = get_object_or_404(UserDetail, pk=pk)
    if request.method == 'POST':
        form = UserDetailForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserDetailForm(instance=user)
    return render(request, 'details/user_edit.html', {'form': form})

def user_delete(request, pk):
    user = get_object_or_404(UserDetail, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'details/user_delete.html', {'user': user})
