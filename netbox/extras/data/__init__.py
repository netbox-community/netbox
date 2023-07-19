from .iata import IATA
from .iso_3166 import ISO_3166
from .un_locode import UN_LOCODE

CHOICE_SETS = {
    'IATA': IATA,
    'ISO_3166': ISO_3166,
    'UN_LOCODE': UN_LOCODE,
}
