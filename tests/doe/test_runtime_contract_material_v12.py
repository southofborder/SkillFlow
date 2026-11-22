"""DOE material binds the complete supported runtime vocabulary."""
import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.doe.material import prepare_doe_material, validate_doe_material
from tests.doe.test_material import _versions_fixture


@pytest.mark.parametrize('change', ['omit_inventory', 'alter_inventory', 'extra_key'])
def test_rehashed_incomplete_or_altered_operation_contract_is_rejected(change):
    material = prepare_doe_material(_versions_fixture()).model_dump(mode='json')
    contract = material['runtime_contract']
    if change == 'omit_inventory':
        contract.pop('operation_contract')
    elif change == 'alter_inventory':
        contract['operation_contract'] = {'operations': []}
    else:
        contract['unreviewed_extension'] = 'accept any operation'
    contract['sha256'] = canonical_sha256({key: value for key, value in contract.items() if key != 'sha256'})
    with pytest.raises(ValueError, match='runtime contract'):
        validate_doe_material(material)
