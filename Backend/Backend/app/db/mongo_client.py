# app/db/mongo_client.py

import os

from pymongo import MongoClient
from pymongo.database import Database


class MongoDBClient:
    """
    MongoDB connection manager.

    Future production database.
    """

    def __init__(self):

        self.mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017"
        )

        self.database_name = os.getenv(
            "MONGODB_DATABASE",
            "live_tutor"
        )

        self.client = None
        self.db = None

    # ----------------------------
    # CONNECT
    # ----------------------------
    def connect(self) -> Database:

        if self.client is None:

            self.client = MongoClient(
                self.mongo_uri
            )

            self.db = self.client[
                self.database_name
            ]

        return self.db

    # ----------------------------
    # GET DATABASE
    # ----------------------------
    def get_database(self) -> Database:

        if self.db is None:
            return self.connect()

        return self.db

    # ----------------------------
    # CLOSE
    # ----------------------------
    def close(self):

        if self.client:
            self.client.close()
            self.client = None
            self.db = None


# Singleton instance
mongo_client = MongoDBClient()