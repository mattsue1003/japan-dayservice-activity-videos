#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本日照中心團康影片資料庫：產生 JSON / CSV

資料來源：data/videos.csv（每支影片一列，人工逐支看過影片畫面整理）
  video_id, category, zh_title, jp_title, how_to_play, standing, length_sec, views, publish_date, portrait
標籤（訓練重點、參與方式、姿勢、場地、道具、準備程度）由玩法描述的關鍵字自動判斷，
帶領提醒依標籤組合產生。要修正或新增影片，改 data/videos.csv 後重新執行本程式。
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_JSON = ROOT / "database.json"
OUT_CSV = ROOT / "database.csv"
GAME_CATS = {"團康遊戲", "一條毛巾就能玩", "體操與腦力訓練"}

# ---- 標籤規則（依中文玩法描述判斷） --------------------------------------
GOAL_RULES = [
    ("下肢肌力", r"腳|踢|踩|踏|腳趾"),
    ("上肢與肩臂", r"手腕|握力|投|拋|丟|揮|拍|擊|推|拉|舉|搧|打|甩|刷|撥|掛|傾斜|抬|抖|運|轉動|釣|抽|持"),
    ("手眼協調", r"投|拋|接|瞄|射|擊|滾|彈|打|套|夾|撈|停在|對準|攔|控|運|送|滑|落|吹|釣|抽|放穩"),
    ("手指精細動作", r"指尖|插進|手部協調|夾|筷|曬衣夾|麻將|拼圖|棋|按壓|彈珠|疊|撿|折"),
    ("認知與反應", r"腦力|猜|聯想|填字|找字|叫聲|節奏|顏色|同色|分色|色塊|指令|口令|喊|記憶|順序|數字|相反|迷宮|拼圖|圈叉|○×|尋寶|時機|紅或|九宮格|賓果"),
    ("平衡與姿勢控制", r"防跌|平衡|站姿|揮擊|上舉|舉高"),
    ("社交與團隊合作", r"多人|全體|分隊|大家|兩排|一排|合作|合力|接力|圍圈|圍成|兩人|雙人|夥伴|兩隊|對戰"),
]
PART_RULES = [
    ("雙人搭檔", r"兩人|雙人|夥伴|對坐"),
    ("團隊合作", r"多人|大家|一起|合力|一排|兩排|圍圈|圍成|合作"),
    ("接力傳遞", r"接力|傳遞|傳給|傳下去|傳球"),
    ("競賽對戰", r"對戰|兩隊|搶|比賽|對抗|計分|勝|最遠|最快|得分"),
]
PLACE_RULES = [
    ("桌面", r"桌"),
    ("地面", r"地上|地板|地面|踢|腳|赤腳"),
    ("牆面／立架", r"牆|立架|立起|立式|高架|架上|門上"),
]
PROP_RULES = [
    ("毛巾／大布", r"毛巾|大布|塑膠布"),
    ("一般球類", r"(?<!乒乓)(?<!氣)(?<!羽毛)(?<!毛巾)球(?!拍|棒|瓶)"),
    ("乒乓球", r"乒乓"),
    ("氣球", r"氣球"),
    ("杯子", r"杯"),
    ("紙箱／紙板", r"紙箱|紙板|箱"),
    ("浮力棒", r"浮力棒"),
    ("繩子", r"繩"),
    ("籃子／桶子", r"籃|桶|篩網"),
    ("呼拉圈", r"呼拉圈|圓環"),
    ("長桿／球棒", r"長桿|桿|棒子|球棒|掃把|竹竿|釣竿|長夾|筷"),
    ("沙包", r"沙包"),
    ("扇子", r"扇"),
    ("曬衣夾／衣架", r"曬衣夾|衣架"),
    ("羽毛球", r"羽毛球"),
]
DIY_PATTERN = r"洞|迷宮|軌道|洞板|有洞|發射|滑道|滑槽|轉盤|轉台|轉輪|蹺蹺板|架上|立架|作法|彈射|斜坡|鐵網|高塔|多層|導軌"


def tags(text, rules):
    return [name for name, pat in rules if re.search(pat, text)]


def fmt_len(sec):
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def episode_no(title):
    t = unicodedata.normalize("NFKC", title)
    m = re.search(r"(?:No|第|part[-ー.]?\s*)(\d+)", t, re.I)
    return int(m.group(1)) if m else None


def clean_jp_title(raw):
    t = unicodedata.normalize("NFKC", raw)
    t = re.sub(r"#\S*", "", t)
    t = re.sub(r"[\U0001F300-\U0001FAFF]", "", t)
    t = re.sub(r"\s+", " ", t).strip(" !！-")
    return t or raw.strip()



def leading_tips(cat, goals, places, parts, props, standing):
    tips = []
    if cat == "一條毛巾就能玩":
        tips.append("影片使用印有數字與圖案的遊戲毛巾，一般長毛巾或在大毛巾上貼數字、圖案標示也能進行。")
    if cat == "體操與腦力訓練":
        tips.append("可以直接播放影片跟著做；先放慢速度示範一次，跟不上的長輩做簡化版也沒關係。")
    if standing:
        tips.append("站姿進行時，旁邊安排工作人員近身保護，或先改成坐姿版本。")
    if "下肢肌力" in goals:
        tips.append("確認椅子穩固、輪椅已煞車；赤腳活動前先檢查足部皮膚，並先做腳踝暖身。")
    if "地面" in places and not standing:
        tips.append("活動區地面保持淨空，滾出的球由工作人員撿回，避免長輩彎腰或起身撿拾。")
    if "認知與反應" in goals:
        tips.append("先從較少選項、較慢節奏開始，熟悉規則後再增加變化；失智長輩可搭配手勢或實物提示。")
    if "競賽對戰" in parts:
        tips.append("分組時讓能力平均，計分以鼓勵為主，讓每位長輩都有成功的機會。")
    if "團隊合作" in parts or "接力傳遞" in parts:
        tips.append("重點在彼此出聲配合，可請長輩互相喊口令，增加互動與交流。")
    if "氣球" in props:
        tips.append("氣球速度慢、較容易擊中，適合反應較慢或上肢力氣較小的長輩。")
    if "手指精細動作" in goals and len(tips) < 3:
        tips.append("可依手部功能調整物品大小與夾取工具，力氣較小者改用較大的物品。")
    if len(tips) < 2:
        tips.append("帶領前先示範一次，依長輩能力調整距離、目標大小與次數，讓每個人都能得分。")
    return tips[:3]


def main():
    rows = list(csv.DictReader(open(DATA / "videos.csv", encoding="utf-8")))
    records = []
    for n, r in enumerate(rows, start=1):
        vid, cat = r["video_id"], r["category"]
        desc, title = r["how_to_play"].strip(), r["zh_title"].strip()
        text = title + "。" + desc
        standing = r["standing"] == "1" or "站姿" in desc
        is_game = cat in GAME_CATS
        goals = tags(text, GOAL_RULES) if is_game else []
        parts = (tags(text, PART_RULES) or ["個人挑戰"]) if is_game else []
        posture = (["站姿"] if standing else ["坐姿可進行"]) if is_game else []
        places = tags(text, PLACE_RULES) if is_game else []
        props = tags(text, PROP_RULES) if cat != "精選合輯" else []
        if not is_game:
            prep = "—"
        elif cat == "一條毛巾就能玩":
            prep = "免準備（一條毛巾）"
        elif cat == "體操與腦力訓練" and not props:
            prep = "免準備"
        elif re.search(DIY_PATTERN, text):
            prep = "需自製教具"
        else:
            prep = "簡單準備"
        sec = int(r["length_sec"] or 0)
        portrait = r["portrait"] == "1"
        records.append({
            "id": f"No.{n:03d}",
            "index": n,
            "video_id": vid,
            "format": "直式短片" if portrait else "影片",
            "category": cat,
            "zh_title": title,
            "jp_title": r["jp_title"].strip(),
            "how_to_play": desc,
            "training_goals": goals,
            "participation": parts,
            "posture": posture,
            "place": places,
            "props": props,
            "prep_level": prep,
            "leading_tips": leading_tips(cat, goals, places, parts, props, standing) if is_game else [],
            "length_sec": sec,
            "length_text": fmt_len(sec) if sec else "",
            "views": int(r["views"] or 0),
            "publish_date": r["publish_date"],
            "url": (f"https://www.youtube.com/shorts/{vid}" if portrait else f"https://www.youtube.com/watch?v={vid}"),
            "thumbnail_url": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        })

    json.dump(records, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cols = [
        ("編號", "id"), ("中文活動名稱", "zh_title"), ("日文標題", "jp_title"), ("影片分類", "category"),
        ("影片格式", "format"), ("玩法描述", "how_to_play"), ("訓練重點", "training_goals"),
        ("參與方式", "participation"), ("姿勢", "posture"), ("場地", "place"), ("道具", "props"),
        ("準備程度", "prep_level"), ("帶領提醒", "leading_tips"), ("影片長度", "length_text"),
        ("觀看次數(2026-10-17)", "views"), ("發布日期", "publish_date"), ("YouTube連結", "url"), ("Video_ID", "video_id"),
    ]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([c for c, _ in cols])
        for r in records:
            w.writerow(["、".join(r[k]) if isinstance(r[k], list) else ("" if r[k] is None else r[k]) for _, k in cols])
    print(f"已產生 {len(records)} 筆資料")


if __name__ == "__main__":
    main()
