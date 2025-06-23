from django.shortcuts import render
#views.py
# Create your views here.
from django.shortcuts import render, redirect
from .utils import Blockchain
from .models import PendingTransaction, Block
from django.http import JsonResponse
from datetime import date # Thêm import này

blockchain = Blockchain()

# Trang 1: Nhà sản xuất
def producer_view(request):
    if request.method == 'POST':
        producer = request.POST.get('producer')
        amount_str = request.POST.get('amount') # Lấy dưới dạng string
        date_str = request.POST.get('date')   # Lấy dưới dạng string
        
        try:
            # Chuyển đổi amount sang integer
            amount = int(amount_str)
            # Chuyển đổi date string sang đối tượng date
            production_date = date.fromisoformat(date_str) # Giả định định dạng 'YYYY-MM-DD'
            
            blockchain.add_transaction(producer, amount, production_date)
            return redirect('producer')
        except ValueError as e:
            # Xử lý lỗi nếu amount không phải số hoặc date sai định dạng
            return render(request, 'blockchain/producer.html', {'error': f'Dữ liệu nhập không hợp lệ: {e}'})
        except Exception as e:
            # Xử lý các lỗi khác trong quá trình thêm giao dịch
            return render(request, 'blockchain/producer.html', {'error': f'Có lỗi xảy ra khi thêm giao dịch: {e}'})
            
    return render(request, 'blockchain/producer.html')

# Trang 2: Xác thực (Nhà phân phối/Đại lý)
def verification_view(request):
    pending = PendingTransaction.objects.all()
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        verifier = request.POST.get('verifier')  # Nhập node ID
        blockchain.verify_transaction(transaction_id, verifier)
        return redirect('verification')
    return render(request, 'blockchain/verification.html', {'transactions': pending})

# Trang 3: Kiểm tra block
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
            return render(request, 'blockchain/verify_block.html', {'error': 'Block not found'})
    return render(request, 'blockchain/verify_block.html')

# Trang 4: Xem blockchain
def block_list_view(request):
    chain = Block.objects.all().order_by('-index')
    return render(request, 'blockchain/block_list.html', {'blocks': chain})