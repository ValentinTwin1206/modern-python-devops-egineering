"""MongoDB repositories and application bootstrap."""

from gridfs import GridFSBucket
from fastapi import FastAPI
from pymongo import MongoClient

from .analysis_db import AnalysisDB
from .users_db import UsersDB


def bootstrap_db( app: FastAPI, client: MongoClient, database_name: str ) -> None:
	"""Initialize shared database resources and required indexes."""
	database = client[database_name]
	users_db = UsersDB(client)
	users_db.ensure_indexes()
	
    # Set shared resources in FastAPI app state
	app.state.mongo_client = client
	app.state.gridfs       = GridFSBucket(database)
	app.state.users_db     = users_db
	app.state.analysis_db  = AnalysisDB(client)
