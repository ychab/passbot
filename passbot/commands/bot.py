from passport.bots.stherblain_hotel import SaintHerblainBot

bots = [
    SaintHerblainBot,
]


def start_bots():
    for bot_klass in bots:
        bot = bot_klass()
        bot.start()


if __name__ == '__main__':
    start_bots()
