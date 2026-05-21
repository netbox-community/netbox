from model_bakery.recipe import Recipe, foreign_key, seq

from circuits.choices import CircuitStatusChoices

#
# Provider
#

provider = Recipe(
    'circuits.Provider',
    name=seq('Provider '),
    slug=seq('provider-'),
)

#
# CircuitType
#

circuit_type = Recipe(
    'circuits.CircuitType',
    name=seq('Circuit Type '),
    slug=seq('circuit-type-'),
)

#
# ProviderAccount
#

provider_account = Recipe(
    'circuits.ProviderAccount',
    name=seq('Provider Account '),
    provider=foreign_key(provider),
    account=seq('ACCT-'),
)

#
# ProviderNetwork
#

provider_network = Recipe(
    'circuits.ProviderNetwork',
    name=seq('Provider Network '),
    provider=foreign_key(provider),
)

#
# Circuit
#

circuit = Recipe(
    'circuits.Circuit',
    cid=seq('CID-'),
    provider=foreign_key(provider),
    type=foreign_key(circuit_type),
    status=CircuitStatusChoices.STATUS_ACTIVE,
)

active_circuit = circuit.extend(
    status=CircuitStatusChoices.STATUS_ACTIVE,
)

planned_circuit = circuit.extend(
    status=CircuitStatusChoices.STATUS_PLANNED,
)

offline_circuit = circuit.extend(
    status=CircuitStatusChoices.STATUS_OFFLINE,
)
