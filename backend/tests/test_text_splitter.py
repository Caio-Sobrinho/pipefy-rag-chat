import pytest

from app.core.exceptions import AppException
from app.services.text_splitter_service import TextSplitterService


def test_split_text_with_overlap():
    splitter = TextSplitterService()

    text = "um dois tres quatro cinco seis sete oito nove dez"

    chunks = splitter.split_text(
        text=text,
        chunk_size=4,
        chunk_overlap=1,
    )

    assert chunks == [
        "um dois tres quatro",
        "quatro cinco seis sete",
        "sete oito nove dez",
        "dez",
    ]


def test_split_text_rejects_empty_text():
    splitter = TextSplitterService()

    with pytest.raises(AppException):
        splitter.split_text(
            text="",
            chunk_size=500,
            chunk_overlap=50,
        )


def test_split_text_rejects_invalid_overlap():
    splitter = TextSplitterService()

    with pytest.raises(AppException):
        splitter.split_text(
            text="texto válido",
            chunk_size=10,
            chunk_overlap=10,
        )