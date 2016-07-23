from peewee import Model
from peewee import TextField
from peewee import CharField
from peewee import IntegerField
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
#                                Pokémon models                               #
# =========================================================================== #
class Pokemon(BaseModel):
    id = IntegerField(primary_key=True)
    xp = IntegerField()
    height = IntegerField()
    weight = IntegerField()
    sprite = CharField(max_length=25)


class PokemonTranslation(BaseModel):
    pokemon = ForeignKeyField(Pokemon)
    lang = ForeignKeyField(Language)
    name = CharField(max_length=20)


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
