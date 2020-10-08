from core.game import Game

testing_pool = ['lobziq', 'Fint', 'POJITOH', 'dispersion']
game = Game(testing_pool)
game.start()

game.vote('lobziq', 'Fint')
game.vote('lobziq', 'Fint')
game.vote('Fint', 'dispersion')
game.vote('Fint', 'dispersion')
game.vote('Fint', 'dispersion')
game.vote('dispersion', 'POJITOH')
game.vote('dispersion', 'dispersion')

print(game.dispatch_day())
print(game.start_night(game.get_current_day().players))

pass
