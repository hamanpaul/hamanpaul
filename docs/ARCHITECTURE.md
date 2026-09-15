# 架構事實與重建

本頁是 profile 架構的維護說明，不是系統部署或 runtime E2E 驗收報告。

## 檔案責任

| 檔案 | 用途 |
|---|---|
| `facts.json` | 唯一架構語意來源：穩定 ID、責任、關係、來源範圍及 unknowns |
| `index.json` | 原生 Archify architecture IR；只增加位置、路由與呈現資訊 |
| `index.html` | 原生 Archify 未經手改的獨立 HTML；實際瀏覽器驗收入口 |
| `source-manifest.json` | 每份公開來源的外部 commit、Git blob SHA、SHA-256、原始網址與本地快照位置 |
| `source-lock.json` | 已閱讀來源的 README blob pin 與選定工具版本；refresh 時來源變更即停止 |
| `evidence/*/README.md` | 公開原始 README 的逐 byte 快照，不是 AI 撰寫的架構摘要 |
| `toolchain.json` | Renderer、事實來源與已審查產物的固定版本和 hashes |

架構事實固定到本 repo 的來源快照 commit `ec017919d4fa5770bca8e859e369518c71f4eb1c`。因此後續更新 README／HTML 不會造成「新文件引用自己證明自己」的循環。原始來源的外部 commit 另記在 manifest；點圖中來源會先到本 repo 的固定快照，追溯原 repo 可查 manifest。

## 範圍與限制

這是公開 repo 的責任與已宣告接點。所有 facts 的 `basis` 都是 `declared`，不把 README 聲明冒稱成已觀測的 runtime 行為。`unknowns` 保留跨 repo 部署閉環、經驗效果與 PatchMUD routing 採納狀態；未證實的關係不畫成既成路徑。

圖中有 11 個元件、11 條具方向的關係。外部 Agent／CLI 是能力類別，不表示 Cortex、TestPilot、PatchMUD 共用同一個進程、權限或 provider session。Template 與 `.github` 是啟動／社群文件基礎，保留在 README 的完整矩陣，不冒充 runtime service。沒有宣告部署或安全隔離 boundary。

本次只讀取公開 README 與 Git metadata，沒有執行硬體測試、派工、存取 provider 憑證、修改 GitHub Pages 或合併 PR。

## 重建與驗證

原生 renderer 固定為 `tt-a1i/archify@a07fa1d5b2a10cbea110c5a2be2817397a301cdc`，Architecture Fact Layer 使用版本 `c9510a2299b44a9fc6b6c75186ef2aa533abb6ef`。本 repo 不包含或依賴私有 skill 的程式碼；公開 CI 使用原生 renderer 與本 repo 的獨立回歸檢查。

```bash
git clone https://github.com/tt-a1i/archify.git /tmp/profile-archify
git -C /tmp/profile-archify checkout a07fa1d5b2a10cbea110c5a2be2817397a301cdc
python3 scripts/verify_profile_architecture.py --archify-root /tmp/profile-archify/archify
python3 -m unittest discover -s scripts -p 'test_*.py' -v
node /tmp/profile-archify/archify/bin/archify.mjs visual-check docs/index.html --json
python3 scripts/check_profile_browser.py --output /tmp/profile-browser
```

前兩項使用 Python 標準函式庫、Git 與 Node.js；瀏覽器檢查另需 Chromium／Chrome、Playwright 與 CJK fonts。檢查預設唯讀；native verifier 在暫存目錄重建後逐 byte 比對，不覆寫 HTML。

`--generate` 僅供明確重建：舊 HTML 存在時拒絕覆寫。正常 CI 不使用它，也不回寫任何檔案或修補產物。若語意或版面變更，先審查並更新 facts／IR，再透過原生 `deliver` 產生新 HTML、重新檢查，最後更新 toolchain hashes；不可改 hash 來掩蓋尚未檢查的變更。

## 更新來源

先讀取原 repo 新版本，確認仍公開、辨識責任差異，再更新 `source-lock.json` 中對應 README blob。明確執行 `python3 scripts/freeze_sources.py` 會抓取公開來源、固定外部 commit 並驗證 Git blob；任一不符就拒絕，不自動用新版資料覆蓋舊認知。

來源快照與 manifest 要先成為獨立 commit，然後讓 facts 的 `repository.revision` 指向該 commit。重新核對 evidence line ranges／hashes，保留未變的 stable IDs。更新 native IR 只能投影同一批元件和關係；不能為了排版自行添加接點。再重建 HTML 與驗證收據。

## 驗收聲明必須分開

原生 `deliver` 的 9／9 showcase 是 deterministic artifact 檢查，不代表人已看懂圖。`visual-check` 與本 repo browser gate 以實際 `file://` 開啟已交付的 HTML，檢查 SVG 元件、具箭頭的路徑、來源連結、focus／reach／finder／theme、四種桌面尺寸及窄螢幕，並保存綁定 HTML SHA-256 的收據和截圖。最後仍需檢視像素，確認文字、方向與路線可讀。

本機 sandbox 的 `file://` 若被拒絕，只能明示為未通過該 transport；content 預覽屬補充資料，不能冒稱 file-navigation 證據。CI 檢查 artifacts 是機械驗證與視覺回顧依據，不是使用者接受、真實設備驗證或跨 repo E2E 的替代品。
