
from django.shortcuts import render,redirect

# Create your views here.

# blockchain/views.py

from django.shortcuts import render, redirect
from .utils import Blockchain
from .models import PendingTransaction, Block
from django.http import JsonResponse

from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from datetime import date # Đảm bảo dòng này có

blockchain = Blockchain()

# Trang 1: Nhà sản xuất (GIỮ NGUYÊN NHƯ ĐÃ SỬA)
def producer_view(request):
    if request.method == 'POST':
        producer = request.POST.get('producer')
        amount_str = request.POST.get('amount')
        date_str = request.POST.get('date')

        try:
            amount = int(amount_str)
            production_date = date.fromisoformat(date_str)

            blockchain.add_transaction(producer, amount, production_date)
            return redirect('producer')
        except ValueError as e:
            return render(request, 'blockchain/producer.html', {'error': f'Dữ liệu nhập không hợp lệ: {e}'})
        except Exception as e:
            return render(request, 'blockchain/producer.html', {'error': f'Có lỗi xảy ra khi thêm giao dịch: {e}'})

    return render(request, 'blockchain/producer.html')


# Trang 2: Xác thực (Nhà phân phối/Đại lý) - Sửa phần này
def verification_view(request):
    pending_transactions = [] # Khởi tạo rỗng để tránh lỗi nếu database không thể truy vấn
    error_message = None

    try:
        # Lấy tất cả các giao dịch đang chờ từ database
        # Lọc các giao dịch CHƯA sẵn sàng đưa vào block để hiển thị cho người dùng xác nhận
        pending_transactions = PendingTransaction.objects.filter(is_ready_for_block=False).order_by('created_at')
    except Exception as e:
        error_message = f'Không thể tải giao dịch đang chờ: {e}'
        # In lỗi ra console của Render để dễ debug hơn
        print(f"Error loading pending transactions: {e}")

    if request.method == 'POST':
        transaction_id_str = request.POST.get('transaction_id')
        verifier = request.POST.get('verifier')

        try:
            transaction_id = int(transaction_id_str) # CHUYỂN ĐỔI SANG INT
            # Gọi hàm verify_transaction
            success = blockchain.verify_transaction(transaction_id, verifier)

            if success:
                return redirect('verification')
            else:
                error_message = 'Xác thực giao dịch thất bại. Có thể giao dịch không tồn tại hoặc lỗi nội bộ.'
        except ValueError:
            error_message = 'ID giao dịch không hợp lệ. Vui lòng nhập một số.'
        except Exception as e:
            error_message = f'Có lỗi xảy ra khi xác thực: {e}'
            print(f"Error during verification POST: {e}")

    return render(request, 'blockchain/verification.html', {
        'transactions': pending_transactions,
        'error': error_message
    })

# Trang 3: Kiểm tra block (GIỮ NGUYÊN)
def verify_block_view(request):
    if request.method == 'POST':
        public_hash = request.POST.get('public_hash')
        try:
            block = Block.objects.get(public_hash=public_hash)
            return render(request, 'blockchain/verify_block.html', {
                'block': block,
                'valid': blockchain.validate_chain()
            })
        except Block.DoesNotExist: # Sử dụng Block.DoesNotExist thay vì catch all
            return render(request, 'blockchain/verify_block.html', {'error': 'Block not found'})
        except Exception as e: # Catch lỗi chung nếu có
            print(f"Error in verify_block_view: {e}")
            return render(request, 'blockchain/verify_block.html', {'error': f'Có lỗi xảy ra: {e}'})
    return render(request, 'blockchain/verify_block.html')

# Trang 4: Xem blockchain (GIỮ NGUYÊN)
def block_list_view(request):
    chain = Block.objects.all().order_by('-index')
    return render(request, 'blockchain/block_list.html', {'blocks': chain})

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