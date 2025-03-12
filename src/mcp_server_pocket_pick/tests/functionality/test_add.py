import pytest
import tempfile
import os
from pathlib import Path
import json
import sqlite3
from ...modules.data_types import AddCommand, PocketItem
from ...modules.functionality.add import add

@pytest.fixture
def temp_db_path():
    # Create a temporary file path
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Return the path as a Path object
    yield Path(path)
    
    # Clean up the temp file after test
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def read_only_db_path():
    # Create a temporary file path
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Make it read-only
    os.chmod(path, 0o444)
    
    # Return the path as a Path object
    yield Path(path)
    
    # Clean up the temp file after test
    if os.path.exists(path):
        os.chmod(path, 0o666)  # Make writable again for deletion
        os.unlink(path)

def test_add_simple(temp_db_path):
    # Create a command to add a simple item
    command = AddCommand(
        text="This is a test item",
        tags=["test", "example"],
        db_path=temp_db_path
    )
    
    # Add the item
    result = add(command)
    
    # Verify result is a PocketItem
    assert isinstance(result, PocketItem)
    assert result.text == "This is a test item"
    assert result.tags == ["test", "example"]
    assert result.id is not None
    
    # Verify item was added to the database
    db = sqlite3.connect(temp_db_path)
    cursor = db.execute("SELECT id, text, tags FROM POCKET_PICK")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == result.id
    assert row[1] == "This is a test item"
    
    # Verify tags were stored as JSON
    stored_tags = json.loads(row[2])
    assert stored_tags == ["test", "example"]
    
    # Verify no more rows exist
    assert cursor.fetchone() is None
    
    db.close()

def test_add_with_tag_normalization(temp_db_path):
    # Create a command with tags that need normalization
    command = AddCommand(
        text="Item with tags to normalize",
        tags=["TAG", "with space", "under_score"],
        db_path=temp_db_path
    )
    
    # Add the item
    result = add(command)
    
    # Verify tags were normalized
    assert result.tags == ["tag", "with-space", "under-score"]
    
    # Verify in database
    db = sqlite3.connect(temp_db_path)
    cursor = db.execute("SELECT tags FROM POCKET_PICK")
    row = cursor.fetchone()
    
    stored_tags = json.loads(row[0])
    assert stored_tags == ["tag", "with-space", "under-score"]
    
    db.close()

def test_add_empty_tags(temp_db_path):
    # Create a command with no tags
    command = AddCommand(
        text="Item with no tags",
        tags=[],
        db_path=temp_db_path
    )
    
    # Add the item
    result = add(command)
    
    # Verify empty tags list
    assert result.tags == []
    
    # Verify in database
    db = sqlite3.connect(temp_db_path)
    cursor = db.execute("SELECT tags FROM POCKET_PICK")
    row = cursor.fetchone()
    
    stored_tags = json.loads(row[0])
    assert stored_tags == []
    
    db.close()

def test_add_long_text(temp_db_path):
    # Create a command with very long text
    long_text = "x" * 10000  # 10,000 character string
    command = AddCommand(
        text=long_text,
        db_path=temp_db_path
    )
    
    # Add the item
    result = add(command)
    
    # Verify text was stored correctly
    assert result.text == long_text
    
    # Verify in database
    db = sqlite3.connect(temp_db_path)
    cursor = db.execute("SELECT text FROM POCKET_PICK")
    row = cursor.fetchone()
    
    assert row[0] == long_text
    
    db.close()

def test_add_special_characters(temp_db_path):
    # Create a command with special characters in text and tags
    special_text = "Special chars: !@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    special_tag = "tag-with-!@#$%^"
    
    command = AddCommand(
        text=special_text,
        tags=[special_tag],
        db_path=temp_db_path
    )
    
    # Add the item
    result = add(command)
    
    # Verify text was stored correctly
    assert result.text == special_text
    
    # Normalized tag should convert to lowercase and replace spaces/underscores with dashes
    normalized_tag = special_tag.lower()
    assert result.tags == [normalized_tag]
    
    # Verify in database
    db = sqlite3.connect(temp_db_path)
    cursor = db.execute("SELECT text, tags FROM POCKET_PICK")
    row = cursor.fetchone()
    
    assert row[0] == special_text
    stored_tags = json.loads(row[1])
    assert stored_tags == [normalized_tag]
    
    db.close()

def test_add_error_handling(read_only_db_path):
    # Create a command that will trigger an error (read-only DB)
    command = AddCommand(
        text="This should cause an error",
        db_path=read_only_db_path
    )
    
    # Add the item should raise an exception
    with pytest.raises(Exception):
        add(command)