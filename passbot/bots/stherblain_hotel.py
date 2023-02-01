from passbot.bots.base import Bot


class SaintHerblainBot(Bot):

    NAME = 'Saint Herblain - Hotel de ville'
    URL_HOMEPAGE = 'https://www.saint-herblain.fr/services-et-demarches/etat-civil-papiers-didentite-elections/carte-didentite-passeport'  # noqa

    group_id = 155113
    intervention_id = 2724111
    calendar_id = 338429
    api_key = '71a07e028193455a8b8fa1c7da526291'

    @property
    def URL_API(self):
        return f'https://www.clicrdv.com/api/v2/availabletimeslots?group_id={self.group_id}&promotions=0&appointments[0][intervention_id]={self.intervention_id}&appointments[0][calendar_id]={self.calendar_id}&apikey={self.api_key}'  # noqa

    def should_alert(self, content):
        return bool(content.get('availabletimeslots', False))
