class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__(errors)
        self.errors = errors


class PlayerNotFound(Exception):
    pass
