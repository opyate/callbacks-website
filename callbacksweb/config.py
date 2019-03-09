# -*- coding: utf-8 -*-
import os


class Config(object):

    DATABASE_URL = None

    # from https://stackoverflow.com/a/35261091/51280
    # https://gist.github.com/SpainTrain/6bf5896e6046a5d9e7e765d0defc8aa8
    def get(self, name):
        cls = self.__class__.__name__
        var = os.environ.get(name)
        print('var env={0} {1}={2}'.format(cls, name, var))
        return var


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    DATABASE_URL = "postgresql://doadmin:r9iusuq6n6b0ivzp@db-postgresql-lon1-80165-do-user-3001284-0.db.ondigitalocean.com:25060/callbacks?sslmode=require"


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DATABASE_URL = "postgres://juanuys@localhost:5432/callbacks"

class TestConfig(Config):
    ENV = 'test'
    TESTING = True
    DEBUG = True
    # not sqlite, because we use Postgresql dialects in the models (e.g. UUID, JSONB)
    #DATABASE_URL = 'sqlite:///'
