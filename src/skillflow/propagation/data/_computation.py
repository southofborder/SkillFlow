"""Private per-calculation reads and undo state; no persisted cache or protocol."""

from collections.abc import Mapping
from contextlib import contextmanager


class ComputationState:
    def __init__(self):
        self.enabled = False
        self.versions = {}
        self.changes = {}
        self.observers = []
        self.journals = []

    def version(self, key):
        return self.versions.get(key, 0)

    def read(self, key):
        for observed in self.observers:
            observed.setdefault(key, self.version(key))

    def remember(self, mapping, key):
        marker = (id(mapping), key)
        for journal in self.journals:
            if marker not in journal:
                journal[marker] = (mapping, key, key in mapping, mapping.get(key))

    def changed(self, key):
        if not self.enabled:
            return
        self.remember(self.versions, key)
        self.remember(self.changes, key)
        self.versions[key] = self.version(key) + 1
        self.changes[key] = None

    @contextmanager
    def observe(self):
        observed = {}
        self.observers.append(observed)
        try:
            yield observed
        finally:
            self.observers.pop()

    @contextmanager
    def transaction(self):
        journal = {}
        self.journals.append(journal)
        try:
            yield
        except Exception:
            reverted_versions = []
            for mapping, key, existed, old in reversed(tuple(journal.values())):
                if mapping is self.versions:
                    reverted_versions.append(key)
                if existed:
                    mapping[key] = old
                else:
                    mapping.pop(key, None)
            # A speculative descriptor read still records its dependency, but
            # cannot leave an uncommitted version that would requeue forever.
            for key in reverted_versions:
                for observed in self.observers:
                    if key in observed:
                        observed[key] = min(observed[key], self.version(key))
            raise
        finally:
            self.journals.pop()


class DataView(Mapping):
    """Resolve only the descriptors a structural query actually visits."""

    def __init__(self, registry):
        self.registry = registry

    def __getitem__(self, identity):
        if not self.registry.contains_data(identity):
            raise KeyError(identity)
        return self.registry._entry(identity).data

    def __iter__(self):
        return iter(self.registry.data_ids())

    def __len__(self):
        return len(self.registry)

    def __contains__(self, identity):
        return self.registry.contains_data(identity)

    def find_part(self, root, path):
        identity = self.registry._find_part(root, path)
        return None if identity is None else self[identity]
