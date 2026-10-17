# 日本日照團康影片中文資料庫

給台灣日照中心、C 據點夥伴使用的團康活動資料庫。整理日本日照中心與照顧現場在 YouTube 公開分享的 350 支團康與體操影片，逐支看過影片畫面，提供中文活動名稱、玩法、訓練重點、參與方式、道具與帶領提醒，並可搜尋與篩選。

## 檔案

| 檔案 | 說明 |
|---|---|
| `index.html` | 網站（單一檔案，資料已內嵌） |
| `database.csv` | 完整資料，可用 Excel 開啟 |
| `data/videos.csv` | **人工整理的影片清單與中文玩法**（要修正或新增影片就改這個檔案） |
| `scripts/build_database.py` | 由 videos.csv 產生 database.csv / database.json，標籤依玩法描述自動判斷 |
| `scripts/build_webapp.py` + `template.html` | 產生 `index.html` |

## 更新方式

```bash
python3 scripts/build_database.py
python3 scripts/build_webapp.py
```

## 說明

- 中文玩法是依影片畫面整理的摘要，非官方翻譯；細節請以影片為準。
- 影片版權屬於各影片的原上傳者，本站只提供連結與嵌入播放。
