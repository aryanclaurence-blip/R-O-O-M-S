# -*- coding: utf-8 -*-
"""Transaction Engine for PARAMS FLOW safe model writes."""
try:
    from Autodesk.Revit.DB import TransactionGroup, Transaction
except ImportError:
    class TransactionGroup(object):
        def __init__(self, doc, name): pass
        def Start(self): pass
        def Commit(self): pass
        def RollBack(self): pass
    class Transaction(object):
        def __init__(self, doc, name): pass
        def Start(self): pass
        def Commit(self): pass
        def RollBack(self): pass

class PFTransactionEngine(object):
    def __init__(self, doc):
        self.doc = doc

    def execute_in_group(self, group_name, action_func):
        """Wraps action execution inside a safe Revit TransactionGroup."""
        tg = TransactionGroup(self.doc, group_name)
        tg.Start()
        try:
            result = action_func()
            tg.Commit()
            return result
        except Exception as e:
            try:
                tg.RollBack()
            except Exception:
                pass
            raise e
