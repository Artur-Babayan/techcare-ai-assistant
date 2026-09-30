import pytest

from app.validators import ResponseValidationError, parse_llm_json, validate_assistant_response


def valid_payload() -> dict[str, object]:
    return {"client_reply": "Здравствуйте!", "upsell_hint": "", "used_kb_ids": ["kb_005"], "flags": ["no_upsell"]}


def test_valid_json_and_response() -> None:
    payload = parse_llm_json('```json\n{"client_reply":"Здравствуйте!","upsell_hint":"","used_kb_ids":["kb_005"],"flags":["no_upsell"]}\n```')
    assert validate_assistant_response(payload, {"kb_005"}).client_reply == "Здравствуйте!"


@pytest.mark.parametrize("payload", ["not json", "[]"])
def test_invalid_json(payload: str) -> None:
    with pytest.raises(ResponseValidationError):
        parse_llm_json(payload)

def test_truncated_markdown_fence_is_validation_error() -> None:
    with pytest.raises(ResponseValidationError):
        parse_llm_json("```")


@pytest.mark.parametrize("field,value", [("flags", ["unknown"]), ("used_kb_ids", ["kb_unknown"]), ("client_reply", "")])
def test_invalid_response_values(field: str, value: object) -> None:
    payload = valid_payload()
    payload[field] = value
    with pytest.raises(ResponseValidationError):
        validate_assistant_response(payload, {"kb_005"})


def test_missing_field() -> None:
    payload = valid_payload()
    del payload["flags"]
    with pytest.raises(ResponseValidationError):
        validate_assistant_response(payload, {"kb_005"})
