from core.game import Game

testing_pool = ['lobziq', 'Fint', 'POJITOH', 'dispersion', 'r0ss0ha']
game = Game(testing_pool)
game.start()

sheriff = [p for p in game.get_current_day().players if p.role.name == 'шериф'][0]

game.vote('lobziq', 'Fint')
game.vote('lobziq', 'Fint')
game.vote('Fint', 'dispersion')
game.vote('Fint', 'dispersion')
game.vote('Fint', 'dispersion')
game.vote('dispersion', 'POJITOH')
game.vote('dispersion', 'dispersion')

game.night_move(sheriff.nickname, 'POJITOH')

game.dispatch_day()
game.start_night(Game.apply_player_state_changes(game.get_current_day().players, game.get_current_day().player_state_changes))

mafia = [p for p in game.get_current_day().players if p.role.name == 'мафия исполнитель'][0]
game.night_move(mafia.nickname, 'POJITOH')

game.dispatch_night()


pass
