# -*- coding: utf-8 -*-
"""Transaction adapter for the pure pyRevit application."""
from rdm.revit.interfaces import ITransactionService


class TransactionService(ITransactionService):
    def __init__(self, doc):
        self._doc = doc

    def execute_in_transaction(self, name, action):
        from Autodesk.Revit.DB import Transaction
        transaction = Transaction(self._doc, name)
        transaction.Start()
        try:
            if action():
                transaction.Commit()
                return True
            transaction.RollBack()
            return False
        except Exception:
            if transaction.HasStarted():
                transaction.RollBack()
            raise
