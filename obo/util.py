from collections import Mapping
from collections import MutableSet


# TODO make sorted (replace internal dict with sorted collection)
class StanzaSet(Mapping, MutableSet):
    def __init__(self, stanzas = ()):
        self._stanzas = {}
        for stanza in stanzas:
            self.add(stanza)

    def discard(self, stanza):
        self._stanzas.pop(stanza.id, None)

    def __getitem__(self, id_):
        return self._stanzas[id_]

    def add(self, stanza):
        self._stanzas[stanza.id] = stanza

    def __len__(self):
        return len(self._stanzas)

    def __iter__(self):
        return iter(self._stanzas.values())
