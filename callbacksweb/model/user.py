class User(object):

    def __init__(self, row) -> None:
        super().__init__()
        self.id = row[0]
        self.user_id = row[1]
        self.api_key = row[2]

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)
