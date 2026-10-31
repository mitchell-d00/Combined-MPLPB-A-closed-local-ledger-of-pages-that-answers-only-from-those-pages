"""Public work-ledger errors; all reject the operation before committing it."""
class WorkError(ValueError):
    pass


class Conflict(WorkError):
    pass


class Denied(WorkError):
    pass


class IntegrityError(WorkError):
    pass
