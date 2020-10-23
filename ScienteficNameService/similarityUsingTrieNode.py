from joblib.numpy_pickle_utils import xrange


class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.word = word

class WordSearcherWithTrieNode:
    trie=None
    def __init__(self, WORDS_FILE_PATH):
        self.trie = TrieNode()
        for word in open(WORDS_FILE_PATH, "r").read().split("\n"):
            self.trie.insert( word )

    def suggest(self, word):
        currentRow = range( len(word) + 1 )
        maxCost = len(word) // 4 #dynamic value to adjust the max cost.
        if (maxCost > 8): maxCost = 5
        if (maxCost < 2): maxCost = 2
        results = []

        for letter in self.trie.children:
            self.searchRecursive(self.trie.children[letter], letter, word, currentRow,results, maxCost )
        return [suggestCostTuple[0] for suggestCostTuple in sorted(results, key=lambda x:x[1])]

    def searchRecursive(self, node, letter, word, previousRow, results, maxCost ):

        columns = len( word ) + 1
        currentRow = [ previousRow[0] + 1 ]

        for column in xrange( 1, columns ):
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1
            if word[column - 1] != letter:
                replaceCost = previousRow[ column - 1 ] + 1
            else:
                replaceCost = previousRow[ column - 1 ]
            currentRow.append( min( insertCost, deleteCost, replaceCost ) )

        if currentRow[-1] <= maxCost and node.word != None:
            results.append( (node.word, currentRow[-1] ) )

        if min( currentRow ) <= maxCost:
            for letter in node.children:
                self.searchRecursive(node.children[letter], letter, word, currentRow, results, maxCost )

