# blockchain/utils.py
from .models import Block, PendingTransaction
import json
import hashlib # Thêm import hashlib nếu chưa có
from time import time # Thêm import time nếu chưa có

class Blockchain:
    def __init__(self):
        # Khi khởi tạo, chúng ta không cần tải pending_transactions vào bộ nhớ nữa
        self.chain = list(Block.objects.all().order_by('index'))
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            transactions=[],
            previous_hash="0",
            nonce=0
        )
        genesis.save()
        # Cập nhật self.chain sau khi tạo genesis block nếu cần quản lý trong bộ nhớ
        # Tuy nhiên, last_block sẽ luôn đọc từ DB, nên không bắt buộc phải thêm vào self.chain ở đây
        # self.chain.append(genesis)

    @property
    def last_block(self):
        # Luôn lấy block cuối cùng từ database để đảm bảo là block mới nhất và chính xác nhất
        return Block.objects.last()

    def add_transaction(self, producer, amount, date):
        # Giao dịch mới được tạo và lưu trực tiếp vào PendingTransaction model trong DB
        PendingTransaction.objects.create(
            producer=producer,
            rice_amount=amount,
            production_date=date
        )
        # Không cần thêm vào danh sách trong bộ nhớ nữa

    def verify_transaction(self, transaction_id, verifier):
        try:
            t = PendingTransaction.objects.get(id=transaction_id)

            # Đảm bảo mỗi verifier chỉ được thêm một lần
            if verifier not in t.verifications:
                t.verifications.append(verifier)
            t.save()

            # Kiểm tra nếu đủ 2 xác nhận khác nhau (sử dụng set để đếm số lượng verifier duy nhất)
            if len(set(t.verifications)) >= 2:
                t.is_ready_for_block = True # Đánh dấu giao dịch đã sẵn sàng để đưa vào block
                t.save()

                # Sau khi đánh dấu là sẵn sàng, kiểm tra và tạo block nếu đủ số lượng
                self.check_and_create_block()

            return True
        except PendingTransaction.DoesNotExist:
            print(f"Transaction with ID {transaction_id} not found.")
            return False
        except Exception as e:
            print(f"Error during verification: {e}")
            return False

    def check_and_create_block(self):
        # Lấy các giao dịch đã sẵn sàng để đưa vào block từ database, giới hạn 5 giao dịch
        ready_transactions = PendingTransaction.objects.filter(is_ready_for_block=True).order_by('created_at')[:5]

        if len(ready_transactions) >= 5:
            # Chuyển đổi các đối tượng PendingTransaction thành dict để lưu vào Block's transactions (JSONField)
            transactions_data = []
            for t in ready_transactions:
                transactions_data.append({
                    'id': t.id,
                    'producer': t.producer,
                    'amount': t.rice_amount,
                    'date': str(t.production_date) # Đảm bảo date là string để JSONField lưu đúng
                })

            last_block = self.last_block
            new_block = Block(
                transactions=transactions_data,
                previous_hash=last_block.current_hash if last_block else "0",
                nonce=0
            )
            new_block.save() # Lưu block lần đầu để có index và hash cơ sở

            # Thực hiện Proof-of-Work (simulated)
            while not new_block.current_hash.startswith("0000"):
                new_block.nonce += 1
                new_block.current_hash = new_block.calculate_hash()
                new_block.save() # Cập nhật nonce và hash vào DB sau mỗi lần thử

            # Sau khi block được tạo thành công và mined, xóa các giao dịch đã được đưa vào block khỏi PendingTransaction
            for t in ready_transactions:
                t.delete()

            # Có thể cập nhật lại self.chain trong bộ nhớ nếu bạn cần nó phản ánh toàn bộ chuỗi
            # Ví dụ: self.chain = list(Block.objects.all().order_by('index'))
            # Tuy nhiên, nếu bạn chỉ dùng self.last_block, thì không quá cần thiết phải cập nhật self.chain liên tục.

            return new_block
        return None # Không đủ giao dịch để tạo block

    def validate_chain(self):
        chain_from_db = list(Block.objects.all().order_by('index'))
        if not chain_from_db:
            print("Blockchain: Chain is empty, considered valid.")
            return True # Chuỗi rỗng vẫn hợp lệ

        for i in range(1, len(chain_from_db)):
            current = chain_from_db[i]
            previous = chain_from_db[i-1]

            # In thông tin debug
            print(f"Blockchain: Validating block {current.index}...")
            print(f"  Current previous_hash: {current.previous_hash}")
            print(f"  Previous current_hash: {previous.current_hash}")

            # Kiểm tra hash của block trước đó
            if current.previous_hash != previous.current_hash:
                print(f"Blockchain Validation Error: Block {current.index} previous_hash mismatch.")
                return False

            # Tính lại hash của block hiện tại và so sánh
            calculated_current_hash = current.calculate_hash()
            print(f"  Current actual hash: {current.current_hash}")
            print(f"  Calculated hash: {calculated_current_hash}")

            if current.current_hash != calculated_current_hash:
                print(f"Blockchain Validation Error: Block {current.index} current_hash mismatch.")
                return False

            # Kiểm tra Proof-of-Work (nếu cần) - Đảm bảo hash bắt đầu bằng "0000"
            if not current.current_hash.startswith("0000"):
                print(f"Blockchain Validation Error: Block {current.index} does not meet PoW difficulty.")
                return False

        print("Blockchain: Chain is valid.")
        return True
