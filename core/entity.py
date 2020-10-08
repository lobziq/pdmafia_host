from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set


class Fraction(Enum):
    CITY = 1
    MAFIA = 2
    NEUTRAL = 3


class PlayerState(Enum):
    ALIVE = 1
    DEAD = 2
    SILENCED = 3
    JAILED = 4


class Ability(Enum):
    KILL = 1
    HEAL = 2
    SILENCE = 3
    JAIL = 4
    BLOCK = 5
    SURVEIL_IN = 6
    SURVEIL_OUT = 7
    REDIRECTION = 8
    CHECK_ACTIVITY = 9
    CHECK_FRACTION = 10
    CHECK_ROLE = 11
    PRIORITY_KILL = 12


@dataclass
class Role:
    name: str
    description: str
    abilities: List[Ability]
    fraction: Fraction


@dataclass
class Player:
    nickname: str
    role: Optional[Role]
    status: Set[PlayerState] = field(default_factory=set)


@dataclass(unsafe_hash=True)
class Vote:
    initiator: str
    target: Optional[str] = None
    jail_kill: Optional[bool] = None


@dataclass
class NightMove:
    initiator: Player
    targets: List[Player]
    ability: List[Ability]


@dataclass
class Setting:
    name: str
    description: str
    roles: List[Role] = field(default_factory=list)
