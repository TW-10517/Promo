"""
Generates synthetic fine-tuning datasets (train.jsonl, val.jsonl) from official Dospara/Thirdwave
press release patterns and template definitions for local Qwen 2.5 training.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core import config, prompts

# Domain examples inspired directly by real Dospara / Thirdwave press releases
DOSPARA_DOMAINS = [
    {
        "brand": "ドスパラ",
        "product": "夏の大感謝SALE＆キャンペーン",
        "category": "セール・キャンペーン",
        "dept": "販売促進部",
        "applicant": "永井 正樹",
        "date": "2026.8.14（金）",
        "period": "2026年8月14日(金)11:00 から 同28日(金)10:59",
        "purpose": "対象新品PCの購入サポートおよび指定グラフィックボードへの格安アップグレード提供による夏商戦の販売促進。",
        "background": "ゲーミングPCおよびクリエイターPCの需要増加に伴い、最新RTX50シリーズ搭載モデルの普及を加速させる。",
        "overview": "新品パソコンを対象に最大145,000円購入サポート。さらに指定PCのRTX 5060を3,000円でRTX 5060Tiへアップグレード可能。",
        "target": "PCゲーム環境を大幅強化したいゲーマーおよび動画編集クリエイター",
        "details": "GALLERIA XDR7A-R58-WL (Ryzen 7 9800X3D/RTX 5080/64GB/2TB) クーポン利用で145,000円引、THIRDWAVE F-14BR5A (Ryzen 5 7430U/16GB) 1,000円引など。",
        "channel": "全国のドスパラ店舗、および通販サイト",
        "effect": "セール期間中の新品PC販売台数 前年同期比130%達成",
        "budget": "セール販促費・クーポン引当 5,000万円",
        "schedule": "2026年8月14日 11:00開始、8月28日 10:59終了（店舗は27日閉店まで）",
        "risks": "人気構成パーツ（RTX5080等）の在庫枯渇リスク",
        "remarks": "【夏の大感謝SALE 特設ページ】https://www.dospara.co.jp/event/summer-thanksgiving2026.html",
        "url": "https://www.dospara.co.jp/event/summer-thanksgiving2026.html",
    },
    {
        "brand": "GALLERIA",
        "product": "『あおぎり高校』スポンサーシップ契約締結",
        "category": "スポンサーシップ・タイアップ",
        "dept": "ブランドマーケティング室",
        "applicant": "永井 正樹",
        "date": "2026.8.10（月）",
        "period": "2026年8月10日（月）～",
        "purpose": "人気VTuberグループ「あおぎり高校」とのスポンサー契約を通じてGALLERIAブランドの若年層認知拡大を図る。",
        "background": "VTuberによるゲーム配信・3Dライブ活動の活発化に伴い、高負荷配信を支えるゲーミングPCの重要性が向上。",
        "overview": "機材提供による配信・制作環境のサポート、コラボ配信およびコラボモデルPCの企画展開。",
        "target": "VTuberファン層、ゲーム配信視聴者、Z世代ゲーマー",
        "details": "GALLERIAハイエンドゲーミングデスクトップおよび配信周辺機器の提供。あおぎり高校所属13名の活動をバックアップ。",
        "channel": "ドスパラ通販サイト、GALLERIAブランドサイト、公式SNS",
        "effect": "SNS総インプレッション 500万件獲得、若年層新規会員数 15%増",
        "budget": "スポンサー協賛費・機材提供枠 1,200万円",
        "schedule": "2026年8月10日 プレスリリース発表、秋以降 コラボ企画順次実施",
        "risks": "コラボ配信スケジュールの調整遅延",
        "remarks": "あおぎり高校公式サイト: https://www.aogirihighschool.com/",
        "url": "https://galleria.net",
    },
    {
        "brand": "ドスパラ",
        "product": "DCPカレンダー “イヌ” テーマ イラスト・写真作品募集",
        "category": "クリエイター支援・コミュニティ",
        "dept": "クリエイター支援推進部",
        "applicant": "永井 正樹",
        "date": "2026.8.10（月）",
        "period": "2026年8月10日(月) ～ 2026年10月9日(金)",
        "purpose": "クリエイター支援プログラム（DCP）を通じたユーザー創作活動の支援とコミュニティ活性化。",
        "background": "イラスト・写真などクリエイティブ制作を行うドスパラ会員の作品発表機会を創出する。",
        "overview": "「イヌ」をテーマにしたイラスト・写真作品を公募。選出作品は公式HP掲載および秋葉原本店にてポストカード配布、5,000pt進呈。",
        "target": "ドスパラ会員、イラストレーター、フォトグラファー、クリエイター志望者",
        "details": "部門：イラスト部門・フォト部門。応募：SNS/Discordにハッシュタグ #DCPカレンダー2026 で投稿。",
        "channel": "DCP公式サイト、ドスパラ公式SNS、ドスパラ秋葉原本店",
        "effect": "応募総数 500作品以上、DCP新規会員登録 1,000名獲得",
        "budget": "ポイント進呈およびポストカード印刷費 80万円",
        "schedule": "2026年10月9日 締切、10月下旬 選考発表、11月・12月 秋葉原本店で配布",
        "risks": "著作権侵害作品の投稿に対する審査体制の徹底",
        "remarks": "【DCPカレンダー公式サイト】https://www.dospara.co.jp/dcp-seminar-event-list-calendar.html",
        "url": "https://www.dospara.co.jp/dcp-seminar-event-list-calendar.html",
    },
    {
        "brand": "THIRDWAVE",
        "product": "法人向け最新Core Ultra搭載スリムデスクトップ「Slim-AD7」発売",
        "category": "法人向けPC・新製品",
        "dept": "法人営業統括部",
        "applicant": "永井 正樹",
        "date": "2026.8.5（水）",
        "period": "2026年8月5日(水) 発売開始",
        "purpose": "オフィスの省スペース化とAI処理能力向上を両立した法人向けデスクトップPCの市場投入。",
        "background": "企業オフィスでのNPU搭載AI PC需要の高まりと、設置面積を抑えたスリム筐体へのニーズ。",
        "overview": "インテル Core Ultra 7 プロセッサー搭載、幅95mmのスリムタワーPC。最大64GBメモリ、3画面同時出力対応。",
        "target": "一般企業、金融機関、コールセンター、自治体",
        "details": "Core Ultra 7 265 / 16GB DDR5 / 512GB NVMe SSD / Windows 11 Pro。標準価格 149,800円（税込）。",
        "channel": "ドスパラ法人Webサイト、法人営業窓口",
        "effect": "初年度販売目標 8,000台、売上高 12億円",
        "budget": "製品カタログ・法人向けWeb広告費 600万円",
        "schedule": "2026年8月5日 受注開始、翌日出荷対応",
        "risks": "大口導入時のメモリ部材供給リードタイム",
        "remarks": "オンサイト保守3年パックの同時加入キャンペーンを実施。",
        "url": "https://www.dospara.co.jp/biz/",
    },
]

PPT_STYLES = [
    # Style 1: Bullet Outline
    """【企画書：{product}】
■ 概要
・ブランド：{brand}
・企画名：{product}
・起案部門：{dept}（担当：{applicant}）
・起案日：{date}
・展開時期：{period}

■ 企画の背景・目的
・目的：{purpose}
・背景：{background}
・施策概要：{overview}

■ ターゲット・詳細
・対象ターゲット：{target}
・詳細仕様・特典：{details}
・展開チャネル：{channel}

■ 目標・予算・スケジュール
・期待効果：{effect}
・概算予算：{budget}
・実施日程：{schedule}
・想定リスク：{risks}
・特設ページ/備考：{remarks}
""",
    # Style 2: Slide Deck Format
    """SLIDE 1: {brand} {product} 実施計画
{dept} / {applicant} （{date}）

SLIDE 2: 実施背景と狙い
【背景】{background}
【目的】{purpose}

SLIDE 3: 施策概要 & 対象
・ターゲット：{target}
・施策内容：{overview}
・展開チャネル：{channel}
・実施期間：{period}

SLIDE 4: 詳細仕様・おすすめポイント
・内容：{details}
・期待効果：{effect}
・関連URL：{url}

SLIDE 5: 予算・スケジュール
・予算：{budget}
・マイルストーン：{schedule}
・留意事項：{risks}
""",
]


# Category -> body pattern. Verified against live Dospara/GALLERIA releases:
# sale/campaign and corporate product launches carry price/period/おすすめポイント
# (pattern A); sponsorships and creator-recruitment announcements use plain
# narrative ■ sections with no price/period block at all (pattern B).
_PATTERN_A_CATEGORIES = {"セール・キャンペーン", "法人向けPC・新製品"}


def _pattern_a_body(domain: dict, missing_keys: list[str]) -> str:
    period_str = "[MISSING: 実施期間]" if "period" in missing_keys else domain["period"]
    url_str = "[MISSING: 特設ページ]" if "url" in missing_keys else domain["url"]
    details_str = "[MISSING: 商品詳細]" if "details" in missing_keys else domain["details"]

    return f"""◆ {domain['product']} 概要
{domain['background']}

●期　　間：{period_str}
※店舗は閉店まで。

【詳細・製品情報】
●{details_str}
<おすすめポイント>
・{domain['overview']}
・{domain['target']}向けに最適な仕様と購入特典
・全国のドスパラ店舗およびWeb通販にて展開
販売ページ　{url_str}

【{domain['product']} 特設ページ】
{url_str}"""


def _pattern_b_body(domain: dict) -> str:
    # Sponsorships / recruitment announcements: plain narrative sections,
    # no price/period/おすすめポイント block -- matches the real structure
    # (e.g. the GALLERIA x あおぎり高校 sponsorship release).
    return f"""{domain['background']}

{domain['overview']}

■ {domain['target']}について
{domain['purpose']}"""


# Brand -> lead-sentence subject descriptor. Verified against live releases
# for ドスパラ and GALLERIA; THIRDWAVE/raytrek follow the same clause shape
# as the verified two (not independently verified against a live release).
_BRAND_LEAD_SUBJECT = {
    "ドスパラ": "パソコン専門店ドスパラ",
    "GALLERIA": "ハイパフォーマンスと安定性を誇るPC　GALLERIA（ガレリア）",
    "THIRDWAVE": "PCブランド THIRDWAVE",
    "raytrek": "クリエイター向けPCブランド raytrek",
}


def generate_dospara_press_release_text(domain: dict, missing_keys: list[str]) -> str:
    """Generate exact Dospara official press release output."""
    brand = domain["brand"]
    date_str = "[MISSING: 配信日]" if "date" in missing_keys else domain["date"]
    subject = _BRAND_LEAD_SUBJECT.get(brand, f"パソコン専門店ドスパラ「{brand}」")

    lead = (
        f"{subject}（株式会社サードウェーブ 取締役社長 永井正樹：東京都千代田区）は、"
        f"{domain['overview']}を、全国のドスパラ店舗、および通販サイトにて、{date_str}より開始しました。"
    )

    body = (
        _pattern_a_body(domain, missing_keys)
        if domain["category"] in _PATTERN_A_CATEGORIES
        else _pattern_b_body(domain)
    )

    return f"""{date_str}

【{brand}】{domain['product']}
{domain['purpose']}

{lead}

{body}

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


def generate_approval_sample(domain: dict, missing_keys: list[str], style_idx: int) -> dict:
    input_data = dict(domain)
    for k in missing_keys:
        input_data[k] = "（記載なし）"

    ppt_text = PPT_STYLES[style_idx % len(PPT_STYLES)].format(**input_data)
    template = config.load_json_template(config.TEMPLATE_APPROVAL)
    system_prompt, user_prompt = prompts.approval_document_prompt(ppt_text, template)

    target_json = {
        "application_date": f"[MISSING: 申請日]" if "date" in missing_keys else domain["date"],
        "department": f"[MISSING: 申請部署]" if "dept" in missing_keys else domain["dept"],
        "applicant": f"[MISSING: 申請者]" if "applicant" in missing_keys else domain["applicant"],
        "subject": f"【{domain['brand']}】{domain['product']} の件",
        "product_name": domain["product"],
        "target_period": f"[MISSING: 実施時期]" if "period" in missing_keys else domain["period"],
        "purpose": f"[MISSING: 目的]" if "purpose" in missing_keys else domain["purpose"],
        "background": f"[MISSING: 背景]" if "background" in missing_keys else domain["background"],
        "overview": f"[MISSING: 施策概要]" if "overview" in missing_keys else domain["overview"],
        "target_customer": f"[MISSING: 対象顧客]" if "target" in missing_keys else domain["target"],
        "product_details": f"[MISSING: 商品内容]" if "details" in missing_keys else domain["details"],
        "sales_channel": f"[MISSING: 販売チャネル]" if "channel" in missing_keys else domain["channel"],
        "expected_effect": f"[MISSING: 期待効果]" if "effect" in missing_keys else domain["effect"],
        "budget": f"[MISSING: 予算]" if "budget" in missing_keys else domain["budget"],
        "schedule": f"[MISSING: スケジュール]" if "schedule" in missing_keys else domain["schedule"],
        "risks": f"[MISSING: 想定リスク・留意事項]" if "risks" in missing_keys else domain["risks"],
        "remarks": domain["remarks"],
    }

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": json.dumps(target_json, ensure_ascii=False, indent=2)},
        ]
    }


def generate_press_release_sample(domain: dict, missing_keys: list[str], style_idx: int) -> dict:
    input_data = dict(domain)
    for k in missing_keys:
        input_data[k] = "（記載なし）"

    ppt_text = PPT_STYLES[style_idx % len(PPT_STYLES)].format(**input_data)
    template_text = config.load_text_template(config.TEMPLATE_PRESS_RELEASE)
    system_prompt, user_prompt = prompts.press_release_prompt(ppt_text, template_text)

    pr_text = generate_dospara_press_release_text(domain, missing_keys)

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": pr_text},
        ]
    }


def main():
    output_dir = root_dir / "training_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    train_file = output_dir / "train.jsonl"
    val_file = output_dir / "val.jsonl"

    all_samples = []
    missing_variations = [
        [],
        ["budget"],
        ["period", "schedule"],
        ["applicant", "dept"],
        ["details", "budget"],
        ["risks"],
    ]

    for domain in DOSPARA_DOMAINS:
        for missing in missing_variations:
            for style_idx in range(len(PPT_STYLES)):
                # Generate both Approval Doc training pairs and Press Release training pairs
                all_samples.append(generate_approval_sample(domain, missing, style_idx))
                all_samples.append(generate_press_release_sample(domain, missing, style_idx))

    random.seed(42)
    random.shuffle(all_samples)

    split_idx = int(len(all_samples) * 0.85)
    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]

    with open(train_file, "w", encoding="utf-8") as f:
        for item in train_samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(val_file, "w", encoding="utf-8") as f:
        for item in val_samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[OK] Generated Dospara-standard dataset successfully:")
    print(f"  -> Total samples : {len(all_samples)}")
    print(f"  -> Training set  : {len(train_samples)} lines -> {train_file}")
    print(f"  -> Validation set: {len(val_samples)} lines -> {val_file}")


if __name__ == "__main__":
    main()
