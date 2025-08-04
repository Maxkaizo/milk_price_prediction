from unittest.mock import patch
from orchestration.tasks.notify_telegram import notify_telegram_fn

@patch("orchestration.tasks.notify_telegram.requests.post")
def test_notify_telegram_post_called(mock_post):
    mock_post.return_value.status_code = 200

    # Llama a la función directamente, no al task
    notify_telegram_fn("Test message")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "Test message" in kwargs["json"]["text"]
