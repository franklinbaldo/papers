import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[1] / "scripts" / "run_model_backed_a_api.py"
_SPEC = importlib.util.spec_from_file_location("run_model_backed_a_api", _SCRIPT)
api_runner = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(api_runner)


def _manifest() -> dict:
    path = Path(__file__).parents[1] / "model_backed_a_v2_api.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _v1_manifest() -> dict:
    path = Path(__file__).parents[1] / "model_backed_a_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_api_manifest_shares_v1_corpus_policy():
    manifest = _manifest()
    v1 = _v1_manifest()
    assert manifest["source_commit"] == v1["source_commit"]
    assert manifest["corpus"] == v1["corpus"]
    assert manifest["trajectory"] == v1["trajectory"]
    assert manifest["atlas"]["center_count"] == v1["atlas"]["center_count"]
    assert manifest["srf_dim"] == v1["srf_dim"]
    assert manifest["generator"]["revision"] == v1["generator"]["revision"]


def test_api_manifest_declares_independent_observers_and_gate():
    manifest = _manifest()
    assert manifest["reference_observer"]["provider"] != manifest["transfer_observer"]["provider"]
    for key in ("reference_observer", "transfer_observer"):
        observer = manifest[key]
        assert observer["provider"] in api_runner._PROVIDERS
        assert observer["credential_env"]
        assert observer["endpoint"].startswith("https://")
    assert manifest["gate"]["require_shuffled_worse_than_paired"] is True
    assert manifest["deviation_notes"]


def test_gemini_encode_batches_and_preserves_order(monkeypatch):
    calls = []
    counter = {"issued": 0}

    def fake_http(url, payload, headers, max_retries):
        calls.append((url, payload))
        # Contract: embeddings come back in request order; ids are global across batches.
        rows = []
        for _ in payload["requests"]:
            counter["issued"] += 1
            rows.append({"values": [float(counter["issued"]), 1.0]})
        return {"embeddings": rows}

    monkeypatch.setattr(api_runner, "_http_json", fake_http)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    spec = {
        "provider": "gemini",
        "model": "gemini-embedding-001",
        "endpoint": "https://example.test/v1beta",
        "credential_env": "GEMINI_API_KEY",
    }
    vectors = api_runner._gemini_encode(
        ["alpha", "beta", "gamma", "delta", "epsilon"], spec, {"gemini_batch_size": 2}, {}
    )

    assert len(calls) == 3
    assert [len(payload["requests"]) for _, payload in calls] == [2, 2, 1]
    assert all(url.endswith(":batchEmbedContents") for url, _ in calls)
    assert vectors.shape == (5, 2)
    assert [row[0] for row in vectors] == [1.0, 2.0, 3.0, 4.0, 5.0]


def test_jina_encode_sorts_rows_by_index_and_sends_frozen_fields(monkeypatch):
    seen_payloads = []
    counter = {"issued": 0}

    def fake_http(url, payload, headers, max_retries):
        seen_payloads.append((url, json.loads(json.dumps(payload))))
        # Contract: data[] may arrive unordered; index carries the row identity.
        count = len(payload["input"])
        first = counter["issued"] + 1
        counter["issued"] += count
        return {
            "data": [
                {"index": position - first, "embedding": [float(position)]}
                for position in reversed(range(first, first + count))
            ]
        }

    monkeypatch.setattr(api_runner, "_http_json", fake_http)
    monkeypatch.setenv("JINA_API_KEY", "test-key")

    spec = {
        "provider": "jina",
        "model": "jina-embeddings-v3",
        "dimensions": 1024,
        "task": "retrieval.passage",
        "endpoint": "https://example.test",
        "credential_env": "JINA_API_KEY",
    }
    vectors = api_runner._jina_encode(["a", "bb", "ccc"], spec, {"jina_batch_size": 2}, {})

    url, payload = seen_payloads[0]
    assert url.endswith("/v1/embeddings")
    assert payload["dimensions"] == 1024
    assert payload["task"] == "retrieval.passage"
    assert payload["model"] == "jina-embeddings-v3"
    assert [len(batch) for _, batch_payload in seen_payloads for batch in [batch_payload["input"]]] == [2, 1]
    # Rows arrived reversed by index; the encoder must restore calibration pairing.
    assert vectors.shape == (3, 1)
    assert [row[0] for row in vectors] == [1.0, 2.0, 3.0]


def test_missing_credential_fails_fast(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    spec = {
        "provider": "gemini",
        "model": "gemini-embedding-001",
        "endpoint": "https://example.test/v1beta",
        "credential_env": "GEMINI_API_KEY",
    }
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        api_runner._gemini_encode(["text"], spec, {}, {})


def test_gemini_rotates_keys_on_429(monkeypatch):
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr(api_runner.time, "sleep", fake_sleep)
    calls = []
    keys_seen = []

    def fake_http(url, payload, headers, max_retries):
        calls.append(1)
        keys_seen.append(headers["x-goog-api-key"])
        if len(calls) == 1:
            raise RuntimeError("HTTP 429 from https://example.test: quota exceeded")
        return {"embeddings": [{"values": [float(len(calls))]} for _ in payload["requests"]]}

    monkeypatch.setattr(api_runner, "_http_json", fake_http)
    monkeypatch.setenv("GEMINI_API_KEY", "key-aaaaaaaaaaaaaaa, key-bbbbbbbbbbbbbbb")

    spec = {
        "provider": "gemini",
        "model": "gemini-embedding-001",
        "endpoint": "https://example.test/v1beta",
        "credential_env": "GEMINI_API_KEY",
    }
    vectors = api_runner._gemini_encode(["x", "y"], spec, {"gemini_batch_size": 2}, {})

    assert vectors.shape == (2, 1)
    assert keys_seen[0] == "key-aaaaaaaaaaaaaaa"
    assert keys_seen[1] == "key-bbbbbbbbbbbbbbb"
    assert slept


def test_unsupported_provider_is_rejected():
    usage: dict = {}
    with pytest.raises(RuntimeError, match="unsupported observer provider"):
        api_runner._encode_with({"provider": "oraculo"}, {}, usage)