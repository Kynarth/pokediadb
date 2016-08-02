from peewee import Model
from peewee import TextField
from peewee import CharField
from peewee import FloatField
from peewee import BooleanField
from peewee import IntegerField
from peewee import CompositeKey
from peewee import FixedCharField
from peewee import SqliteDatabase
from peewee import ForeignKeyField


# Database path is unknown at the moment. Initialize it with the init function
db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Language(BaseModel):
    name = CharField(max_length=15)
    code = FixedCharField(max_length=2)


# =========================================================================== #
#                                Version models                               #
# =========================================================================== #
class Version(BaseModel):
    id = IntegerField(primary_key=True)
    generation = IntegerField()


class VersionTranslation(BaseModel):
    version = ForeignKeyField(Version)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=30)

    class Meta:
        primary_key = CompositeKey("version", "lang")


# =========================================================================== #
#                                 Type models                                 #
# =========================================================================== #
class Type(BaseModel):
    id = IntegerField(primary_key=True)
    generation = IntegerField()


class TypeEfficacy(BaseModel):
    damage_type = ForeignKeyField(Type, related_name="attacker")
    target_type = ForeignKeyField(Type, related_name="defender")
    damage_factor = IntegerField()


class TypeSlot(BaseModel):
    first = ForeignKeyField(Type, related_name="primary")
    second = ForeignKeyField(Type, related_name="secondary")


class TypeTranslation(BaseModel):
    type = ForeignKeyField(Type)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=15)

    class Meta:
        primary_key = CompositeKey("type", "lang")


# =========================================================================== #
#                               Ability models                                #
# =========================================================================== #
class Ability(BaseModel):
    id = IntegerField(primary_key=True)
    generation = IntegerField()


class AbilityTranslation(BaseModel):
    ability = ForeignKeyField(Ability)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=20)
    effect = TextField()

    class Meta:
        primary_key = CompositeKey("ability", "lang")


# =========================================================================== #
#                                 Move models                                 #
# =========================================================================== #
class Move(BaseModel):
    id = IntegerField(primary_key=True)
    generation = IntegerField()
    type = ForeignKeyField(Type)
    power = IntegerField()
    pp = IntegerField()
    accuracy = IntegerField()
    priority = IntegerField()
    damage_class = CharField(max_length=10)


class MoveTranslation(BaseModel):
    move = ForeignKeyField(Move)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=20)
    effect = TextField()

    class Meta:
        primary_key = CompositeKey("move", "lang")


# =========================================================================== #
#                                Pokémon models                               #
# =========================================================================== #
class Pokemon(BaseModel):
    id = IntegerField(primary_key=True)
    base_xp = IntegerField()
    height = FloatField()
    weight = FloatField()
    national_id = IntegerField()
    # sprite = CharField(max_length=25)


class PokemonAbility(BaseModel):
    pokemon = ForeignKeyField(Pokemon)
    ability = ForeignKeyField(Ability)
    hidden = BooleanField()
    slot = IntegerField()


class PokemonTranslation(BaseModel):
    pokemon = ForeignKeyField(Pokemon)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=20)
    genus = CharField(max_length=20)

    class Meta:
        primary_key = CompositeKey("pokemon", "lang")


class PokemonMove(BaseModel):
    pokemon = ForeignKeyField(Pokemon)
    move = ForeignKeyField(Move)
