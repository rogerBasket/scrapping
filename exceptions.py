class ScrappingError(Exception):
    pass

class DestinationError(ScrappingError):
    pass

class OriginationError(ScrappingError):
    pass