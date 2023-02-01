#!/usr/bin/env python

if __name__ == '__main__':
    from passbot.bots.stherblain_hotel import SaintHerblainBot

    bots = [
        SaintHerblainBot,
    ]

    for bot_klass in bots:
        bot = bot_klass()
        bot.start()
