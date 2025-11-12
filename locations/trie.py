class SuffixTrieNode:
    def __init__(self):
        self.children = {}
        self.slug_end = None

class SuffixTrie:
    def __init__(self):
        self.root = SuffixTrieNode()

    def insert(self, slug):
        reversed_slug = slug[::-1]
        node = self.root
        for char in reversed_slug:
            if char not in node.children:
                node.children[char] = SuffixTrieNode()
            node = node.children[char]
        node.slug_end = slug

    def match_suffix(self, input_slug):
        reversed_input = input_slug[::-1]
        node = self.root
        longest_match = None

        for char in reversed_input:
            if char in node.children:
                node = node.children[char]
                if node.slug_end:
                    longest_match = node.slug_end  # keep updating to find the deepest match
            else:
                break

        return longest_match  # longest valid slug suffix
