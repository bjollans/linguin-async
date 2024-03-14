import boto3

_get_cache = {}
_has_cache = []


class VocabDB:
    TABLE_BASE_NAME = "linguin-vocab"
    REGION = 'eu-west-1'

    def __init__(self, from_lang) -> None:
        self.from_lang = from_lang
        self.table_name = f"{self.TABLE_BASE_NAME}-{from_lang}"
        self.db = boto3.resource(
            'dynamodb', region_name=self.REGION).Table(self.table_name)

    def _get(self, word):
        if word not in _get_cache:
            if len(word) == 0:
                return None
            response = self.db.get_item(Key={'word': word})
            if not 'Item' in response:
                return None
            _get_cache[word] = response['Item']
        return _get_cache[word]

    def get_translation(self, word, to_lang):
        item = self._get(word)
        return item[to_lang] if to_lang in item else None

    def has(self, word):
        if word in _has_cache:
            return True
        if self._get(word):
            _has_cache.append(word)
            return True
        return False

    def write_words(self, words: list[str]):
        for word in words:
            self.write_word(word)

    def write_word(self, word):
        if not self.has(word):
            self.db.put_item(Item={'word': word})

    def write_translation(self, word, to_lang, translation):
        if not self.has(word):
            self.write_word(word)
        item = self._get(word)

        item[to_lang] = translation

        _get_cache[word] = item
        self.db.put_item(Item=item)
