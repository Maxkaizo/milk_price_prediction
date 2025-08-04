from datetime import datetime
from orchestration.tasks.check_file_availability import _is_file_available_logic

def test_future_date_returns_false():
    assert _is_file_available_logic(datetime(2099, 1, 1)) is False

def test_past_date_returns_false():
    assert _is_file_available_logic(datetime(2022, 1, 1)) is False
