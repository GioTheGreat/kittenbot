import betterconf.caster
from betterconf import field, Config


class PidorConfig(Config):
    token: str = field("token")
    probability: float = field("probability", default=0.5, caster=betterconf.caster.FloatCaster())
