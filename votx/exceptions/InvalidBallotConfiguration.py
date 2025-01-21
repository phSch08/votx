from fastapi import HTTPException, status


class InvalidBallotConfiguration(HTTPException):
    def __init__(self, detail="The provided configuration for the ballot is invalid!"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

