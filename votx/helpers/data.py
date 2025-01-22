import json

from peewee import JOIN, Case

from ..db_models import (
    Ballot,
    BallotVoteGroup,
    RegistrationToken,
    UserVote,
    VoteGroup,
    VoteGroupMembership,
    VoteOption,
    VoterToken,
)
from ..models import BallotData, VoteOptionData
from ..socket_manager import SocketManager

socket_manager = SocketManager()


def get_user_ballots(voter_token: str) -> list:
    query = (
        Ballot.select(
            Ballot,
            VoteOption,
            Case(None, [(UserVote.id.is_null(), False)], True).alias("has_user_vote"),
        )
        .distinct()
        .where(Ballot.active)
        .join(BallotVoteGroup)
        .join(VoteGroup)
        .join(VoteGroupMembership)
        .join(RegistrationToken)
        .join(VoterToken)
        .join(
            UserVote,
            on=(
                (RegistrationToken.id == UserVote.voter)
                & (Ballot.id == UserVote.ballot)
            ),
            join_type=JOIN.LEFT_OUTER,
        )
        .join_from(Ballot, VoteOption)
        .where(VoterToken.token == voter_token)
    )

    ballots = {}
    for row in query:
        if row.id not in ballots:
            ballots[row.id] = {"ballot": row, "voted": row.has_user_vote, "options": []}
        ballots[row.id]["options"].append(row.voteoption)

    return list(map(to_dict_ballot_data, ballots.values()))


async def broadcast_user_ballots():
    await socket_manager.broadcast_func(
        lambda voter_token: {"type": "BALLOTS", "data": get_user_ballots(voter_token)}
    )


def to_pydantic_ballot_data(ballot: Ballot):
    return BallotData(
        id=ballot["ballot"].id,
        title=ballot["ballot"].title,
        maximum_votes=ballot["ballot"].maximumVotes,
        vote_stacking=ballot["ballot"].voteStacking,
        vote_options=[
            VoteOptionData(
                option_id=voteOption.id,
                option_index=voteOption.optionIndex,
                option_title=voteOption.title,
            )
            for voteOption in ballot["options"]
        ],
        active=ballot["ballot"].active,
        voted=ballot["voted"],
    )


def to_dict_ballot_data(ballot: Ballot):
    return to_pydantic_ballot_data(ballot).model_dump()


async def update_beamer_vote_count(ballot: Ballot):
    await socket_manager.broadcast_beamer(
        json.dumps({"type": "SETVOTECOUNT", "data": len(ballot.votes)})
    )
