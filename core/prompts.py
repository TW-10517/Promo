"""
Prompt construction for the three document types.

Every prompt is assembled from four parts, in this order:

    1. Purpose        -- what document is being produced.
    2. Rules          -- the non-negotiable content rules (never invent facts,
                         mark missing information, keep the template structure).
    3. Source content -- the extracted Planning Document text (plus the
                         generated Approval Document for the Action Plan).
    4. Template       -- the predefined structure the output must follow.

The functions also build the JSON Schemas used for structured output, so the
Approval Document and Action Plan responses are guaranteed to be valid JSON
that maps 1:1 onto the template fields.
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# Shared rule blocks
# ---------------------------------------------------------------------------

_COMMON_RULES = """\
【厳守事項】
1. 出典のない事実・数値・日付・人名・企業名を絶対に創作しないこと。
   与えられた資料に書かれていない情報は、推測・補完・一般常識での穴埋めを一切行わない。
2. 資料から読み取れる内容のみを使用し、表現を整えることは可としても、内容を追加しない。
3. 出力は必ず指定されたテンプレート構造に従うこと。
   項目やセクションの追加・削除・名称変更は禁止。
4. 日本語のビジネス文書として自然な、簡潔で事実に即した文体で記述すること。
"""

_MISSING_RULE_TEXT = """\
5. テンプレート上必須だが資料から確定できない項目は、推測せず
   "[MISSING: 項目名]" とだけ記載すること。
   例: 価格が資料にない場合 -> "[MISSING: 価格]"
"""

_MISSING_RULE_BLANK = """\
5. 資料から確定できない項目は、推測せず空文字列 "" にすること。
   この帳票は多くの欄が後日の協議後に手入力で埋められる前提であり、
   空欄であることが正しい状態である。憶測で埋めてはならない。
"""


# ---------------------------------------------------------------------------
# 1. Press Release  (plain text in, plain text out)
# ---------------------------------------------------------------------------

PRESS_RELEASE_SCHEMA = {
    "type": "object",
    "properties": {
        "release_date": {"type": "string", "description": "YYYY.M.D（曜日）形式の配信日"},
        "brand": {"type": "string", "description": "ドスパラ / GALLERIA / THIRDWAVE / raytrek のいずれか"},
        "headline": {"type": "string", "description": "メイン見出し・キャッチコピー"},
        "subtitle": {"type": "string", "description": "サブタイトル・施策要約"},
        "lead_paragraph": {"type": "string", "description": "パソコン専門店ドスパラ（株式会社サードウェーブ...）から始まるリード文"},
        "section_title": {"type": "string", "description": "セクション見出し（企画名・製品名など）"},
        "section_body": {"type": "string", "description": "企画の背景・概要説明（2〜3文）"},
        "period": {"type": "string", "description": "実施期間・発売時期"},
        "product_name": {"type": "string", "description": "代表モデル名および主要スペック"},
        "price_support": {"type": "string", "description": "販売価格または購入サポートクーポン額"},
        "points": {"type": "string", "description": "おすすめポイント（箇条書き3点程度）"},
        "product_url": {"type": "string", "description": "販売ページURL"},
        "special_page_url": {"type": "string", "description": "特設ページURL"},
    },
    "required": ["release_date", "brand", "headline", "subtitle", "lead_paragraph", "section_title", "section_body", "period", "product_name"],
    "additionalProperties": False,
}


def press_release_json_prompt(source_text: str) -> tuple[str, str, dict]:
    """Build structured prompt and schema for Press Release extraction."""
    system = (
        "あなたは株式会社サードウェーブ（ドスパラ）の販売促進部・広報担当者です。"
        "提供された企画書の内容だけを根拠に、公式プレスリリースの各項目を抽出します。"
    )
    user = f"""\
【目的】
企画書（Planning Document）の内容をもとに、ドスパラ公式プレスリリースの構成項目をJSON形式で抽出してください。

{_COMMON_RULES}{_MISSING_RULE_TEXT}

【企画書の内容】
<planning_document>
{source_text}
</planning_document>

指定されたJSONスキーマに従って出力してください。企画書に記載のない項目は "[MISSING: 項目名]" としてください。
"""
    return system, user, PRESS_RELEASE_SCHEMA


def render_dospara_press_release(data: dict) -> str:
    """Render extracted fields into the official Dospara press release text."""
    date = data.get("release_date", "2026.8.14（金）")
    brand = data.get("brand", "ドスパラ")
    headline = data.get("headline", "")
    subtitle = data.get("subtitle", "")
    lead = data.get("lead_paragraph", "")
    sec_title = data.get("section_title", "企画概要")
    sec_body = data.get("section_body", "")
    period = data.get("period", "[MISSING: 実施期間]")
    prod_name = data.get("product_name", "[MISSING: 商品名]")
    price = data.get("price_support", "[MISSING: 価格]")
    points = data.get("points", "")
    prod_url = data.get("product_url", "[MISSING: 販売ページ]")
    special_url = data.get("special_page_url", "[MISSING: 特設ページ]")

    points_block = ""
    if points and points != "[MISSING: おすすめポイント]":
        p_lines = [l.strip() if l.strip().startswith("・") else f"・{l.strip()}" for l in points.split("\n") if l.strip()]
        points_block = "<おすすめポイント>\n" + "\n".join(p_lines) + "\n"

    return f"""{date}

【{brand}】{headline}
{subtitle}

{lead}

◆ {sec_title}
{sec_body}

●期　　間：{period}
※店舗は閉店まで。

【詳細・製品情報】
●{prod_name}
価格：{price}
{points_block}販売ページ　{prod_url}

【{sec_title} 特設ページ】
{special_url}

■株式会社サードウェーブについて
個人のお客様からプロユース、法人のお客様の課題解決のためのソリューションビジネスを行うIT企業です。PCショップ『ドスパラ』や、パソコン・スマホの修理とサポートの専門店『デジタルドック』の運営をはじめ、PCブランド『GALLERIA』、『THIRDWAVE』などの企画・製造、及び当社だけのアフターフォローやサポートサービスを展開。さらに、高校生のためのeスポーツ大会『NASEF JAPAN 全日本高校eスポーツ選手権』に特別協賛しています。また、各地方自治体に対し、eスポーツのための支援を行っています。サードウェーブは最先端の技術を安心と共にお届けすることで、より良い情報化社会の実現に貢献し、100年先も世の中に求められる企業であることを目指します。

サードウェーブ　https://info.twave.co.jp/
ドスパラ　　　　https://www.dospara.co.jp/

※ 本リリースに記載の内容は予告なく変更となる場合があります。予めご了承ください。

このリリースに関するお問い合わせは、下記までお願いいたします。
【購入前のご相談・お問い合わせ先】購入前相談窓口
TEL：03-4332-9656
電話受付　10:00から19:00

【パソコンのサポートに関するお問い合わせ先】サードウェーブサポートセンター
TEL：03-4332-9193　（ナビダイヤル：0570-028-119）
電話受付　24時間　365日対応

【報道関係者様お問い合わせ先】広報室
TEL：03-5294-2043
Mail：dospara-koho@twave.co.jp

■本リリース内の画像・テキストの引用・掲載について
報道・ニュース配信の目的でのみご利用いただけます。
ご利用の際は、出典元として以下のリンクの掲載をお願いいたします。
リ ン ク 先：https://www.dospara.co.jp/
出典表記例：{brand}（株式会社サードウェーブ）"""


def press_release_prompt(source_text: str, template: str) -> tuple[str, str]:
    """Build (system, user) prompts for the Press Release."""
    system = (
        "あなたは株式会社サードウェーブ（ドスパラ）の販売促進部・広報担当者です。"
        "提供された企画書の内容だけを根拠に、公式プレスリリースの定型フォーマットに沿って正確・魅力的なプレスリリースを作成します。"
    )

    user = f"""\
【目的】
企画書（Planning Document）の内容をもとに、ドスパラ公式フォーマットのプレスリリースを作成してください。

{_COMMON_RULES}{_MISSING_RULE_TEXT}
6. 出力はプレーンテキストのみ。JSON、Markdown記法（**、#、```など）、前置き・後書き・説明文は一切含めないこと。
   1行目の日付からプレスリリース本文を開始し、本文以外を出力しない。
7. テンプレートの角括弧 [ ] は差し込み位置を示すプレースホルダである。
   出力では角括弧を残さず、企画書の内容に応じた適切な文言に置き換えること。
   ただし企画書から確定できない項目は "[MISSING: 項目名]" とする。
8. ブランド名（【ドスパラ】、【GALLERIA】、【THIRDWAVE】、【raytrek】等）やセクション記号（◆、●、・、■）の並び順はテンプレート通りに保つこと。
9. 会社概要、免責事項、問い合わせ先、引用表記などの定型フッター部分はテンプレートの文面をそのまま正確に維持すること。

【企画書の内容】
<planning_document>
{source_text}
</planning_document>

【プレスリリース テンプレート】
<template>
{template}
</template>

上記テンプレートの構造に従い、プレスリリース本文のみを出力してください。
"""
    return system, user


# ---------------------------------------------------------------------------
# 2. Approval Document  (JSON out, one key per template field)
# ---------------------------------------------------------------------------

def approval_document_schema(template: dict) -> dict:
    """
    Build a JSON Schema whose properties are exactly the template's field keys.

    Using structured output means the response can be mapped field-by-field
    onto the .docx without any fragile text parsing.
    """
    keys = [f["key"] for f in template.get("header_fields", [])]
    keys += [s["key"] for s in template.get("sections", [])]

    properties = {key: {"type": "string"} for key in keys}
    return {
        "type": "object",
        "properties": properties,
        "required": keys,
        "additionalProperties": False,
    }


def _describe_fields(fields: list[dict]) -> str:
    """Render template fields as a readable key/label/hint list for the prompt."""
    lines = []
    for field in fields:
        hint = field.get("hint", "")
        lines.append(f'  - "{field["key"]}" ({field["label"]}): {hint}')
    return "\n".join(lines)


def approval_document_prompt(source_text: str, template: dict) -> tuple[str, str]:
    """Build (system, user) prompts for the Approval Document."""
    system = (
        "あなたは日本企業の販売促進部に所属する、社内稟議書作成の専門家です。"
        "提供された企画書の内容だけを根拠に、定型フォーマットの稟議書を作成します。"
    )

    user = f"""\
【目的】
企画書（Planning Document）の内容をもとに、稟議書「{template.get('document_title', '稟議書')}」を作成してください。

{_COMMON_RULES}{_MISSING_RULE_TEXT}
6. 出力は指定されたキーを持つJSONオブジェクトのみ。
   すべての値は文字列とする。キーの追加・削除・変更は禁止。
7. 各項目は簡潔にまとめること。本文セクションは1〜5文程度を目安とする。
   改行が必要な場合は "\\n" を使用してよい。

【稟議書テンプレートの項目】
▼ ヘッダー項目（表形式で出力される短い項目）
{_describe_fields(template.get("header_fields", []))}

▼ 本文セクション
{_describe_fields(template.get("sections", []))}

【企画書の内容】
<planning_document>
{source_text}
</planning_document>

上記の各キーに対応する値を持つJSONオブジェクトを出力してください。
"""
    return system, user


# ---------------------------------------------------------------------------
# 3. Action Plan  (JSON out, fixed row/column grid, blanks are expected)
# ---------------------------------------------------------------------------

def action_plan_schema(template: dict) -> dict:
    """
    Build a JSON Schema for the Action Plan grid.

    The response is ``{"rows": [ {<editable column key>: string, ...}, ... ]}``
    with exactly one entry per template row, in template order. The first
    column (the fixed row label) comes from the template, not from the model.
    """
    editable = [c["key"] for c in template.get("columns", []) if not c.get("fixed")]
    row_schema = {
        "type": "object",
        "properties": {key: {"type": "string"} for key in editable},
        "required": editable,
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"rows": {"type": "array", "items": row_schema}},
        "required": ["rows"],
        "additionalProperties": False,
    }


def action_plan_prompt(
    source_text: str,
    approval_text: str,
    template: dict,
) -> tuple[str, str]:
    """
    Build (system, user) prompts for the Action Plan.

    ``approval_text`` is a flattened rendering of the freshly generated
    Approval Document — the Action Plan is derived from both sources.
    """
    columns = template.get("columns", [])
    rows = template.get("rows", [])
    editable = [c for c in columns if not c.get("fixed")]

    column_desc = "\n".join(
        f'  - "{c["key"]}" ({c["header"]}): '
        + (
            "資料から確定できる場合のみ記入。"
            if c.get("fill")
            else "原則として空文字列 \"\"（協議後に手入力される欄）。"
        )
        for c in editable
    )

    row_desc = "\n".join(
        f'  {i + 1}. {r["item"]} — {r.get("hint", "")}' for i, r in enumerate(rows)
    )

    system = (
        "あなたは日本企業の販売促進部に所属する、実施計画書作成の担当者です。"
        "資料に明記された事実のみを転記し、未確定の欄は空欄のまま残します。"
    )

    user = f"""\
【目的】
企画書と、そこから作成された稟議書の内容をもとに、
「{template.get('document_title', '実施計画書')}」の各行を作成してください。

{_COMMON_RULES}{_MISSING_RULE_BLANK}
6. 出力は {{"rows": [...]}} の形式のJSONオブジェクトのみ。
   rows の要素数はちょうど {len(rows)} 件とし、下記の行の順序と完全に一致させること。
   行の追加・削除・並べ替えは禁止。
7. この帳票は「価格」など多くの項目を、販売促進部と企画部の協議後に
   手入力で確定させる前提である。未確定の欄を埋めようとしないこと。
   迷った場合は空文字列 "" を選ぶこと。
8. "[MISSING: ...]" は使用しない。この帳票では空文字列 "" を用いる。

【列（各行のオブジェクトのキー）】
{column_desc}

【行（この順序・この件数で出力すること）】
{row_desc}

【企画書の内容】
<planning_document>
{source_text}
</planning_document>

【稟議書の内容】
<approval_document>
{approval_text}
</approval_document>

上記の {len(rows)} 行に対応する rows 配列を持つJSONオブジェクトを出力してください。
"""
    return system, user


def flatten_approval(data: dict, template: dict) -> str:
    """
    Render the generated Approval Document as readable text.

    Used as the second source input when generating the Action Plan.
    """
    lines: list[str] = []
    for field in template.get("header_fields", []) + template.get("sections", []):
        value = str(data.get(field["key"], "")).strip()
        lines.append(f'{field["label"]}: {value}')
    return "\n".join(lines) if lines else json.dumps(data, ensure_ascii=False, indent=2)
