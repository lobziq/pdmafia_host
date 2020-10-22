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

    def get_player(self, nickname: str) -> Optional[Player]:
        for p in self.players:
            if p.nickname == nickname:
                return p


@dataclass
class Day(Period):
    votes: List[Vote] = field(default_factory=list)


@dataclass
class Night(Period):
    moves: List[NightMove] = field(default_factory=list)


test_setting = Setting(name='test setting name',
                       description='test setting description',
                       roles=[Role(name='шериф',
                                   description='test role sheriff',
                                   fraction=Fraction.CITY,
                                   abilities=[Ability.CHECK_FRACTION]),
                              Role(name='медик',
                                   description='test role medic',
                                   fraction=Fraction.CITY,
                                   abilities=[Ability.HEAL]),
                              Role(name='мафия исполнитель',
                                   description='test role killer',
                                   fraction=Fraction.MAFIA,
                                   abilities=[Ability.KILL]),
                              Role(name='мафия блокер',
                                   description='test role blocker',
                                   fraction=Fraction.MAFIA,
                                   abilities=[Ability.BLOCK]),
                              Role(name='мафия чекер на активность',
                                   description='test role check_activity',
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
        self.night_moves: List[NightMove] = list()

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

        # TODO изящный однострочник сюда
        max_votecount = 0
        targets = list()
        for nick, votecount in Counter(target_votes.values()).items():
            if votecount > max_votecount:
                max_votecount = votecount
                targets = [nick]
            elif votecount == max_votecount:
                targets.append(nick)

        kicked_player = self.get_current_day().get_player(choice(targets))
        self.get_current_day().player_state_changes.append(PlayerStateChange(kicked_player, kicked_player.status, {PlayerState.DEAD}))

    @staticmethod
    def apply_player_state_changes(players: List[Player], player_state_changes: List[PlayerStateChange]):
        changed_players = players.copy()
        for sc in player_state_changes:
            if sc.player in changed_players and PlayerState.DEAD in sc.new:
                changed_players.remove(sc.player)

        return changed_players

    def start_night(self, remaining_players: List[Player]):
        self.nights.append(Night(players=remaining_players))

        # все состояния кроме "ЖИВОЙ" снимаются, был в клетке - вышел, сало - снимается
        for p in self.get_current_night().players:
            p.status = {PlayerState.ALIVE}

    def night_move(self, nickname: str, target: str, ability_name: str = None):
        if not self.get_current_day().get_player(nickname):
            return

        if not self.get_current_day().get_player(nickname).role:
            return

        self.night_moves = [move for move in self.night_moves if move.initiator != nickname]
        if self.get_current_day().get_player(target):
            self.night_moves.append(NightMove(initiator=nickname, target=target, ability=self.get_current_day().get_player(nickname).role.abilities[0]))

    @staticmethod
    def get_move_targets(moves: List[NightMove]) -> List[str]:
        return [a.target for a in moves]

    def dispatch_night(self):
        # мертвые не ходят
        self.get_current_night().night_moves = [m for m in self.night_moves if self.get_current_night().get_player(m.initiator)]

        # блок первым
        performed_moves: List[NightMove] = [m for m in self.night_moves if m.ability == Ability.BLOCK]

        # теперь килл маньяка, если он не в блоке
        for move in [m for m in self.night_moves if m.ability == Ability.PRIORITY_KILL and m.initiator not in Game.get_move_targets(performed_moves)]:
            performed_moves.append(move)

        # остальной пул абилок, которые проходят, если в чела не въехал маньяк или он не в блоке
        for move in [m for m in self.night_moves if m.ability in [Ability.KILL, Ability.SECONDARY_KILL, Ability.HEAL,
                                                                  Ability.CHECK_ROLE, Ability.CHECK_ACTIVITY, Ability.CHECK_FRACTION,
                                                                  Ability.SILENCE, Ability.SURVEIL_IN, Ability.SURVEIL_OUT]]:
            # для читаемости отдельно
            if move.initiator not in Game.get_move_targets(performed_moves):
                performed_moves.append(move)

        for nickname in Game.get_move_targets([m for m in performed_moves if m.ability in [Ability.KILL, Ability.SECONDARY_KILL, Ability.PRIORITY_KILL]]):
            # TODO возвращать резалты

            if nickname not in Game.get_move_targets([m for m in performed_moves if m.ability in [Ability.HEAL]]):
                # чувака убивали и не похилили - меняем ему состояние на "МЕРТВЫЙ"
                player = self.get_current_night().get_player(nickname)
                self.get_current_night().player_state_changes.append(PlayerStateChange(player, player.status, {PlayerState.DEAD}))
            else:
                pass

        for nickname in Game.get_move_targets([m for m in performed_moves if m.ability == Ability.SILENCE]):
            player = self.get_current_night().get_player(nickname)

