import datetime
import os
from peewee import PostgresqlDatabase, TextField, Model, IntegerField, CompositeKey, CharField, DateTimeField, ForeignKeyField, BooleanField

# db = SqliteDatabase(None)
db = PostgresqlDatabase(
    os.environ.get('POSTGRES_DB'),
    user=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)


class BaseModel(Model):
    class Meta:
        database = db


class Ballot(BaseModel):
    title = CharField()
    maximumVotes = IntegerField(default=1)
    minimumVotes = IntegerField(default=1)
    voteStacking = BooleanField(default=False)
    active = BooleanField(default=False)


class RegistrationToken(BaseModel):
    token = CharField()
    issueDate = DateTimeField()


class VoterToken(BaseModel):
    token = CharField()
    registrationToken = ForeignKeyField(
        RegistrationToken, backref='voterToken')


class VoteGroup(BaseModel):
    title = CharField()


class BallotVoteGroup(BaseModel):
    ballot = ForeignKeyField(Ballot, backref='votegroups')
    votegroup = ForeignKeyField(VoteGroup, backref='ballots')


class VoteGroupMembership(BaseModel):
    voteGroup = ForeignKeyField(
        VoteGroup, backref="memberships", on_delete="CASCADE")
    registrationToken = ForeignKeyField(
        RegistrationToken, backref="memberships")


class VoteOption(BaseModel):
    title = CharField()
    ballot = ForeignKeyField(Ballot, backref='voteOptions')
    optionIndex = IntegerField()


class UserVote(BaseModel):
    voter = ForeignKeyField(RegistrationToken, backref='votes')
    ballot = ForeignKeyField(Ballot, backref='votes')


class Vote(BaseModel):
    vote_option = ForeignKeyField(VoteOption, backref='votes')
    custom_id = CharField()


class BallotProtocol(BaseModel):
    ballot = ForeignKeyField(Ballot, backref='protocol')
    timestamp = DateTimeField(default=datetime.datetime.now)
    message = TextField()