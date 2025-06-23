# blockchain/models.py
from django.db import models
import hashlib
import json
from time import time

class Block(models.Model):
    index = models.AutoField(primary_key=True)
    timestamp = models.FloatField(default=time)
    transactions = models.JSONField(default=list)
    previous_hash = models.CharField(max_length=64)
    nonce = models.IntegerField(default=0)
    current_hash = models.CharField(max_length=64, blank=True)
    public_hash = models.CharField(max_length=64, blank=True)
    is_verified = models.BooleanField(default=False)

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def save(self, *args, **kwargs):
        if not self.current_hash:
            self.current_hash = self.calculate_hash()
        if not self.public_hash:
            self.public_hash = hashlib.sha256(self.current_hash.encode()).hexdigest()
        super().save(*args, **kwargs)

class PendingTransaction(models.Model):
    producer = models.CharField(max_length=100)
    rice_amount = models.IntegerField()
    production_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    verifications = models.JSONField(default=list)  # Track verification nodes
    is_ready_for_block = models.BooleanField(default=False) # <-- THÊM DÒNG NÀY