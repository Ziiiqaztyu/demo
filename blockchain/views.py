from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render, redirect
from .utils import Blockchain
from .models import PendingTransaction, Block
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

blockchain = Blockchain()

# Trang 1: Nhà sản xuất
@login_required
def producer_view(request):
    if request.method == 'POST':
        producer = request.POST.get('producer')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        blockchain.add_transaction(producer, amount, date)
        return redirect('producer')
    return render(request, 'blockchain/producer.html', {'title': 'Nhập Thông Tin Gạo'})

# Trang 2: Xác thực (Nhà phân phối/Đại lý)
@login_required
def verification_view(request):
    pending = PendingTransaction.objects.all()
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        verifier = request.POST.get('verifier')  # Nhập node ID
        blockchain.verify_transaction(transaction_id, verifier)
        return redirect('verification')
    return render(request, 'blockchain/verification.html', {'transactions': pending, 'title': 'Xác Thực Giao Dịch'})

# Trang 3: Kiểm tra block
@login_required
def verify_block_view(request):
    if request.method == 'POST':
        public_hash = request.POST.get('public_hash')
        try:
            block = Block.objects.get(public_hash=public_hash)
            return render(request, 'blockchain/verify_block.html', {
                'block': block,
                'valid': blockchain.validate_chain()
            })
        except:
            return render(request, 'blockchain/verify_block.html', {'error': 'Block not found'}, {'title': 'Nhập Thông Tin Gạo'})
    return render(request, 'blockchain/verify_block.html')

# Trang 4: Xem blockchain
@login_required
def block_list_view(request):
    chain = Block.objects.all().order_by('-index')
    return render(request, 'blockchain/block_list.html', {'blocks': chain,'title': 'Toàn Bộ Blockchain'})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Chào mừng bạn, {user.username}!") # Success message
            # Redirect to a protected page (e.g., home or a dashboard)
            next_url = request.GET.get('next') # Check for a 'next' parameter for redirection
            if next_url:
                return redirect(next_url)
            return redirect('home') # Assuming 'home' is a named URL for your main page
        else:
            # Form is not valid, re-render with errors
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.") # Error message
    else:
        # GET request: Display an empty form
        form = AuthenticationForm()

    return render(request, 'blockchain/signin.html', {'form': form, 'title': 'Đăng nhập'})

def user_logout(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    return redirect('signin')

def register_view(request):
    if request.method == 'POST':
        # Khi người dùng submit form
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Tài khoản {username} đã được tạo thành công! Vui lòng đăng nhập.')
            return redirect('sign_in') # Chuyển hướng tới trang đăng nhập
    else:
        # Khi người dùng mới vào trang (request GET)
        form = UserCreationForm()
    context = {
        "form": form,
        'title': 'Đăng ký'
    }
    return render(request, 'blockchain/register.html', context)
    
def home(request):
    return render(request, 'blockchain/home.html', {'title': 'Trang chủ'})