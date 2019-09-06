class AbortTransaction(Exception):
    """
    A dummy exception used to trigger a database transaction rollback.
    """
    pass
