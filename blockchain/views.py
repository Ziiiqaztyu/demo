from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .utils import Blockchain
from .models import PendingTransaction, Block
from django.http import JsonResponse

blockchain = Blockchain()

# Trang 1: Nhà sản xuất
def producer_view(request):
    if request.method == 'POST':
        producer = request.POST.get('producer')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        blockchain.add_transaction(producer, amount, date)
        return redirect('producer')
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