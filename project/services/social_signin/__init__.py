from project.services.social_signin import facebook
from models import social_signins


class SocialSignin:
    class Invalid(Exception):
        pass

    def verify(self, social_type, token):
        social_id = self.verifiers[social_type](token)
        if social_id is None:
            raise self.Invalid('%s validation was invalid.' % social_type)

        user_data = social_signins.get_user_from_social_id(social_type, social_id)

        if user_data is None:
            raise self.Invalid('Social account not associated with a Founderati account')

        return user_data

    verifiers = {'facebook': facebook.verify}

SocialSignin = SocialSignin()
