"""
Comprehensive end-to-end validation for all databases and features.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core import config, missing_tracker, router
from core.missing_tracker import MissingItem
from core.project_manager import Project, ProjectManager
from builders import approval_doc_builder, action_plan_builder, press_release_builder


def test_full_pipeline():
    print("[1/5] Testing ProjectManager & Index persistence (projects.json)...")
    proj = ProjectManager.create_project(
        name="Validation Initiative 2026",
        description="End-to-end verification of all databases and features"
    )
    assert proj.root_dir.is_dir()
    assert proj.input_dir.is_dir()
    assert proj.output_dir.is_dir()
    assert proj.history_dir.is_dir()
    print("  -> Project folder structure created successfully.")

    # Verify index loading
    all_projects = ProjectManager.list_projects()
    found = next((p for p in all_projects if p.id == proj.id), None)
    assert found is not None, "Project not found in index"
    assert found.name == "Validation Initiative 2026"
    print("  -> projects.json index persistence validated.")

    print("\n[2/5] Testing Planning Document ingestion...")
    # Create a dummy PPTX input file
    dummy_input = proj.input_dir / "sample_campaign.pptx"
    dummy_input.write_text("Dummy content for simulation", encoding="utf-8")
    ProjectManager.save_input_document(proj, dummy_input)
    assert proj.get_input_file_path() is not None
    assert proj.get_input_file_path().name == "sample_campaign.pptx"
    print("  -> Planning document saved and scoped to project input/ successfully.")

    print("\n[3/5] Testing Document Builders & Missing Item Detection...")
    approval_template = config.load_json_template(config.TEMPLATE_APPROVAL)
    action_plan_template = config.load_json_template(config.TEMPLATE_ACTION_PLAN)
    
    # Mock data with some missing fields
    approval_mock_data = {
        "application_date": "2026-08-14",
        "department": "販売促進部",
        "applicant": "[MISSING: 申請者]",
        "subject": "新製品プロモーション",
        "purpose": "新製品の認知拡大および販売促進",
        "budget": "[MISSING: 予算]",
    }
    
    appr_path = proj.output_dir / "approval_document_test.docx"
    written_appr, missing_appr = approval_doc_builder.build(
        approval_mock_data, approval_template, appr_path
    )
    assert written_appr.is_file(), "Approval docx not created"
    assert len(missing_appr) > 0, "Missing items not detected"
    print(f"  -> Approval Document built: {written_appr.name} with {len(missing_appr)} missing items detected.")

    # Action plan builder
    action_mock_data = {
        "rows": [
            {"task": "企画確定", "owner": "山田", "due": "8月末", "status": "進行中"},
        ]
    }
    action_path = proj.output_dir / "action_plan_test.xlsx"
    written_act, missing_act = action_plan_builder.build(action_mock_data, action_plan_template, action_path)
    assert written_act.is_file(), "Action plan xlsx not created"
    print(f"  -> Action Plan built: {written_act.name} with {len(missing_act)} missing items detected.")

    # Press release builder
    pr_path = proj.output_dir / "press_release_test.docx"
    pr_text = "報道関係者各位\n\n新サービス発表のお知らせ\n\n■ 商品概要\n革新的なAI文書生成ツール。"
    written_pr, missing_pr = press_release_builder.build(pr_text, pr_path)
    assert written_pr.is_file(), "Press release docx not created"
    print(f"  -> Press Release built: {written_pr.name} with {len(missing_pr)} missing items detected.")

    print("\n[4/5] Testing Per-Project SQLite Database (missing_items.db)...")
    db_path = proj.db_path
    run_id = missing_tracker.create_run(source_filename="sample_campaign.pptx", db_path=db_path)
    assert run_id > 0, "Run ID not created"
    
    all_missing = list(missing_appr)
    for item in all_missing:
        item.output = "稟議書 (Approval Document)"
    for item in missing_act:
        item.output = "実施計画書 (Action Plan)"
        all_missing.append(item)
    for item in missing_pr:
        item.output = "プレスリリース (Press Release)"
        all_missing.append(item)
        
    missing_tracker.add_missing_items(run_id, all_missing, db_path=db_path)
    
    db_items = missing_tracker.get_missing_items(run_id, db_path=db_path)
    assert len(db_items) == len(all_missing), "Items in DB do not match detected items"
    
    initial_pending = missing_tracker.pending_count(run_id, db_path=db_path)
    assert initial_pending == len(all_missing)
    print(f"  -> SQLite DB created at {db_path.name} with {initial_pending} pending missing items.")

    # Toggle resolution in DB
    first_item = db_items[0]
    missing_tracker.mark_resolved(first_item.id, resolved=True, db_path=db_path)
    updated_pending = missing_tracker.pending_count(run_id, db_path=db_path)
    assert updated_pending == initial_pending - 1
    print(f"  -> Resolution toggle verified: pending count decreased from {initial_pending} to {updated_pending}.")

    print("\n[5/5] Testing Status Summaries & Project Cleanup...")
    status = proj.get_status_summary()
    assert status["has_input"] is True
    assert status["generated_count"] == 3
    assert status["has_approval"] is True
    assert status["has_action_plan"] is True
    assert status["has_press_release"] is True
    assert status["pending_missing"] == updated_pending
    print("  -> Summary verified:", status)

    # Clean up project
    ProjectManager.delete_project(proj.id)
    assert not proj.root_dir.exists()
    print("  -> Project deletion and disk cleanup verified.")

    print("\n" + "=" * 55)
    print("ALL DATABASES AND FEATURES ARE VERIFIED AND WORKING 100% PROPERLY!")
    print("=" * 55)


if __name__ == "__main__":
    test_full_pipeline()
