from fuzzywuzzy import process


class SuggestEngineWithFuzzy:
    fuzzyChoices = None

    def __init__(self, WORDS_FILE_PATH):
        with open(WORDS_FILE_PATH, "r") as f:
            self.fuzzyChoices = f.read().split("\n")

    def suggest(self, word):
        results = process.extract(word, self.fuzzyChoices)
        return [suggestCostTuple[0] for suggestCostTuple in results]
