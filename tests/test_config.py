from __future__ import annotations

import os

from app import config


def test_model_stage_overrides(monkeypatch):
    monkeypatch.setenv("MODEL_EXTRACT", "test/extract-model")
    assert config.model_for_stage("extract") == "test/extract-model"


def test_available_models_excludes_fallback(monkeypatch):
    monkeypatch.setenv("MODEL_MATCH", "test/match-model")
    models = config.available_models()
    assert "fallback" not in models
    assert models["match"] == "test/match-model"


def test_apply_to_all_parsing(monkeypatch):
    monkeypatch.setenv("APPLY_TO_ALL_ELIGIBLE", "TRUE")
    assert config._env_bool("APPLY_TO_ALL_ELIGIBLE", False) is True
    monkeypatch.setenv("APPLY_TO_ALL_ELIGIBLE", "0")
    assert config._env_bool("APPLY_TO_ALL_ELIGIBLE", True) is False
