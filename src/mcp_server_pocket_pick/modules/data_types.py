from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .constants import DEFAULT_SQLITE_DATABASE_PATH


class AddCommand(BaseModel):
    text: str
    tags: List[str] = []
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class FindCommand(BaseModel):
    text: str
    mode: str = "substr"  # substr | fts | glob | regex | exact
    limit: int = 5
    info: bool = False
    tags: List[str] = []
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class ListCommand(BaseModel):
    tags: List[str] = []
    limit: int = 100
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class ListTagsCommand(BaseModel):
    limit: int = 1000
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class RemoveCommand(BaseModel):
    id: str
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class GetCommand(BaseModel):
    id: str
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class BackupCommand(BaseModel):
    backup_path: Path
    db_path: Path = DEFAULT_SQLITE_DATABASE_PATH


class PocketItem(BaseModel):
    id: str
    created: datetime
    text: str
    tags: List[str]