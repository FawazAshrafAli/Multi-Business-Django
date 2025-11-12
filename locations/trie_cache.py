from .models import UniquePlace, UniqueDistrict, UniqueState
from .trie import SuffixTrie

_place_trie = None
_district_trie = None
_state_trie = None

def get_place_trie():
    global _place_trie
    if _place_trie is None:
        _place_trie = SuffixTrie()
        for p in UniquePlace.objects.all():
            _place_trie.insert(p.slug)
    return _place_trie

def get_district_trie():
    global _district_trie
    if _district_trie is None:
        _district_trie = SuffixTrie()
        for d in UniqueDistrict.objects.all():
            _district_trie.insert(d.slug)
    return _district_trie

def get_state_trie():
    global _state_trie
    if _state_trie is None:
        _state_trie = SuffixTrie()
        for s in UniqueState.objects.all():
            _state_trie.insert(s.slug)
    return _state_trie
