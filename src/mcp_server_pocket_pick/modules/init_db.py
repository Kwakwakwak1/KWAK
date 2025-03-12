import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with POCKET_PICK table"""
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing database at {db_path}")
    # Ensure the directory exists
    if not db_path.parent.exists():
        logger.info(f"Creating directory {db_path.parent}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    db = sqlite3.connect(str(db_path))
    
    # Enable foreign keys
    db.execute("PRAGMA foreign_keys = ON")
    
    # Create the POCKET_PICK table
    db.execute("""
    CREATE TABLE IF NOT EXISTS POCKET_PICK (
        id TEXT PRIMARY KEY,
        created TIMESTAMP NOT NULL,
        text TEXT NOT NULL,
        tags TEXT NOT NULL
    )
    """)
    
    # Create indexes for efficient searching
    db.execute("CREATE INDEX IF NOT EXISTS idx_pocket_pick_created ON POCKET_PICK(created)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_pocket_pick_text ON POCKET_PICK(text)")
    
    # Create FTS5 virtual table for full-text search
    try:
        db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pocket_pick_fts USING fts5(
            text,
            content='POCKET_PICK',
            content_rowid='rowid'
        )
        """)
        
        # Create triggers to keep FTS index up to date
        db.execute("""
        CREATE TRIGGER IF NOT EXISTS pocket_pick_ai AFTER INSERT ON POCKET_PICK
        BEGIN
            INSERT INTO pocket_pick_fts(rowid, text) VALUES (new.rowid, new.text);
        END
        """)
        
        db.execute("""
        CREATE TRIGGER IF NOT EXISTS pocket_pick_ad AFTER DELETE ON POCKET_PICK
        BEGIN
            INSERT INTO pocket_pick_fts(pocket_pick_fts, rowid, text) VALUES('delete', old.rowid, old.text);
        END
        """)
        
        db.execute("""
        CREATE TRIGGER IF NOT EXISTS pocket_pick_au AFTER UPDATE ON POCKET_PICK
        BEGIN
            INSERT INTO pocket_pick_fts(pocket_pick_fts, rowid, text) VALUES('delete', old.rowid, old.text);
            INSERT INTO pocket_pick_fts(rowid, text) VALUES (new.rowid, new.text);
        END
        """)
        
        # Rebuild FTS index if needed (for existing data)
        db.execute("""
        INSERT OR IGNORE INTO pocket_pick_fts(rowid, text)
        SELECT rowid, text FROM POCKET_PICK
        """)
        
    except sqlite3.OperationalError as e:
        # If FTS5 is not available, log a warning but continue
        logger.warning(f"FTS5 extension not available: {e}. Full-text search will fallback to basic search.")
    
    # Commit changes
    db.commit()
    
    return db

def normalize_tag(tag: str) -> str:
    """
    Normalize tags:
    - lowercase
    - trim whitespace
    - replace spaces and underscores with dashes
    """
    tag = tag.lower().strip()
    return tag.replace(' ', '-').replace('_', '-')

def normalize_tags(tags: list[str]) -> list[str]:
    """Apply normalization to a list of tags"""
    return [normalize_tag(tag) for tag in tags]