from FlapPyBird.flappy import GameClient
import Bot.bot as bot

def main():
    #game.doStuff(bot)
    game = GameClient()
    bot.play(game)

if __name__ == '__main__':
    main()

