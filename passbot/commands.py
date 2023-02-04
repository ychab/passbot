import logging

from passbot.bots.stherblain_hotel import SaintHerblainBot

logger = logging.getLogger(__name__)


def start_bots():
    bots = [
        SaintHerblainBot,
    ]

    for bot_klass in bots:
        bot = bot_klass()

        logger.info(f'Starting bot {bot.NAME}...')
        bot.start()
        logger.info(f'Ending bot {bot.NAME}')
