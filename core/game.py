from core.entity import Ability, Role, Player, PlayerState, Fraction, Setting, Vote, NightMove
from typing import List, Optional, Set
from enum import Enum
from random import choice
from dataclasses import dataclass, field
from collections import Counter


class GameState(Enum):
    STARTING = 1
    ONGOING = 2
    FINISHED = 3


@dataclass
class PlayerStateChange:
    player: Player
    prev: Set[PlayerState]
    new: Set[PlayerState]


@dataclass
class Period:
    players: List[Player] = field(default_factory=list)
    player_state_changes: List[PlayerStateChange] = field(default_factory=list)


@dataclass
class Day(Period):
    votes: List[Vote] = field(default_factory=list)

    def get_player(self, nickname: str) -> Optional[Player]:
        for p in self.players:
            if p.nickname == nickname:
                return p


@dataclass
class Night(Period):
    players: List[Player] = field(default_factory=list)


test_setting = Setting(name='test setting name',
                       description='test setting description',
                       roles=[Role(name='шериф',
                                   description='test role sheriff',
                                   fraction=Fraction.CITY,
                                   abilities=[Ability.CHECK_ROLE]),
                              Role(name='мафия исполнитель',
                                   description='test role killer',
                                   fraction=Fraction.MAFIA,
                                   abilities=[Ability.KILL]),
                              Role(name='мафия блокер',
                                   description='test role blocker',
                                   fraction=Fraction.MAFIA,
                                   abilities=[Ability.BLOCK]),
                              Role(name='мафия сайленсер',
                                   description='test role silencer',
                                   fraction=Fraction.MAFIA,
                                   abilities=[Ability.SILENCE])
                              ]
                       )


class Game:
    def __init__(self, pool: List[str], setting_name: str = None):
        self.setting_name: str = setting_name
        if not self.setting_name:
            self.setting_name = 'default'
        self.pool: List[str] = pool
        self.state: GameState = GameState.STARTING
        self.days: List[Day] = list()
        self.nights: List[Night] = list()
        self.setting: Setting = test_setting  # TODO DISPATCH SETTING
        self.next_day_votes: Set[Vote] = set()
        self.next_night_moves: Set[NightMove] = set()

    def dispatch_setting(self):
        pass

    def get_current_day(self) -> Day:
        return self.days[-1]

    def get_current_night(self) -> Night:
        return self.nights[-1]

    def start(self):
        # TODO COMMENT
        _pool = self.pool.copy()
        day = Day()

        for role in self.setting.roles:
            selected_nickname = choice(_pool)
            day.players.append(Player(nickname=selected_nickname, role=role, status={PlayerState.ALIVE}))
            _pool.remove(selected_nickname)

        for n in _pool:
            day.players.append(Player(nickname=n, role=None, status={PlayerState.ALIVE}))

        self.days.append(day)
        self.state = GameState.ONGOING

    def start_day(self, remaining_players: List[Player]):
        self.days.append(Day(players=remaining_players, votes=list(self.next_day_votes)))
        self.next_day_votes = set()

    def vote(self, nickname: str, target: Optional[str] = None, jail_kill: Optional[bool] = None):
        jail_votes = [v for v in self.get_current_day().votes if v.jail_kill and v.initiator == nickname]
        jailed_players = [p for p in self.get_current_day().players if p.status == PlayerState.JAILED]
        target_votes = [v for v in self.get_current_day().votes if not v.jail_kill and v.initiator == nickname]

        # TODO COMMENT LOGIC
        if jail_kill:
            if len(jail_votes) > len(jailed_players):
                self.next_day_votes.add(Vote(initiator=nickname, target=nickname))
            else:
                self.get_current_day().votes.append(Vote(initiator=nickname, target=target, jail_kill=True))

        if len(target_votes) == 2:
            self.next_day_votes.add(Vote(initiator=nickname, target=nickname))
        elif target not in self.pool:
            self.get_current_day().votes.append(Vote(initiator=nickname, target=nickname))
        else:
            self.get_current_day().votes.append(Vote(initiator=nickname, target=target))

    def dispatch_day(self):
        # TODO JAIL LOGIC
        # TODO COMMENT
        target_votes = dict()
        for v in self.get_current_day().votes:
            target_votes[v.initiator] = v.target

        max_votecount = 0
        targets = list()
        for nick, votecount in Counter(target_votes.values()).items():
            if votecount > max_votecount:
                max_votecount = votecount
                targets = [nick]
            elif votecount == max_votecount:
                targets.append(nick)

        kicked_player = self.get_current_day().get_player(choice(targets))
        self.get_current_day().player_state_changes.append(PlayerStateChange(kicked_player, kicked_player.status, kicked_player.status.union([PlayerState.DEAD])))

    def start_night(self, remaining_players: List[Player]):
        self.nights.append(Night(players=remaining_players))

    def night_move(self, nickname: str, target: str, ability_name: str):
        pass

    def dispatch_night(self):
        pass
        # self.next_night_moves
