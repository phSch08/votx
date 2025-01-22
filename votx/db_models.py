import datetime
import os

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    TextField,
)

# db = SqliteDatabase(None)
db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
)


class BaseModel(Model):
    class Meta:
        database = db


class Ballot(BaseModel):
    title = CharField()
    maximum_votes = IntegerField(default=1)
    minimum_votes = IntegerField(default=1)
    vote_stacking = BooleanField(default=False)
    active = BooleanField(default=False)


class RegistrationToken(BaseModel):
    token = CharField()
    issue_date = DateTimeField()


class VoterToken(BaseModel):
    token = CharField()
    registration_token = ForeignKeyField(RegistrationToken, backref="voterToken")


class VoteGroup(BaseModel):
    title = CharField()


class BallotVoteGroup(BaseModel):
    ballot = ForeignKeyField(Ballot, backref="votegroups")
    votegroup = ForeignKeyField(VoteGroup, backref="ballots")


class VoteGroupMembership(BaseModel):
    vote_group = ForeignKeyField(VoteGroup, backref="memberships", on_delete="CASCADE")
    registration_token = ForeignKeyField(RegistrationToken, backref="memberships")


class VoteOption(BaseModel):
    title = CharField()
    ballot = ForeignKeyField(Ballot, backref="voteOptions")
    option_index = IntegerField()


class UserVote(BaseModel):
    voter = ForeignKeyField(RegistrationToken, backref="votes")
    ballot = ForeignKeyField(Ballot, backref="votes")


class Vote(BaseModel):
    vote_option = ForeignKeyField(VoteOption, backref="votes")
    custom_id = CharField()


class BallotProtocol(BaseModel):
    ballot = ForeignKeyField(Ballot, backref="protocol")
    timestamp = DateTimeField(default=datetime.datetime.now)
    message = TextField()
