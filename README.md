# REHA SHINE 團康影片中文資料庫

給台灣日照中心、C 據點夥伴使用的團康活動資料庫。整理日本宮崎縣都城市日照中心「リハシャインみやこんじょ」在 YouTube 頻道 [REHA SHINE](https://www.youtube.com/@REHASHINE) 公開的 277 支影片，提供中文活動名稱、玩法、訓練重點、參與方式、道具與帶領提醒，並可搜尋與篩選。

**網站：** https://mattsue1003.github.io/rehashine-video-database/

## 檔案

| 檔案 | 說明 |
|---|---|
| `index.html` | 網站（單一檔案，資料已內嵌） |
| `rehashine_database.csv` | 完整資料，可用 Excel 開啟（執行 build_database.py 另會產生 JSON） |
| `data/video_notes.csv` | **人工整理的中文名稱與玩法**（要修正內容就改這個檔案） |
| `data/raw_videos.json` | 影片清單與日文原標題 |
| `data/youtube_meta.json` | 影片長度、觀看次數、發布日期（2026-10-17 擷取） |
| `scripts/build_database.py` | 由上述資料產生 JSON/CSV，標籤依玩法描述自動判斷 |
| `scripts/build_webapp.py` + `template.html` | 產生 `index.html` |

## 更新方式

```bash
python3 scripts/build_database.py
python3 scripts/build_webapp.py
```

## 說明

- 中文玩法是依影片畫面逐支整理的摘要（Shorts 多半沒有旁白），非官方翻譯；細節請以影片為準。
- 影片版權屬於 REHA SHINE／リハシャインみやこんじょ，本站只提供連結與嵌入播放。
