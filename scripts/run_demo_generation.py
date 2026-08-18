"""
Runs an automated end-to-end demo generation using the local model/pipeline.
Creates a project, loads the demo PPTX, generates all 3 business documents,
and prints the results.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.project_manager import ProjectManager
from core.router import Router, APPROVAL, ACTION_PLAN, PRESS_RELEASE
from core.ai_client import AIClient
from core.ppt_reader import extract_text, summarize


def main():
    print("==================================================================")
    print("[START] Running Automated Demo Generation (Local Model / Dospara Template)")
    print("==================================================================\n")

    pm = ProjectManager()

    # 1. Create or retrieve demo project
    project_name = "GALLERIA_Autumn_2026_Promotion"
    desc = "2026年秋 最新AIゲーミングPC（GALLERIA XDR7A-R58-WL等）発売記念プロモーション"
    
    # Check if project already exists
    projects = pm.list_projects()
    demo_proj = next((p for p in projects if p.name == project_name), None)
    if not demo_proj:
        demo_proj = pm.create_project(project_name, desc)
        print(f"[1/4] Created Project: {demo_proj.name} (ID: {demo_proj.id})")
    else:
        print(f"[1/4] Found Existing Project: {demo_proj.name} (ID: {demo_proj.id})")

    # 2. Ingest Planning Document
    pptx_path = root_dir / "data" / "demo_planning_document.pptx"
    if not pptx_path.is_file():
        print(f"Error: {pptx_path} not found. Run scripts/create_demo_pptx.py first.")
        return

    saved_input = pm.save_input_document(demo_proj, pptx_path)
    print(f"[2/4] Saved Planning Document to: {saved_input}")

    # Extract text
    source_text = extract_text(saved_input)
    print(f"      -> Extracted Text Summary: {summarize(source_text)}")

    # 3. Run Document Generation
    print("\n[3/4] Generating Documents with Router & Local AI Model...")
    client = AIClient()
    router = Router(client)

    selections = [APPROVAL, ACTION_PLAN, PRESS_RELEASE]
    result = router.run(
        source_text=source_text,
        source_path=saved_input,
        output_dir=demo_proj.output_dir,
        selections=selections,
        db_path=demo_proj.db_path,
    )

    print("\n[4/4] [SUCCESS] Generation Complete! Output Documents Created:")
    for doc_type, file_path in result.files.items():
        print(f"  [OK] {doc_type:15}: {file_path}")

    print(f"\n[INFO] Missing Items Detected: {len(result.missing_items)} items recorded to SQLite database:")
    for item in result.missing_items[:5]:
        print(f"   - {item.field} (Context: {item.context})")
    if len(result.missing_items) > 5:
        print(f"   ... and {len(result.missing_items) - 5} more items.")

    print("\n==================================================================")
    print(f"Project Folder: {demo_proj.folder_path}")
    print("==================================================================")


if __name__ == "__main__":
    main()
