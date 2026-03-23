from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflector import Inflector


class PhraseInflector:
    def __init__(self, infector:Inflector):
        self._inflector = infector

