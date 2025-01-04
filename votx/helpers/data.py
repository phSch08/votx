import json
from ..dbModels import BallotVoteGroup, RegistrationToken, Ballot, UserVote, VoteGroup, VoteGroupMembership, VoteOption, VoterToken
from ..Models import BallotData, VoteOptionData
from ..socketManager import SocketManager
from peewee import JOIN, Case

socketManager = SocketManager()

def get_user_ballots(voterToken: str) -> list:
    query = (Ballot 
        .select(
            Ballot,
            VoteOption,
            Case(
                None,
                [(UserVote.id.is_null(), False)],
                True
            ).alias("has_user_vote")
        )
        .distinct()
        .where(Ballot.active == True)
        .join(BallotVoteGroup)
        .join(VoteGroup)
        .join(VoteGroupMembership)
        .join(RegistrationToken)
        .join(VoterToken)
        .join(UserVote, on=((RegistrationToken.id == UserVote.voter) & (Ballot.id == UserVote.ballot)), join_type=JOIN.LEFT_OUTER)
        .join_from(Ballot, VoteOption)
        .where(VoterToken.token == voterToken))
            
    ballots = {}
    for row in query:
        if row.id not in ballots:
            ballots[row.id] = {
                "ballot": row,
                "voted": row.has_user_vote,
                "options": []
            }
        ballots[row.id]["options"].append(row.voteoption)
        
    return list(map(toDictBallotData, ballots.values()))

async def broadcast_user_ballots():
    await socketManager.broadcast_func(lambda voter_token: {
        'type': 'BALLOTS', 
        'data': get_user_ballots(voter_token)
    })

def toPydanticBallotData(ballot: Ballot):
    return BallotData(
        id=ballot["ballot"].id,
        title=ballot["ballot"].title,
        maximumVotes=ballot["ballot"].maximumVotes,
        voteStacking=ballot["ballot"].voteStacking,
        voteOptions=[VoteOptionData(optionId=voteOption.id, optionIndex=voteOption.optionIndex, optionTitle=voteOption.title) for voteOption in ballot["options"]],
        active=ballot["ballot"].active,
        voted=ballot["voted"]
    )

def toDictBallotData(ballot: Ballot):
    return toPydanticBallotData(ballot).model_dump()

async def updateBeamerVoteCount(ballot: Ballot):
    await socketManager.broadcast_beamer(json.dumps({
        'type': 'SETVOTECOUNT',
        'data': len(ballot.votes)
    }))
    