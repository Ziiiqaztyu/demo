from .models import Block, PendingTransaction
import json
#utils.py
class Blockchain:
    def __init__(self):
        self.pending_transactions = []
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
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def add_transaction(self, producer, amount, date):
        transaction = {
            'producer': producer,
            'amount': amount,
            'date': str(date),
        }
        PendingTransaction.objects.create(
            producer=producer,
            rice_amount=amount,
            production_date=date
        )

    def verify_transaction(self, transaction_id, verifier):
        try:
            t = PendingTransaction.objects.get(id=transaction_id)
            t.verifications.append(verifier)
            t.save()
            
            # Check if verified by 2 different nodes
            if len(set(t.verifications)) >= 2:
                self.pending_transactions.append({
                    'id': t.id,
                    'producer': t.producer,
                    'amount': t.rice_amount,
                    'date': str(t.production_date)
                })
                t.delete()
                
                # Create block if 5 verified transactions
                if len(self.pending_transactions) >= 5:
                    self.create_block()
            
            return True
        except:
            return False

    def create_block(self):
        last_block = self.last_block
        new_block = Block(
            transactions=self.pending_transactions[:5],
            previous_hash=last_block.current_hash if last_block else "0",
            nonce=0
        )
        new_block.save()
        
        # Proof-of-Work simulation
        while not new_block.current_hash.startswith("0000"):
            new_block.nonce += 1
            new_block.current_hash = new_block.calculate_hash()
            new_block.save()
        
        self.pending_transactions = self.pending_transactions[5:]
        self.chain.append(new_block)
        return new_block

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.previous_hash != previous.current_hash:
                return False
            
            if current.current_hash != current.calculate_hash():
                return False
        
        return True