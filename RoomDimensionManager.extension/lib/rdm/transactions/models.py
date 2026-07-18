# -*- coding: utf-8 -*-
"""
Models for the Transaction Management Engine.
IronPython 2.7 compatible.
"""
import datetime
import uuid

class TransactionPolicy(object):
    """Rules and limits defining how transactions should behave."""
    def __init__(self, mode, suppress_warnings=True, rollback_on_error=True, max_retries=0, batch_size=1000):
        self.mode = mode
        self.suppress_warnings = suppress_warnings
        self.rollback_on_error = rollback_on_error
        self.max_retries = max_retries
        self.batch_size = batch_size

class TransactionContext(object):
    """Metadata regarding an active or historical transaction."""
    def __init__(self, name="Unknown Transaction"):
        self.transaction_id = str(uuid.uuid4())
        self.name = name
        self.start_time = datetime.datetime.utcnow()
        self.end_time = None
        self.affected_elements = []
        self.affected_views = []
        self.is_group = False
        self.is_committed = False
        self.is_rolled_back = False
        self.failure_details = None
        
    @property
    def duration_ms(self):
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000.0

class TransactionStatistics(object):
    """Aggregated audit of transaction operations."""
    def __init__(self, total_started=0, total_committed=0, total_rolled_back=0, total_failures=0, average_duration_ms=0.0):
        self.total_started = total_started
        self.total_committed = total_committed
        self.total_rolled_back = total_rolled_back
        self.total_failures = total_failures
        self.average_duration_ms = average_duration_ms
