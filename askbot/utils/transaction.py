"""Utilities for working with database transactions"""

class DummyTransaction(object):
    """Dummy transaction class
    that can be imported instead of the django
    transaction management and debug issues
    inside the code running inside the transaction blocks
    """
    @classmethod
    def commit(cls):
        pass

    @classmethod
    def commit_manually(cls, func):
        def decorated(*args, **kwargs):
            func(*args, **kwargs)
        return decorated

#a utility instance to use instead of the normal transaction object
dummy_transaction = DummyTransaction()
