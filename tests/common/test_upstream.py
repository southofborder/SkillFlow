"""Run references use explicit locations and survive moving their containing tree."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest
from skillflow.common.recording import canonical_sha256
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference


def sealed(directory):
    directory.mkdir(parents=True)
    value = {'identity': 'fixture-v1', 'schema_version': 1}
    value['manifest_sha256'] = canonical_sha256(value)
    (directory / 'manifest.json').write_text(json.dumps(value), encoding='utf-8')
    return value


def test_reference_moves_as_a_tree_without_absolute_identity(tmp_path):
    tree = tmp_path / 'analysis'; origin = tree / 'annotation'; owner = tree / 'propagation'
    manifest = sealed(origin)
    owner.mkdir()
    ref = make_run_reference(owner, origin)
    assert ref == {'path': '../annotation', 'manifest_sha256': manifest['manifest_sha256']}
    moved = tmp_path / 'relocated'
    shutil.move(str(tree), moved)
    assert resolve_run_reference(moved / 'propagation', ref) == moved / 'annotation'


@pytest.mark.parametrize('change', ['extra','backslash','empty','nonstring','digest'])
def test_reference_does_not_guess_or_accept_bad_locators(tmp_path, change):
    origin = tmp_path / 'annotation'; sealed(origin)
    ref = make_run_reference(tmp_path / 'propagation', origin)
    if change == 'extra': ref['identity'] = 'guess'
    if change == 'backslash': ref['path'] = '..\\annotation'
    if change == 'empty': ref['path'] = ''
    if change == 'nonstring': ref['path'] = 1
    if change == 'digest': ref['manifest_sha256'] = '0' * 64
    with pytest.raises(ValueError): resolve_run_reference(tmp_path / 'propagation', ref)


def test_missing_target_does_not_search_for_a_similar_run(tmp_path):
    sealed(tmp_path / 'annotation')
    ref = make_run_reference(tmp_path / 'propagation', tmp_path / 'annotation')
    ref['path'] = '../another-annotation'
    with pytest.raises(FileNotFoundError): resolve_run_reference(tmp_path / 'propagation', ref)


@pytest.mark.parametrize('mode', ['digest','duplicate'])
def test_changed_manifest_rejected(tmp_path, mode):
    origin = tmp_path / 'annotation'; manifest = sealed(origin)
    path = origin / 'manifest.json'
    if mode == 'digest': manifest['schema_version'] = 2; path.write_text(json.dumps(manifest), encoding='utf-8')
    else: path.write_text(json.dumps(manifest)[:-1] + ',"schema_version":1}', encoding='utf-8')
    with pytest.raises(ValueError): make_run_reference(tmp_path / 'propagation', origin)


def test_symlink_input_or_parent_rejected(tmp_path):
    origin = tmp_path / 'annotation'; sealed(origin)
    link = tmp_path / 'link'
    try: link.symlink_to(origin, target_is_directory=True)
    except OSError as error: pytest.skip('Symlink privilege unavailable: ' + str(error))
    with pytest.raises(ValueError, match='links'): checked_run_path(link)
    with pytest.raises(ValueError, match='links'): checked_run_path(link / 'manifest.json')
