# Architecture Fact Layer：重建與驗證

## 哪一份是權威

- `facts.json`：本 profile 圖的語意權威；元件、方向、責任、basis、evidence、unknowns 均在此。
- `architecture.json`：原生 Archify 投影與版面；不得另加沒有 facts 的元件、關係或部署邊界。
- `index.html`：原始 Archify renderer 的完整單檔輸出；不手動改 HTML，不引用 CDN。
- `source-manifest.json` 與 `evidence/*.txt`：精確公開來源與原始摘錄。摘錄不是把本圖的敘述再包裝成證據。

此圖是 portfolio overview，不展開 Cortex 的七階段、Card、Job、AgentInstance 細節。它們不應因為本圖省略內部流程就被理解成一對一；請回 Cortex 的來源契約核對。

## 固定工具版本

原始引擎：`tt-a1i/archify`，commit `d673e8300df60a5c8166abe78787fdc78f6b8000`；使用其 `archify/` 子目錄，不修改 renderer。需要 Python 3、Git、Node.js；瀏覽器檢查另外需要 Chrome / Chromium。

```bash
git clone https://github.com/tt-a1i/archify.git /tmp/profile-archify
git -C /tmp/profile-archify checkout d673e8300df60a5c8166abe78787fdc78f6b8000
ENGINE=/tmp/profile-archify/archify

python3 docs/build_architecture.py verify
python3 -m unittest discover -s docs -p 'test_architecture.py' -v
python3 docs/build_architecture.py check-html --archify-root "$ENGINE"
node "$ENGINE/bin/archify.mjs" visual-check docs/index.html --json
```

`check-html` 先核對 facts 與投影，再由固定版本的原始引擎重繪至暫存檔並逐 byte 比對；不會覆寫已交付 HTML。Native showcase receipt 必須為 9/9、0 errors、0 warnings。單純 schema 通過不等於此門檻。

## 更新來源

先編輯 manifest 到經過檢視的公開 commit／行號／hash，再執行：

```bash
python3 docs/build_architecture.py snapshot --sources-root /tmp/profile-sources
git add docs/evidence docs/source-manifest.json
git commit -m 'docs: pin reviewed public architecture sources'
python3 docs/build_architecture.py pin --revision "$(git rev-parse HEAD)"
```

接著人工檢視並更新 `facts.json` 及投影；不要只改來源 SHA 就假定所有語意仍成立。`snapshot` 只讀取 allowlist 內 repo 的 Git blobs，不執行摘錄中的程式、命令或 instructions。可用 `provenance --sources-root /tmp/profile-sources` 重新核對已有本機 Git blobs。

```bash
python3 docs/build_architecture.py verify
python3 docs/build_architecture.py render --archify-root "$ENGINE"
python3 -m unittest discover -s docs -p 'test_architecture.py' -v
node "$ENGINE/bin/archify.mjs" visual-check docs/index.html --json
```

## 驗收邊界

文字使用繁體中文；上游固定 UI 僅支援 en／zh-CN，因此不設定 `meta.locale`，固定介面與 HTML lang 回退為英文。所有主要節點與箭頭在預設畫布呈現；搜尋／聚焦只檢視同一份拓撲。

瀏覽器要以真實 `file://` 開啟，量測 1440×900、1600×1000、1920×1080、2048×1320，桌面不得有 document overflow；窄螢幕允許垂直捲動。原始 `visual-check` 輸出綁定 HTML SHA-256、瀏覽器版本與四個 viewport，仍需另行看實際畫面。

本 repo 的 Python 測試是 profile 適配的來源、投影與負向控制，不冒充其他 repo 的全部單元測試。文件／機器 gate、瀏覽器行為、視覺檢視、使用者接受、runtime E2E 分別陳述；本次文件工作不會連接 DUT、派工、改 vendor 憑證、啟用 Pages 或合併 PR。
