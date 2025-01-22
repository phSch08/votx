from fastapi import HTTPException, status


class BallotProtectedException(HTTPException):
    def __init__(self, detail="The ballot cannot be changed!"):
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
