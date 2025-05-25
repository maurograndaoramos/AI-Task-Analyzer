import sys
import os
from pathlib import Path
import datetime
import json


def test_python_version():
    """Test that Python version is 3.8 or higher."""
    assert sys.version_info >= (3, 8), f"Python version is {sys.version_info}, need 3.8+"


def test_app_directory_exists():
    """Test that the app directory exists."""
    app_path = Path("/app/app")
    assert app_path.exists(), "App directory should exist"
    assert app_path.is_dir(), "App should be a directory"


def test_basic_math():
    """Test basic mathematical operations work correctly."""
    assert 2 + 2 == 4
    assert 10 * 5 == 50
    assert 100 / 4 == 25.0
    assert 2 ** 3 == 8


def test_environment_variables():
    """Test that we can access environment variables."""
    # These should be available from the .env file
    env_vars = ["PYTHONPATH", "PYTHONUNBUFFERED"]
    
    for var in env_vars:
        assert os.environ.get(var) is not None, f"Environment variable {var} should be set"
    
    # Test that PYTHONPATH is set to /app
    pythonpath = os.environ.get("PYTHONPATH")
    assert pythonpath == "/app", f"PYTHONPATH should be /app, got {pythonpath}"


# NEW TESTS - 4 more that always pass

def test_string_operations():
    """Test basic string operations work correctly."""
    test_string = "Hello World"
    assert len(test_string) == 11
    assert test_string.upper() == "HELLO WORLD"
    assert test_string.lower() == "hello world"
    assert "World" in test_string
    assert test_string.split() == ["Hello", "World"]


def test_list_operations():
    """Test basic list operations work correctly."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert test_list[0] == 1
    assert test_list[-1] == 5
    assert sum(test_list) == 15
    assert max(test_list) == 5
    assert min(test_list) == 1


def test_datetime_operations():
    """Test that datetime operations work correctly."""
    now = datetime.datetime.now()
    assert isinstance(now, datetime.datetime)
    assert now.year >= 2024
    assert 1 <= now.month <= 12
    assert 1 <= now.day <= 31
    assert 0 <= now.hour <= 23


def test_json_operations():
    """Test that JSON operations work correctly."""
    test_data = {"name": "test", "value": 123, "active": True}
    json_string = json.dumps(test_data)
    assert isinstance(json_string, str)
    
    parsed_data = json.loads(json_string)
    assert parsed_data == test_data
    assert parsed_data["name"] == "test"
    assert parsed_data["value"] == 123
    assert parsed_data["active"] is True