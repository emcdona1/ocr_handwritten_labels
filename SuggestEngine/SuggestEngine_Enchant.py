import enchant


class SuggestEngineWithEnchant:
    plantDict = None

    def __init__(self, WORDS_FILE_PATH):
        self.plantDict = enchant.PyPWL(WORDS_FILE_PATH)

    def suggest(self, word):
        return self.plantDict.suggest(word)
