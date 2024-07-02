from jsonpath_rw import parse
from pytest_check import check
from pytest_bdd import then, parsers
from requests import Response


@then(
    parsers.cfparse(
        "I get a {expected_status:Number} HTTP response code",
        extra_types=dict(Number=int)
    )
)
def check_status(response: Response, expected_status: int) -> None:
    with check:
        assert response.status_code == expected_status


@then(
    parsers.cfparse(
        '{value:String} is at {path:String} in the response body',
        extra_types=dict(String=str)
    ))
def check_value_in_response_body_at_path(response_body: dict, value: str, path: str) -> None:
    matches = parse(path).find(response_body)
    with check:
        assert matches, f'There are no matches for {value} at {path} in the response body'
        for match in matches:
            assert match.value == value, f'{match.value} is not the expected value, {value}, at {path}'
