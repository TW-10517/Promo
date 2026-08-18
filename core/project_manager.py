"""
Project management and storage organization.

Each project represents a distinct business initiative / product promotion and
owns its own folder containing:
    projects/<project_folder>/
        input/     -> Original/loaded Planning Document (.pptx)
        output/    -> Generated Approval Document, Action Plan, Press Release
        history/   -> Missing items database (missing_items.db) and run logs

Project metadata is tracked in `projects.json` for fast listing on the home screen.
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from core import config


def _sanitize_folder_name(name: str) -> str:
    """Turn a project name into a safe filesystem folder name."""
    sanitized = name.strip()
    for bad in '<>:"/\\|?*':
        sanitized = sanitized.replace(bad, "_")
    sanitized = re.sub(r"\s+", "_", sanitized)
    return sanitized[:64] or "project"


@dataclass
class Project:
    """Represents a single project / initiative."""

    id: str
    name: str
    folder_name: str
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    input_filename: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- Directory helpers -------------------------------------------------

    @property
    def root_dir(self) -> Path:
        return ProjectManager.projects_root() / self.folder_name

    @property
    def folder_path(self) -> Path:
        """Alias for ``root_dir`` -- some UI code refers to it by this name."""
        return self.root_dir

    @property
    def input_dir(self) -> Path:
        return self.root_dir / "input"

    @property
    def output_dir(self) -> Path:
        return self.root_dir / "output"

    @property
    def history_dir(self) -> Path:
        return self.root_dir / "history"

    @property
    def db_path(self) -> Path:
        return self.history_dir / "missing_items.db"

    @property
    def state_path(self) -> Path:
        """
        Internal generation state: the raw text/data from the most recent
        generation run, saved automatically so reopening this project can
        show the output again. This is NOT a real .docx/.xlsx file -- it
        lives in ``output/`` alongside any files the user explicitly
        exported, but as JSON, so it's never mistaken for one (see
        ``get_generated_files``, which only looks for real document
        extensions).
        """
        return self.output_dir / "_generation_state.json"

    def ensure_directories(self) -> None:
        """Ensure all project subdirectories exist on disk."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    # --- Files helpers ----------------------------------------------------

    def get_input_file_path(self) -> Path | None:
        """Return the path to the currently registered or newest PPTX in input/."""
        if self.input_filename:
            candidate = self.input_dir / self.input_filename
            if candidate.is_file():
                return candidate

        # Fallback: scan input_dir for any .pptx
        if self.input_dir.is_dir():
            pptx_files = sorted(
                self.input_dir.glob("*.pptx"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if pptx_files:
                return pptx_files[0]
        return None

    def get_generated_files(self) -> list[Path]:
        """Return all generated files in the output directory sorted newest first."""
        if not self.output_dir.is_dir():
            return []
        files = [
            p for p in self.output_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".docx", ".xlsx", ".pdf", ".txt"}
        ]
        return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    def get_status_summary(self) -> dict[str, Any]:
        """
        Compute quick summary information for dashboard display.
        Returns:
            {
                "has_input": bool,
                "input_name": str,
                "generated_count": int,
                "has_approval": bool,
                "has_action_plan": bool,
                "has_press_release": bool,
                "output_summary": str,
                "pending_missing": int,
            }
        """
        input_path = self.get_input_file_path()
        generated = self.get_generated_files()

        # "Generated" means the AI has produced this document, whether or
        # not the user has exported a real file yet -- the internal JSON
        # state (saved automatically every run) is the primary signal, with
        # real exported files as a fallback for older projects that predate
        # internal state tracking.
        state_kinds: set[str] = set()
        if self.state_path.is_file():
            try:
                import json
                payload = json.loads(self.state_path.read_text(encoding="utf-8"))
                state_kinds = set(payload.get("documents", {}).keys())
            except Exception:
                state_kinds = set()

        has_approval = "approval" in state_kinds or any("approval" in f.name.lower() or "稟議" in f.name for f in generated)
        has_action_plan = "action_plan" in state_kinds or any("action_plan" in f.name.lower() or "実施計画" in f.name for f in generated)
        has_press_release = "press_release" in state_kinds or any("press_release" in f.name.lower() or "プレスリリース" in f.name for f in generated)

        kinds_count = sum([has_approval, has_action_plan, has_press_release])
        output_summary = f"{kinds_count}/3 文書生成済" if kinds_count > 0 else "未生成"

        # Check pending missing fields if DB exists
        pending_count = 0
        if self.db_path.is_file():
            try:
                from core import missing_tracker
                runs = missing_tracker.list_runs(db_path=self.db_path, limit=1)
                if runs:
                    pending_count = missing_tracker.pending_count(runs[0].id, db_path=self.db_path)
            except Exception:
                pass

        return {
            "has_input": input_path is not None,
            "input_name": input_path.name if input_path else "",
            "generated_count": kinds_count,
            "has_approval": has_approval,
            "has_action_plan": has_action_plan,
            "has_press_release": has_press_release,
            "output_summary": output_summary,
            "pending_missing": pending_count,
        }


class ProjectManager:
    """Manages project folders and the `projects.json` metadata index."""

    @staticmethod
    def projects_root() -> Path:
        """Root directory containing all project folders."""
        root = config.app_dir() / "projects"
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def index_path() -> Path:
        """Path to projects.json index."""
        return config.app_dir() / "projects.json"

    @classmethod
    def load_index(cls) -> list[dict[str, Any]]:
        """Load raw project records from projects.json."""
        index_file = cls.index_path()
        if not index_file.is_file():
            return []
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    @classmethod
    def save_index(cls, records: list[dict[str, Any]]) -> None:
        """Save project records to projects.json."""
        index_file = cls.index_path()
        index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    @classmethod
    def list_projects(cls) -> list[Project]:
        """List all projects, ordered by updated_at DESC."""
        raw_list = cls.load_index()
        projects = []
        for raw in raw_list:
            try:
                proj = Project(
                    id=raw["id"],
                    name=raw["name"],
                    folder_name=raw["folder_name"],
                    description=raw.get("description", ""),
                    created_at=raw.get("created_at", ""),
                    updated_at=raw.get("updated_at", ""),
                    input_filename=raw.get("input_filename"),
                    metadata=raw.get("metadata", {}),
                )
                projects.append(proj)
            except Exception:
                continue

        # Sort by updated_at DESC (fallback to created_at)
        projects.sort(
            key=lambda p: p.updated_at or p.created_at or "",
            reverse=True,
        )
        return projects

    @classmethod
    def get_project(cls, project_id: str) -> Project | None:
        """Get a project by its ID."""
        for proj in cls.list_projects():
            if proj.id == project_id:
                return proj
        return None

    @classmethod
    def get_project_status_summary(cls, project_or_id: str | Project) -> dict[str, Any]:
        """Get status summary for a project by Project instance or ID."""
        proj = cls.get_project(project_or_id) if isinstance(project_or_id, str) else project_or_id
        if not proj:
            return {
                "has_input": False,
                "input_name": "",
                "generated_count": 0,
                "has_approval": False,
                "has_action_plan": False,
                "has_press_release": False,
                "output_summary": "0/3",
                "pending_missing": 0,
            }
        return proj.get_status_summary()

    get_status_summary = get_project_status_summary

    @classmethod
    def create_project(cls, name: str, description: str = "") -> Project:
        """
        Create a new project folder and register it in the index.
        """
        name = name.strip()
        if not name:
            raise ValueError("プロジェクト名を入力してください。")

        now = datetime.now().isoformat(timespec="seconds")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:6]
        folder_base = _sanitize_folder_name(name)
        folder_name = f"{folder_base}_{stamp}_{unique_suffix}"

        project_id = f"proj_{stamp}_{unique_suffix}"

        project = Project(
            id=project_id,
            name=name,
            folder_name=folder_name,
            description=description.strip(),
            created_at=now,
            updated_at=now,
        )

        # Create project folder structure
        project.ensure_directories()

        # Update index
        records = cls.load_index()
        records.insert(0, asdict(project))
        cls.save_index(records)

        return project

    @classmethod
    def update_project(cls, project: Project) -> None:
        """Update existing project record in index."""
        project.updated_at = datetime.now().isoformat(timespec="seconds")
        records = cls.load_index()
        updated = False
        for i, rec in enumerate(records):
            if rec.get("id") == project.id:
                records[i] = asdict(project)
                updated = True
                break
        if not updated:
            records.append(asdict(project))
        cls.save_index(records)

    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        """
        Delete a project folder and its index entry.
        """
        project = cls.get_project(project_id)
        if project and project.root_dir.is_dir():
            try:
                shutil.rmtree(project.root_dir, ignore_errors=True)
            except Exception:
                pass

        records = cls.load_index()
        filtered = [r for r in records if r.get("id") != project_id]
        cls.save_index(filtered)
        return True

    @classmethod
    def save_input_document(cls, project: Project | str, source_path: Path | str) -> Path:
        """
        Copy a selected PPTX file into the project's `input/` folder and update project.
        """
        proj = cls.get_project(project) if isinstance(project, str) else project
        if not proj:
            raise ValueError(f"Project not found: {project}")

        src = Path(source_path)
        proj.ensure_directories()
        dest_path = proj.input_dir / src.name
        
        # If source is already in the project's input_dir, no need to copy over itself
        if src.resolve() != dest_path.resolve():
            shutil.copy2(src, dest_path)

        proj.input_filename = dest_path.name
        cls.update_project(proj)
        return dest_path
