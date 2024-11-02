from .dbModels import AccessCode, Ballot, Vote
from .Models import BallotData
from peewee import DoesNotExist, Case, fn
from .socketManager import SocketManager

socketManager = SocketManager()

def get_user_ballots(access_code: str):
    subquery = (
        Vote
        .select(fn.COUNT(Vote.id))
        .join(AccessCode)
        .where((Vote.ballot == Ballot.id) & (AccessCode.code == access_code))
    )
   
    query = (
        Ballot
        .select(
            Ballot,
            Case(
                None,
                (
                    (subquery > 0, True),
                ),
                False
            ).alias('has_voted')
        ).where(Ballot.active)
    )
   
    return query

async def broadcast_user_ballots():
    await socketManager.broadcast_func(lambda access_code: {
        'type': 'BALLOTS', 
        'data': list(map(toDictBallotData, get_user_ballots(access_code)))})

def toPydanticBallotData(ballot: Ballot):
    return BallotData(
        id=ballot.id,
        title=ballot.title,
        maximumVotes=ballot.maximumVotes,
        voteStacking=ballot.voteStacking,
        voteOptions=[voteOption.title for voteOption in ballot.voteOptions],
        active=ballot.active,
        alreadyVoted=ballot.has_voted
        )

def toDictBallotData(ballot: Ballot):
    return toPydanticBallotData(ballot).model_dump()