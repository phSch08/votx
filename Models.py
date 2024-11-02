from pydantic import BaseModel

class AccessCodeCreationData(BaseModel):
    amount: int

class BallotData(BaseModel):
    id: None | int = None
    title: str
    maximumVotes: int = 1
    minimumVotes: int = 1
    voteStacking: bool
    voteOptions: list[str]
    active: bool
    alreadyVoted: None | bool = None

class VoteData(BaseModel):
    accessCode: str
    ballotId: int
    votes: list[int]

class Token(BaseModel):
    access_token: str
    token_type: str