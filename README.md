# Paul Haman

**Embedded Systems · Agentic Engineering · 以證據串起受治理的工程閉環**

我從嵌入式裝置通訊、韌體整合與實機測試出發，逐步把日常工程工作拆成可協作、可驗證、可追溯的工具與契約。現在關注的不只是讓 Agent 寫出 patch，而是讓它知道自己能決定什麼、該交出什麼證據，以及什麼情況必須停下來。

> **目標不是讓 AI 宣稱「修好了」，而是讓變更有證據、驗證有裁決、交付有紀錄，最後把經驗連回實際結果，讓下一次少走同一段彎路。**

## 系統架構

**[開啟互動式架構圖](docs/index.html)** · [架構事實](docs/facts.json) · [Archify JSON](docs/index.json)

這是一張跨 repo 的**責任與契約接點圖**，不是把所有專案硬串成同一個程式：`paulshaclaw` 是操作入口，`paulsha-cortex` 管工作生命週期，`paulsha-hippo` 管經驗；測試、實體通訊與 repo 規範則各有自己的權責。

圖中實線表示已宣告的核心接點，虛線表示選配或特定用途；policy 線表示變更規範，不是派工指令。所有關係均固定到公開來源的版本；**來源契約存在，不等於同一部署已完成端到端驗證**。範本與社群預設檔案列在下方矩陣，不畫成 runtime service。

GitHub 檔案頁不直接執行這份 HTML；下載或 clone 後，以瀏覽器開啟 `docs/index.html` 即可操作，不需要 server。架構文字採繁體中文；原生 Archify 的固定操作介面使用英文。本次沒有啟用或變更 GitHub Pages 設定。

## 公開專案矩陣

### 1. Agent 操作、治理與經驗

| Repo | 負責什麼 | 不應混淆的界線 |
|---|---|---|
| [`paulshaclaw`](https://github.com/hamanpaul/paulshaclaw) | Operator shell：CLI、bot、cockpit、部署與操作整合入口 | 接入 Cortex／Hippo，不重新擁有它們的生命週期或經驗權威 |
| [`paulsha-cortex`](https://github.com/hamanpaul/paulsha-cortex) | Work／WorkflowRun／Job／Slice 的生命週期、派工、retry、review 與交付 | Persona 是角色契約，AgentInstance 才執行；domain tools 回傳 artifacts，不改寫工作生命週期 |
| [`paulsha-hippo`](https://github.com/hamanpaul/paulsha-hippo) | Session 蒸餾、dream、wakeup／recall，以及來源、採用歸因與經驗生命週期 | 找到或讀到筆記不等於已採用，更不等於已證明有效；不管理外部 CLI 的登入憑證 |
| [`paulsha-patchmud`](https://github.com/hamanpaul/paulsha-patchmud) | 凍結關卡、確定性評分與可重播的 coding-agent 評測實驗室 | 不是生產控制器；對 Cortex／Hippo 零 runtime 依賴，不把評測結果畫成自動上線指令 |

### 2. 實體通訊與測試驗證

| Repo | 負責什麼 | 不應混淆的界線 |
|---|---|---|
| [`serialwrap`](https://github.com/hamanpaul/serialwrap) | `serialwrapd` 持有真實 UART；多方共享、single-writer 仲裁、WAL 與 recovery | 提供原始實體證據，不替領域測試決定 Pass／Fail |
| [`log-generator`](https://github.com/hamanpaul/log-generator) | 透過 serialwrap 執行重啟耐久測試，支援已配置目標上的故障注入 | 是實機 reboot-log soak toolkit，不只是模擬日誌產生器 |
| [`testpilot-core`](https://github.com/hamanpaul/testpilot-core) | Plugin-based 測試 host：SDK、執行生命週期、證據、trace、報告與 canonical verdict 保存 | 領域案例、環境操作與 `evaluate()` 語意由 plugin 定義；Agent 介入不代表驗證通過 |

TestPilot 的核心擴充模型不限定嵌入式領域，但也不代表任意領域都已開箱驗證。公開參考包括不需要硬體的 `sample_echo`，以及位於 serialwrap repo 的 `serialwrap_reliability`。**只有需要 UART 的工作流程才依賴 serialwrap**；plugin 自訂 runner 的責任也不能與預設 core-owned 路徑混為一談。

### 3. Repo 規範與啟動基礎

| Repo | 負責什麼 | 不應混淆的界線 |
|---|---|---|
| [`paulsha-conventions`](https://github.com/hamanpaul/paulsha-conventions) | 文件、版號、分支、PR、generated facts 與 policy drift 的規範與確定性檢查 | Policy 通過不等於領域測試通過；規範引擎不接管 Cortex 的派工或交付狀態 |
| [`new-project-template`](https://github.com/hamanpaul/new-project-template) | 新專案的最小骨架、policy metadata、agent 規範檔與固定版本的 CI workflow | Bootstrap 起點，不是常駐控制器 |
| [`.github`](https://github.com/hamanpaul/.github) | 帳號層級 community health defaults；下游缺少個別檔案時提供支援的預設內容 | 只負責社群文件與 PR 範本，不承載 policy engine 或 workflow templates |

本頁聚焦這三類核心專案，不把所有工具、fork 或私有工作 repo 都列成生態系依賴。矩陣依 [固定版本的公開來源](docs/source-manifest.json) 整理，不以「已上線／穩定」標籤代替可查證的能力與界線。

## 想完成的工程閉環

```text
真實證據與明確問題
  → 範圍受控的診斷與變更
  → 專案建置、領域測試與獨立審查
  → Policy 檢查與可追溯交付
  → 帶來源、採用歸因與結果的經驗回饋
```

**這是整合目標，不是目前所有箭頭都已全自動接通的保證。** 個別工具有自己的能力與契約，跨 repo 的接線仍要以具體部署和驗證產物證明。尤其不把 `Cortex → build → TestPilot → policy → Hippo` 畫成每項工作必經的既成管線，也不把 PatchMUD 的檔案輸出等同於已部署的自動 routing。

完成一次工作，至少要能回答：改了什麼、用什麼證據判定、誰有權推進狀態，以及這次經驗是否真的被採用並產生結果。這些問題分別由適當的工具與契約回答，不交給同一個 Agent 自我認證。

## 工程原則

**一種事實，一個權威。** 操作入口、工作生命週期、領域 verdict、原始 UART 證據、repo policy 與經驗狀態各自分工；整合不代表接管別人的裁決權。

**先有產物，再推進狀態。** 診斷、變更、測試與交付都應留下可核對的產物。Agent 可以提出方案，但不能以自己的說法取代獨立驗證；實體裝置的觀測也不能被推測覆蓋。

**自主必須有邊界，學習必須連回結果。** 角色、範圍、預算與恢復路徑要明確；證據不足時保留 unknown，而不是補出成功故事。記憶不只追求筆記增加，更要區分 recall、applied 與後續結果。

## 目前關注

把跨 repo 的 Golden Path 做成可重現的整合案例；守住 TestPilot 的 core／plugin 與 Agent 建議邊界；持續改善 serialwrap 的實機通訊可靠性，以及 Hippo 經驗的來源、採用歸因與結果連結。

架構的維護與驗證方式見 [架構文件說明](docs/ARCHITECTURE.md)。語意先更新 `facts.json`，再更新呈現 JSON 並以固定版本的原生 Archify 重建 HTML；不另外手改 HTML 或維護第二份矛盾拓撲。
