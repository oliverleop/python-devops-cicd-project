import pytest
import requests
from pytest_mock import MockerFixture

from simple_http_checker.checker import check_urls


def test_check_urls_success(mocker):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)

    mock_response.status_code = 200
    mock_response.resason = "OK"
    mock_response.ok = True
    mock_request_get.return_value = mock_response

    urls = ["http://example.com"]
    results = check_urls(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results == {urls[0]: "200 OK"}


def test_check_urls_client_error(mocker: MockerFixture):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)

    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response.ok = False
    mock_request_get.return_value = mock_response

    urls = ["http://example.com/nonexistent"]
    results = check_urls(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results == {urls[0]: "404 Not Found"}


@pytest.mark.parametrize(
    "error_exception, expected_status",
    [
        (requests.exceptions.Timeout, "Timeout"),
        (requests.exceptions.ConnectionError, "Connection Error"),
        (requests.exceptions.RequestException, "Request Exception: RequestException"),
    ],
)
def test_check_urls_request_exception(
    mocker: MockerFixture,
    error_exception: type[requests.RequestException],
    expected_status: str,
):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_request_get.side_effect = error_exception(f"Simulated {expected_status}")

    urls = ["http://example.com/nonexistent"]
    results = check_urls(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results == {urls[0]: expected_status}


def test_check_urls_with_multiple_urls(mocker: MockerFixture):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    # OK response for first URL
    mock_response_ok = mocker.MagicMock(spec=requests.Response)
    mock_response_ok.status_code = 200
    mock_response_ok.reason = "OK"
    mock_response_ok.ok = True

    # Timeout for second URL
    timeout_exception = requests.exceptions.Timeout("Simulated Timeout")

    # 500 Server Error for third URL
    mock_response_server_error = mocker.MagicMock(spec=requests.Response)
    mock_response_server_error.status_code = 500
    mock_response_server_error.reason = "Internal Server Error"
    mock_response_server_error.ok = False

    mock_request_get.side_effect = [
        mock_response_ok,
        timeout_exception,
        mock_response_server_error,
    ]

    urls = [
        "http://example.com",
        "http://example.com/timeout",
        "http://example.com/server-error",
    ]

    results = check_urls(urls)

    assert results["http://example.com"] == "200 OK"
    assert results["http://example.com/timeout"] == "Timeout"
    assert results["http://example.com/server-error"] == "500 Internal Server Error"
