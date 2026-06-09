from unittest.mock import patch, MagicMock
import os
import pytest
from datetime import datetime
from propaganda_bot import is_quiet_hour, generate_schedule, load_quotes, send_to_discord

def test_is_quiet_hour_standard_range():
    # Range 23:00 - 08:00
    assert is_quiet_hour(23, 23, 8) is True
    assert is_quiet_hour(0, 23, 8) is True
    assert is_quiet_hour(7, 23, 8) is True
    assert is_quiet_hour(8, 23, 8) is False
    assert is_quiet_hour(12, 23, 8) is False
    assert is_quiet_hour(22, 23, 8) is False

def test_is_quiet_hour_daytime_range():
    # Range 14:00 - 16:00
    assert is_quiet_hour(14, 14, 16) is True
    assert is_quiet_hour(15, 14, 16) is True
    assert is_quiet_hour(16, 14, 16) is False
    assert is_quiet_hour(10, 14, 16) is False

def test_generate_schedule_respects_quiet_hours():
    # Test if all generated timestamps are outside quiet hours
    count = 10
    schedule = generate_schedule(count)
    assert len(schedule) == count
    
    from propaganda_bot import QUIET_HOURS_START, QUIET_HOURS_END
    for timestamp in schedule:
        assert is_quiet_hour(timestamp.hour, QUIET_HOURS_START, QUIET_HOURS_END) is False

def test_generate_schedule_sorted():
    schedule = generate_schedule(5)
    assert schedule == sorted(schedule)

def test_load_quotes_success(tmp_path):
    # Create a temporary quotes file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_quotes.txt"
    p.write_text("Quote 1\nQuote 2\n\nQuote 3  ", encoding="utf-8")
    
    with patch("propaganda_bot.QUOTES_FILE", str(p)):
        quotes = load_quotes()
        assert quotes == ["Quote 1", "Quote 2", "Quote 3"]

def test_load_quotes_missing_file():
    with patch("propaganda_bot.QUOTES_FILE", "non_existent_file.txt"):
        with patch("os.path.exists", return_value=False):
            quotes = load_quotes()
            assert quotes == []

@patch("requests.post")
def test_send_to_discord_success(mock_post):
    # Mock a successful response (204 No Content)
    mock_post.return_value.status_code = 204
    
    with patch("propaganda_bot.WEBHOOK_URL", "http://fake-webhook.com"):
        send_to_discord("Test Quote", remaining_today=2)
    
    # Verify requests.post was called correctly
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://fake-webhook.com"
    assert "Test Quote" in kwargs["json"]["embeds"][0]["description"]

@patch("requests.post")
def test_send_to_discord_failure(mock_post):
    # Mock a failed response (e.g., 404)
    mock_post.return_value.status_code = 404
    mock_post.return_value.text = "Not Found"
    
    with patch("propaganda_bot.WEBHOOK_URL", "http://fake-webhook.com"):
        # This should not raise an exception but print an error
        send_to_discord("Test Quote")
    
    mock_post.assert_called_once()
