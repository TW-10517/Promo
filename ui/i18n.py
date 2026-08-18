"""
Internationalization (i18n) module for Japanese / English UI strings.
Default is Japanese.
"""

from __future__ import annotations

LANG_JA = "ja"
LANG_EN = "en"

CURRENT_LANG = LANG_JA

STRINGS = {
    # ── Header & Window ──
    "app_title": {
        "ja": "ドスパラ 企画・販促文書 自動生成システム",
        "en": "Dospara Promotion Document Generator",
    },
    "app_subtitle": {
        "ja": "企画書 (PowerPoint) から、稟議書・実施計画書・プレスリリースを一括自動生成します",
        "en": "Automatically generate Approval Docs, Action Plans, and Press Releases from PowerPoint",
    },
    "lang_toggle_btn": {
        "ja": "🌐 EN / JP",
        "en": "🌐 EN / JP",
    },
    "theme_to_light": {
        "ja": "☀️ ライトモード",
        "en": "☀️ Light Mode",
    },
    "theme_to_dark": {
        "ja": "🌙 ダークモード",
        "en": "🌙 Dark Mode",
    },

    # ── Document Step 1: Input ──
    "step1_title": {
        "ja": "1. 企画書 PowerPoint (.pptx) の読み込み",
        "en": "1. Ingest Planning Document (.pptx)",
    },
    "select_file_btn": {
        "ja": "ファイルを選択...",
        "en": "Select File...",
    },
    "file_placeholder": {
        "ja": "企画書 (.pptx) を選択してください...",
        "en": "Please select a planning document (.pptx)...",
    },
    "extracting_text": {
        "ja": "企画書のスライドテキストを解析中...",
        "en": "Analyzing slide text from planning document...",
    },
    "extract_success": {
        "ja": "スライド解析完了: {summary}",
        "en": "Analysis complete: {summary}",
    },
    "extract_empty": {
        "ja": "企画書が選択されていません",
        "en": "No planning document selected",
    },
    "preview_placeholder": {
        "ja": "企画書を選択すると、抽出されたスライド内容がここに表示されます...",
        "en": "Extracted slide contents will appear here once selected...",
    },

    # ── Document Step 2: Target Selection ──
    "step2_title": {
        "ja": "2. 生成する文書の選択",
        "en": "2. Select Documents to Generate",
    },
    "doc_approval": {
        "ja": "稟議書",
        "en": "Approval Document",
    },
    "doc_approval_desc": {
        "ja": "社内決裁用の申請文書。目的・背景・予算・スケジュール等を自動整理。",
        "en": "Internal approval document with objectives, background, budget, and schedule.",
    },
    "doc_action_plan": {
        "ja": "実施計画書",
        "en": "Action Plan",
    },
    "doc_action_plan_desc": {
        "ja": "販促部・企画部間の進行管理表。固定フォーマットで自動生成。",
        "en": "Action schedule and progress management table across departments.",
    },
    "doc_press_release": {
        "ja": "プレスリリース",
        "en": "Press Release",
    },
    "doc_press_release_desc": {
        "ja": "ドスパラ公式フォーマット。見出し・リード文・おすすめポイントを抽出。",
        "en": "Official press release format with headlines, lead, and highlight points.",
    },
    "start_generation_btn": {
        "ja": "文書を生成する",
        "en": "Generate Documents",
    },
    "cancel_btn": {
        "ja": "中止",
        "en": "Cancel",
    },

    # ── Document Step 3: Generated Outputs & Previews ──
    "step3_title": {
        "ja": "3. 生成結果の確認・プレビュー",
        "en": "3. Generated Document Previews",
    },
    "click_to_view": {
        "ja": "クリックして詳細をポップアップ表示します",
        "en": "Click to view full preview in popup modal",
    },
    "export_btn": {
        "ja": "ファイルとして保存...",
        "en": "Export to File...",
    },
    "copy_btn": {
        "ja": "テキストをコピー",
        "en": "Copy Text",
    },
    "copied_toast": {
        "ja": "クリップボードにコピーしました！",
        "en": "Copied to clipboard!",
    },
    "close_btn": {
        "ja": "閉じる",
        "en": "Close",
    },

    # ── Missing items / Status ──
    "missing_tab_title": {
        "ja": "要確認項目 (未確定DB)",
        "en": "Pending Items Checklist",
    },
    "missing_desc": {
        "ja": "企画書から抽出できず [MISSING] とマークされた項目です。クリックして解決済みに変更できます。",
        "en": "Items marked as [MISSING]. Click the status cell to toggle resolved.",
    },
    "missing_items_tooltip_title": {
        "ja": "未確定項目",
        "en": "Pending Items",
    },
    "missing_items_tooltip_more": {
        "ja": "ほか {n}件",
        "en": "and {n} more",
    },
    "status_waiting": {
        "ja": "待機中: 企画書を選択して「文書を生成する」をクリックしてください。",
        "en": "Ready: Select a planning document and click 'Generate Documents'.",
    },
    "status_generating": {
        "ja": "AIが文書を生成しています...",
        "en": "AI is generating documents...",
    },
    "status_complete": {
        "ja": "文書生成が完了しました！下のボタンから各文書を確認できます。",
        "en": "Generation complete! Click the document cards below to view previews.",
    },
    "status_error": {
        "ja": "エラーが発生しました",
        "en": "An error occurred",
    },

    # ── Popups / Alerts ──
    "input_required": {
        "ja": "企画書 (.pptx) を選択してください。",
        "en": "Please select a PowerPoint planning document (.pptx).",
    },
    "select_at_least_one": {
        "ja": "生成する文書を少なくとも1つ選択してください。",
        "en": "Please select at least one document to generate.",
    },
    "preview_modal_title": {
        "ja": "【プレビュー】 {title}",
        "en": "[Preview] {title}",
    },

    # ── Home Screen ──
    "home_subtitle": {
        "ja": "企画書（PowerPoint）から、稟議書・実施計画書・プレスリリースを一括自動生成します。",
        "en": "Automatically generate an Approval Document, Action Plan, and Press Release from one PowerPoint.",
    },
    "kpi_projects": {"ja": "プロジェクト", "en": "Projects"},
    "kpi_docs": {"ja": "生成文書", "en": "Generated Docs"},
    "kpi_missing": {"ja": "要確認項目", "en": "Pending Items"},
    "search_placeholder": {
        "ja": "🔍  プロジェクト名または説明で検索...",
        "en": "🔍  Search by project name or description...",
    },
    "create_project_btn": {"ja": "＋  新規プロジェクト作成", "en": "+  New Project"},
    "no_projects_title": {"ja": "プロジェクトがありません", "en": "No projects yet"},
    "no_projects_filtered_title": {
        "ja": "検索条件に一致するプロジェクトがありません",
        "en": "No projects match your search",
    },
    "no_projects_sub": {
        "ja": "「＋ 新規プロジェクト作成」ボタンをクリックして開始してください。",
        "en": "Click \"+ New Project\" to get started.",
    },
    "folder_btn": {"ja": "📁  フォルダ", "en": "📁  Folder"},
    "delete_btn": {"ja": "🗑  削除", "en": "🗑  Delete"},
    "open_project_btn": {"ja": "開く  →", "en": "Open  →"},
    "delete_confirm_title": {"ja": "プロジェクトの削除確認", "en": "Confirm Delete"},
    "delete_confirm_msg": {
        "ja": "プロジェクト「{name}」を削除しますか？\n\n※ プロジェクト内の企画書、生成文書、履歴データがすべて完全に削除されます。",
        "en": "Delete project \"{name}\"?\n\nAll planning documents, generated files, and history data inside this project will be permanently deleted.",
    },
    "docs_generated_badge": {"ja": "{n}/3 文書生成済", "en": "{n}/3 generated"},
    "docs_generating_badge": {"ja": "{n}/3 生成中", "en": "{n}/3 in progress"},
    "not_generated_badge": {"ja": "未生成", "en": "Not generated"},
    "input_pptx_label": {"ja": "📊  企画書", "en": "📊  Planning Doc"},
    "input_pptx_unset": {"ja": "未設定", "en": "Not set"},
    "pending_confirm_badge": {"ja": "⚠  確認待ち: {n}件", "en": "⚠  {n} pending"},
    "no_missing_badge": {"ja": "✓  未確定: なし", "en": "✓  None pending"},
    "missing_dash": {"ja": "未確定項目: —", "en": "Pending items: —"},
    "created_at_label": {"ja": "📅  {date}", "en": "📅  {date}"},
    "no_description": {"ja": "（説明なし）", "en": "(No description)"},

    # ── Create Project Dialog ──
    "create_project_dialog_title": {"ja": "新規プロジェクト作成", "en": "New Project"},
    "create_project_heading": {"ja": "✦  新規プロジェクトを作成", "en": "✦  Create New Project"},
    "create_project_desc": {
        "ja": "プロジェクトごとに企画書（PPTX）、生成文書（Word/Excel）、未確定項目DBが専用フォルダに独立して保存されます。",
        "en": "Each project keeps its planning document (.pptx), exported files, and pending-items history in its own folder.",
    },
    "project_name_label": {"ja": "プロジェクト名", "en": "Project Name"},
    "project_name_placeholder": {
        "ja": "例: GALLERIA秋の最新AI-PCプロモーション",
        "en": "e.g. GALLERIA Autumn AI-PC Promotion",
    },
    "project_desc_label": {"ja": "説明 / メモ (任意)", "en": "Description / Notes (optional)"},
    "project_desc_placeholder": {
        "ja": "プロモーションの概要、ターゲット層、担当者など",
        "en": "Campaign overview, target audience, owner, etc.",
    },
    "cancel_generic_btn": {"ja": "キャンセル", "en": "Cancel"},
    "create_project_submit_btn": {"ja": "✦  プロジェクトを作成", "en": "✦  Create Project"},
    "project_name_required": {
        "ja": "プロジェクト名を入力してください。",
        "en": "Please enter a project name.",
    },
    "project_create_failed": {
        "ja": "プロジェクトの作成に失敗しました:",
        "en": "Failed to create the project:",
    },
    "input_error_title": {"ja": "入力エラー", "en": "Input Error"},
    "error_title": {"ja": "エラー", "en": "Error"},

    # ── Workspace: Project scoping ──
    "back_to_home_btn": {"ja": "←  プロジェクト一覧", "en": "←  Project List"},
    "back_to_home_tooltip": {"ja": "プロジェクト一覧に戻る", "en": "Back to project list"},
    "back_to_output_btn": {"ja": "←  出力ページに戻る", "en": "←  Back to Output"},
    "back_to_output_tooltip": {"ja": "出力ページに戻る", "en": "Return to the output page"},
    "regenerate_tooltip": {"ja": "再生成する", "en": "Regenerate"},
    "goto_generate_btn": {"ja": "🚀  生成画面へ", "en": "🚀  Go to Generate"},
    "goto_generate_tooltip": {"ja": "企画書の変更・再生成を行う", "en": "Change input or regenerate documents"},
    "delete_tooltip": {"ja": "プロジェクトを削除", "en": "Delete project"},

    # ── Document Editor Screen (popup) ──
    "editor_save_tooltip": {"ja": "保存（このアプリ内に保持）", "en": "Save (kept in this app)"},
    "editor_export_tooltip": {"ja": "ファイルとして書き出す", "en": "Export to a file"},
    "editor_copy_tooltip": {"ja": "テキストをコピー", "en": "Copy text"},
    "editor_close_tooltip": {"ja": "閉じる", "en": "Close"},
    "editor_saved_toast": {"ja": "保存しました（このアプリ内のみ / ファイルは作成されません）", "en": "Saved (kept in this app only — no file was created)"},
    "editor_structured_note": {
        "ja": "※ この文書は定型フォーマットで書き出されます。ここでの編集はプレビュー表示とコピーにのみ反映され、エクスポートされるファイルの内容は元のAI生成データに基づきます。",
        "en": "Note: this document is exported in a fixed format. Edits here update the preview and copy text only — the exported file still uses the original generated data.",
    },

    # ── Missing Translation Keys ──
    "extract_error": {"ja": "⚠  テキスト解析エラー", "en": "⚠  Text analysis error"},
    "generation_cancelled": {"ja": "生成を中止しました。", "en": "Generation cancelled."},
    "export_complete": {"ja": "保存完了", "en": "Export Complete"},
    "export_success_msg": {"ja": "ファイルとして保存しました:\n{file}", "en": "Successfully exported to:\n{file}"},
    "export_error": {"ja": "保存エラー", "en": "Export Error"},
    "export_fail_msg": {"ja": "ファイルの保存に失敗しました:\n{exc}", "en": "Failed to save file:\n{exc}"},
    "warning_title": {"ja": "確認", "en": "Warning"},
    "generation_in_progress_exit": {"ja": "文書生成中です。終了しますか？", "en": "Generation in progress. Are you sure you want to exit?"},
    "worker_extract_error": {"ja": "企画書の解析中にエラーが発生しました: {exc}", "en": "Error occurred while parsing planning document: {exc}"},
    "worker_ai_connecting": {"ja": "AIモデル接続確認中...", "en": "Connecting to AI model..."},
    "worker_ai_connecting_log": {"ja": "▶ AIバックエンド接続確認中...", "en": "▶ Checking AI backend connection..."},
    "worker_ai_connected_log": {"ja": "✓ AIバックエンド接続完了", "en": "✓ AI backend connection successful"},
    "worker_generating": {"ja": "企画書から文書を生成中...", "en": "Generating documents from planning document..."},
    "worker_generation_done": {"ja": "文書生成が完了しました！", "en": "Document generation complete!"},
    "worker_doc_done_log": {"ja": "✓ 生成完了: {doc}", "en": "✓ Generated: {doc}"},
    "worker_save_internal_error": {"ja": "※ 内部状態の保存に失敗しました（表示には影響しません）: {exc}", "en": "※ Failed to save internal state (does not affect display): {exc}"},
    "worker_config_error": {"ja": "設定エラー:\n{exc}", "en": "Configuration error:\n{exc}"},
    "worker_ai_error": {"ja": "AI生成エラー:\n{exc}", "en": "AI generation error:\n{exc}"},
    "worker_unexpected_error": {"ja": "予期しないエラーが発生しました:\n{exc_type}: {exc}", "en": "An unexpected error occurred:\n{exc_type}: {exc}"},
}


def set_language(lang: str) -> None:
    global CURRENT_LANG
    if lang in (LANG_JA, LANG_EN):
        CURRENT_LANG = lang


def get_language() -> str:
    return CURRENT_LANG


def t(key: str, **kwargs) -> str:
    """Get translated string for the current language."""
    entry = STRINGS.get(key, {})
    text = entry.get(CURRENT_LANG, entry.get(LANG_JA, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
