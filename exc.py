
class SITOException(Exception):
    """All exceptions from the bot"""

class NotFound(SITOException):
    """Not Found"""

class InvalidArgs(SITOException):
    """Invalid args given to command"""

class InvalidSheet(SITOException):
    """Exception occur when a error occur when"""

class PermissionNotGiven(SITOException):
    """Exception raised when bot can't acces character sheet"""

class ALEDException(SITOException):
    """Well done for got this error"""