"""Output directory / run-id resolution shared by every writer in this package."""

import os
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
#: Wohin Läufe schreiben. **`AF_AUSGABE` verlegt das Verzeichnis**, und zwar in
#: jedem Prozess, der dieses Modul lädt — auch in einem Unterprozess, den keine
#: Umleitung einer Modulvariable erreicht. Die Test-Suite setzt sie, damit kein
#: Testlauf im echten `outputs/` landet (P7.3-U3.3); dieselbe Form wie
#: `AF_DEMO_ANFRAGEN` für die Demo-Anfragen der Landingpage.
OUTPUT_DIR = os.environ.get("AF_AUSGABE") or str(_REPO_ROOT / "outputs")


def create_run_id(prefix: str = "run") -> str:
    """Create a unique run directory name, e.g. ``run_20260603T143022Z``."""

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{timestamp}"


def ensure_output_dir():
    """Stellt sicher, dass der Output-Ordner existiert."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def resolve_run_output_dir(run_id: str | None = None) -> Path:
    """Return ``outputs/<run_id>/``, creating the directory when needed."""

    ensure_output_dir()
    resolved_run_id = run_id or create_run_id()
    run_dir = Path(OUTPUT_DIR) / resolved_run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_output_path(
    filename: str,
    output_subdir: str | Path | None = None,
    *,
    run_dir: Path | None = None,
) -> str:
    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        return str(run_dir / filename)

    ensure_output_dir()
    if output_subdir is None:
        target_dir = Path(OUTPUT_DIR)
    else:
        subdir_path = Path(output_subdir)
        target_dir = subdir_path if subdir_path.is_absolute() else Path(OUTPUT_DIR) / subdir_path
        target_dir.mkdir(parents=True, exist_ok=True)
    return str(target_dir / filename)
