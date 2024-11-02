from peewee import SqliteDatabase, Model, IntegerField, CompositeKey, CharField, DateTimeField, ForeignKeyField, BooleanField

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class AccessCode(BaseModel):
    code = CharField()
    issueDate = DateTimeField()

class Ballot(BaseModel):
    title = CharField()
    maximumVotes = IntegerField(default= 1)
    minimumVotes = IntegerField(default= 1)
    voteStacking = BooleanField(default=False)
    active= BooleanField(default=False)

class VoteOption(BaseModel):
    title = CharField()
    voteCount = IntegerField(default=0)
    ballot = ForeignKeyField(Ballot, backref='voteOptions')
    optionIndex = IntegerField()

    class Meta:
        primary_key = CompositeKey('ballot', 'optionIndex')

class Vote(BaseModel):
    voter = ForeignKeyField(AccessCode, backref='votes')
    ballot = ForeignKeyField(Ballot, backref='votes')