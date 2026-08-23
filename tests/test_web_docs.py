"""Das Handbuch muss vollständig bleiben.

Der Sinn dieser Tests ist weniger, Fehler in der Darstellung zu finden, als
Lücken zu verhindern: Eine neue Einstellung, eine neue Systemgröße oder ein
neues Preset ohne Eintrag im Handbuch lässt die Suite fehlschlagen. Das ist
die einzige Sicherung dagegen, dass die Dokumentation still hinter der
Anwendung zurückbleibt.
"""

from __future__ import annotations

import pytest

from dashboard.config_catalog import list_sweep_presets, load_config_file
from dashboard.web.config_editor import glossary
from dashboard.web.pages import docs


def _text(component) -> str:
    return str(component)


# --- Registry --------------------------------------------------------------


def test_every_chapter_has_a_source():
    """Kein Kapitel darf auf eine fehlende Markdown-Datei zeigen."""

    missing = [c.slug for c in docs.CHAPTERS if "Kapitel fehlt" in c.source()]

    assert not missing, f"Ohne Textdatei: {missing}"


def test_chapter_slugs_are_unique():
    slugs = [c.slug for c in docs.CHAPTERS]

    assert len(slugs) == len(set(slugs))


def test_every_chapter_belongs_to_a_known_part():
    unknown = {c.part for c in docs.CHAPTERS} - set(docs.PARTS)

    assert not unknown, f"Unbekannte Teile: {unknown}"


@pytest.mark.parametrize("chapter", docs.CHAPTERS, ids=lambda c: c.slug)
def test_every_chapter_renders(chapter):
    rendered = _text(docs.render(chapter))

    assert chapter.title in rendered
    assert "Traceback" not in rendered


@pytest.mark.parametrize("chapter", docs.CHAPTERS, ids=lambda c: c.slug)
def test_every_chapter_has_substance(chapter):
    """Ein Kapitel, das nur aus der Überschrift besteht, hilft niemandem."""

    assert len(chapter.source()) > 400, f"Zu dünn: {chapter.slug}"


# --- Vollständigkeit -------------------------------------------------------


def test_every_parameter_is_documented():
    """Jede Einstellung des Editors muss im Referenzkapitel auftauchen."""

    reference = docs.BY_SLUG["ref-parameter"].source()
    missing = [path for path, param in glossary.PARAMS.items() if param.label not in reference]

    assert not missing, f"Nicht im Handbuch: {missing}"


def test_every_system_property_is_documented():
    payload = load_config_file("properties.json")
    reference = docs.BY_SLUG["ref-systemgroessen"].source()
    missing = [
        item["id"]
        for item in payload.get("system_properties", [])
        if isinstance(item, dict) and item.get("id") and item["id"] not in reference
    ]

    assert not missing, f"Systemgrößen ohne Eintrag: {missing}"


def test_every_factor_is_documented():
    payload = load_config_file("factors.json")
    reference = docs.BY_SLUG["ref-faktoren"].source()
    missing = [
        key
        for key, factor in payload.items()
        if isinstance(factor, dict) and factor.get("name") and key not in reference
    ]

    assert not missing, f"Faktoren ohne Eintrag: {missing}"


def test_every_preset_is_documented():
    reference = docs.BY_SLUG["ref-presets"].source()
    missing = [sweep.id for sweep in list_sweep_presets() if sweep.id not in reference]

    assert not missing, f"Presets ohne Eintrag: {missing}"


def test_every_agent_is_documented():
    payload = load_config_file("agent_profiles.json")
    reference = docs.BY_SLUG["ref-akteure"].source()
    missing = [key for key in payload if key not in reference.lower()]

    assert not missing, f"Akteure ohne Eintrag: {missing}"


# --- Querverweise ----------------------------------------------------------


def test_internal_links_point_at_existing_chapters():
    """Ein Verweis auf ein Kapitel, das es nicht gibt, ist eine Sackgasse."""

    import re

    broken: list[str] = []
    for chapter in docs.CHAPTERS:
        for slug in re.findall(r"\(/doku/([a-z0-9-]+)\)", chapter.source()):
            if slug not in docs.BY_SLUG:
                broken.append(f"{chapter.slug} -> {slug}")

    assert not broken, f"Tote Verweise: {broken}"


def test_editor_links_point_at_existing_chapters():
    """Auch die Verweise aus dem Config-Editor müssen ankommen."""

    import re
    from pathlib import Path

    editor = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "config_editor"
    broken: list[str] = []
    for path in editor.glob("*.py"):
        for slug in re.findall(r'doc_link\(\s*"([a-z0-9-]+)"', path.read_text(encoding="utf-8")):
            if slug not in docs.BY_SLUG:
                broken.append(f"{path.name} -> {slug}")

    assert not broken, f"Tote Verweise aus dem Editor: {broken}"


# --- Navigation und Suche --------------------------------------------------


def test_navigation_lists_every_chapter():
    rendered = _text(docs.navigation(docs.DEFAULT_SLUG))

    for chapter in docs.CHAPTERS:
        assert chapter.title in rendered, chapter.slug


def test_search_narrows_the_navigation():
    alle = _text(docs.navigation(docs.DEFAULT_SLUG))
    treffer = _text(docs.navigation(docs.DEFAULT_SLUG, "Yield Management"))

    assert len(treffer) < len(alle)
    assert "Wie der Preis entsteht" in treffer


def test_search_without_a_hit_says_so():
    rendered = _text(docs.navigation(docs.DEFAULT_SLUG, "zzz-gibt-es-nicht"))

    assert "Nichts gefunden" in rendered


def test_unknown_path_falls_back_to_the_first_chapter():
    assert docs.slug_from_path("/doku/gibt-es-nicht") == docs.DEFAULT_SLUG
    assert docs.slug_from_path(None) == docs.DEFAULT_SLUG
    assert docs.slug_from_path("/doku/cib") == "cib"
    assert docs.slug_from_path("/doku/cib/") == "cib"


# --- Abschnitte und Anker --------------------------------------------------


def test_sections_are_split_at_headings():
    sections = docs.split_sections("Vorspann\n\n## Erster\n\nText\n\n## Zweiter\n\nMehr")

    assert [title for title, _ in sections] == [None, "Erster", "Zweiter"]


def test_headings_inside_code_blocks_do_not_split():
    markdown = "## Echt\n\n```\n## nur Text\n```\n\nWeiter"

    assert [title for title, _ in docs.split_sections(markdown)] == ["Echt"]


def test_anchor_handles_umlauts_and_punctuation():
    assert docs.anchor("Sättigung & Größe") == "saettigung-groesse"
    assert docs.anchor("Wer fliegt?") == "wer-fliegt"
    assert docs.anchor("!!!") == "abschnitt"
