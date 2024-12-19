from pydantic import BaseModel

class RegistrationTokenCreationData(BaseModel):
    amount: int

class VoteOptionData(BaseModel):
    optionId: int
    optionTitle: str

class BallotData(BaseModel):
    id: None | int = None
    title: str
    maximumVotes: int = 1
    minimumVotes: int = 1
    voteStacking: bool
    voteOptions: list[VoteOptionData]
    active: bool
    voted: bool

class VoteData(BaseModel):
    ballotId: int
    votes: list[int]

class TokenData(BaseModel):
    access_token: str
    token_type: str