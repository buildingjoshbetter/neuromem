import pytest

import truememory.ingest.extractor as extractor


@pytest.mark.parametrize(
    ("source_type", "expected_prompt"),
    [
        ("email", extractor.EXTRACTION_PROMPT_EMAIL),
        ("document", extractor.EXTRACTION_PROMPT_DOCUMENT),
        ("slack", extractor.EXTRACTION_PROMPT_CHAT),
        ("discord", extractor.EXTRACTION_PROMPT_CHAT),
        ("teams", extractor.EXTRACTION_PROMPT_CHAT),
        ("conversation", extractor.EXTRACTION_PROMPT),
    ],
)
def test_extract_facts_selects_source_prompt(monkeypatch, source_type, expected_prompt):
    prompts = []
    monkeypatch.setattr(
        extractor,
        "complete",
        lambda config, prompt, system: prompts.append(prompt) or "[]",
    )

    extractor.extract_facts("Durable source content", object(), source_type=source_type)

    assert prompts == [expected_prompt.format(transcript="Durable source content")]


@pytest.mark.parametrize(
    "prompt",
    [
        extractor.EXTRACTION_PROMPT_EMAIL,
        extractor.EXTRACTION_PROMPT_DOCUMENT,
        extractor.EXTRACTION_PROMPT_CHAT,
    ],
)
def test_source_prompts_preserve_untrusted_content_fence(prompt):
    assert "UNTRUSTED" in prompt
    assert extractor._TRANSCRIPT_OPEN in prompt
    assert extractor._TRANSCRIPT_CLOSE in prompt
