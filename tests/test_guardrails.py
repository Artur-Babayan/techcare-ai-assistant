import pytest

from app.guardrails import validate_supported_numbers
from app.models import AssistantResponse, KnowledgeItem
from app.validators import ResponseValidationError


def test_unsupported_numeric_fact_is_rejected() -> None:
    response = AssistantResponse("Стоимость 9999 ₽.", "", ["kb_005"], ["no_upsell"])
    source = KnowledgeItem("kb_005", "Windows", "Установка стоит 3000 ₽.", [])
    with pytest.raises(ResponseValidationError):
        validate_supported_numbers(response, [source])
