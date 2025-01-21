from pydantic import BaseModel


class RegistrationTokenCreationData(BaseModel):
    amount: int
    voteGroups: list[int]


class VoteOptionData(BaseModel):
    optionId: int
    optionIndex: int
    optionTitle: str


class BaseBallotData(BaseModel):
    id: None | int = None
    title: str
    maximumVotes: int = 1
    minimumVotes: int = 1
    voteStacking: bool
    voteOptions: list[str]
    voteGroups: list[int]
    active: bool


class BallotData(BaseModel):
    id: int
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
    customId: str


class TokenData(BaseModel):
    access_token: str
    token_type: str


class VoteGroupCreationData(BaseModel):
    title: str
    

class VoteGroupDeletionData(BaseModel):
    id: int
    

class BeamerTextData(BaseModel):
    text: str
    

class RegistrationTokenResetData(BaseModel):
    token: str