from pydantic import BaseModel


class RegistrationTokenCreationData(BaseModel):
    amount: int
    vote_groups: list[int]


class VoteOptionData(BaseModel):
    option_id: int
    option_index: int
    option_title: str


class BaseBallotData(BaseModel):
    id: None | int = None
    title: str
    maximum_votes: int = 1
    minimum_votes: int = 1
    vote_stacking: bool
    vote_options: list[str]
    vote_groups: list[int]
    active: bool


class BallotData(BaseModel):
    id: int
    title: str
    maximum_votes: int = 1
    minimum_votes: int = 1
    vote_stacking: bool
    vote_options: list[VoteOptionData]
    active: bool
    voted: bool


class VoteData(BaseModel):
    ballot_id: int
    votes: list[int]
    custom_id: str


class VoteResultData(BaseModel):
    success: bool
    ballots: list[BallotData] | None


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
