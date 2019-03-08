

class Callback(object):

    def __init__(self, row) -> None:
        super().__init__()
        self.id = row[0]
        self.url = row[1]
        self.payload = row[2]
        self.headers = row[3]
        self.http_method = row[4]
        self.shard = row[5]
        self.ts = row[6]
        self.status = row[7]
        self.user_id = row[8]

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)



