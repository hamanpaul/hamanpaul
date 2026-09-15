# Paul / hamanpaul

**嵌入式系統工程 · Agentic Engineering · 有邊界、可驗證、能累積經驗的自主工程**

我從裝置通訊、韌體整合與測試自動化出發，正在把日常工程工作整理成一套可協作的工具生態。
重點不是讓更多 Agent 同時寫 code，而是把「誰決定、誰執行、誰驗證、誰記住」分清楚，讓工具失敗時仍能依證據恢復，而不是重新猜一次。

> **想做到的事：Agent 可以提出解法，但不能只憑一句「完成了」放行。**
> 從原始 log、問題定義、變更、測試，到 review 與交付，都應留下可追溯的 artifacts；有用的經驗再回到下一次工作。

## 架構入口

**[互動式架構圖：hamanpaul.github.io]([https://hamanpaul.github.io/index.html](https://hamanpaul.github.io/hamanpaul/))** · [架構事實 facts.json](docs/facts.json) · [Archify 投影 architecture.json](docs/architecture.json) · [來源版本與摘錄索引](docs/source-manifest.json)

GitHub 檔案頁不會直接執行 HTML。下載 `docs/index.html` 後以瀏覽器開啟，即可使用縮放、搜尋、聚焦、關係追蹤與來源檢視；不需要啟動 server。檔名也適合日後以 GitHub Pages 從 `main /docs` 發布，但本次文件更新不代表 Pages 已啟用。

圖中內容以繁體中文撰寫；上游 Archify 的固定操作介面目前回退為英文。這是**公開 repo 的責任與代表性接點圖**，不是共同部署版本的證明，也不是完整 import graph。「可呼叫測試 CLI」與「隔離 CLI 評測」分別標示條件式組合與實驗室呼叫；線條樣式沿用 Archify 類型，不代表已部署程度，具體 `observed` / `declared` / `inferred` 依 `facts.json` 為準。

## 誰負責什麼

同一個「完成」，在不同層有不同意思。裝置回應了，不代表測試通過；測試通過了，不代表 PR 可合併；Agent 退出了，也不代表工作已交付。

| 權威／平面 | Repo | 擁有的責任 | 不應越界的責任 |
|---|---|---|---|
| 操作入口 | [paulshaclaw](https://github.com/hamanpaul/paulshaclaw) | CLI、bot、cockpit 與 operator-facing integration | 不另建 workflow lifecycle、domain verdict 或長期記憶權威 |
| 工作治理 | [paulsha-cortex](https://github.com/hamanpaul/paulsha-cortex) | Work / WorkflowRun / Job / Slice、派工、重試、review、delivery、completion | 不讓 domain tool 或觀測畫面自行改寫工作進度 |
| 長期經驗 | [paulsha-hippo](https://github.com/hamanpaul/paulsha-hippo) | Provenance、recall、applied attribution、reinforce、contradict、retire | 不接管派工，不管理 vendor 登入與憑證 |
| 變更完整性 | [paulsha-conventions](https://github.com/hamanpaul/paulsha-conventions) | Repo policy、文件與版號一致性、PR gate、generated facts 與 policy drift | 不等於領域測試引擎，也不會執行 `auto_build` 內的命令 |
| 測試執行與證據 | [testpilot-core](https://github.com/hamanpaul/testpilot-core) | Plugin SDK、core-owned 測試生命週期、evidence / trace、結果與報告 | 領域 cases、環境操作與 `evaluate()` 語意屬於 plugin；Agent 介入本身不是 Pass |
| 實體通訊 | [serialwrap](https://github.com/hamanpaul/serialwrap) | `serialwrapd` 擁有 UART，提供 single-writer 仲裁、共享 console、WAL 與 recovery | 不把通訊成功等同於領域測試成功 |

上述分工依各 repo 已宣告的契約與可查核的實作整理；精確來源 SHA、原始路徑、行號與摘錄 hash 見[來源索引](docs/source-manifest.json)。不以未量測的「已上線」「Core 穩定」或通用效能倍數代替證據。

### 三條重要邊界

**操作入口不等於控制器。** `paulshaclaw` 透過 control client / CLI shim 使用 Cortex，記憶平面則交給 Hippo。Cortex 內的 Persona 是角色與範圍契約，不是執行中的 Agent；Monitor 是狀態投影，不是任意推進生命週期的第二個 Manager。

**測試生命週期不等於工作生命週期。** TestPilot 在 core-owned path 執行測試並保存 plugin 產生的 canonical verdict；Cortex 管理工程工作的交付條件。`Job exited` 不足以證明 Slice completed，還要看必要驗證、review 與候選變更是否進入目標分支。

**建置契約不等於建置服務。** Conventions 的 `auto_build` 是可讓執行者讀取的 per-project 宣告；policy engine 只驗其格式，不執行其中命令。真正的 build/test 仍由被授權的執行者或專案 CI 負責。Cortex 已有 `policy_check.preflight` 的 typed-argv adapter，但不因此取得領域判定權。

## 從一件工程工作看協作

目標路徑是：人或上游問題來源提出工作，Cortex 依契約安排執行；Agent 帶著相關經驗與明確範圍產生 artifacts，再由對應的測試、policy 與 review 接點檢查，最後依遠端證據完成交付。經驗是否真的被閱讀、採用並改善結果，則要由 Hippo 的 attribution 與 outcome 證據回答。

對裝置驗證，可以使用 **TestPilot → domain plugin → serialwrap → DUT / STA**；對不需硬體的測試，plugin 不必經過 UART。公開例子包括 TestPilot 的 [`sample_echo`](https://github.com/hamanpaul/testpilot-core/tree/main/examples/sample_echo) 與 serialwrap 的 [`serialwrap_reliability`](https://github.com/hamanpaul/serialwrap/tree/main/reliability)。

圖中的 **Agent → TestPilot** 是「可依任務呼叫測試 CLI」的條件式組合，**不是 Cortex 已內建 TestPilot 專用派工的宣稱**。這次盤點沒有執行整條跨 repo 實機 E2E，也不宣稱所有交付 outcome 已自動回寫 Hippo。缺口保留在 `facts.json` 的 `unknowns`，不靠畫一條箭頭就視為完成整合。

## 評測與支援工具

| Repo | 定位 | 與主系統的界線 |
|---|---|---|
| [paulsha-patchmud](https://github.com/hamanpaul/paulsha-patchmud) | Frozen fixture、確定性評分、可重播的 coding-agent 評測實驗室 | 對 Cortex / Hippo 無 runtime 依賴；隔離 CLI 呼叫與正式工作執行不是同一程序。結果可透過檔案契約供 roster / routing 參考，不直接接管正式工作 |
| [log-generator](https://github.com/hamanpaul/log-generator) | 透過 serialwrap 跑長時間實機 reboot-log soak，可搭配已安裝的 fault injector | 不是單純仿真 log 產生器，也不是原始 UART 證據的權威 |
| [ask-bridge](https://github.com/hamanpaul/ask-bridge) | 以真實瀏覽器與 MCP / CDP 提供模型互動的 CLI 接點 | 支援工具，不因存在於帳號下就成為 Cortex 的必要 runtime 依賴 |
| [new-project-template](https://github.com/hamanpaul/new-project-template) | Policy metadata、版本／changelog、agent 規範與 CI 的起始骨架 | 產生專案，不是常駐服務 |
| [.github](https://github.com/hamanpaul/.github) | 帳號層級 community health defaults | 不承載 policy engine、workflow templates 或下游自動化邏輯 |

這不是帳號所有 repo 的清單。僅列與本文工程主軸有關、且具有公開來源的專案；私有工作與機器本地設定不納入公開架構事實。

## 我在意的工程原則

**一個事實，一個權威。** Runtime 狀態、領域測試結果、repo policy 與長期經驗各有自己的 owner；本 profile 只是導航，不取代任何 repo 的 canonical contract。

**先有 artifact，再承認 transition。** Prompt、程序 exit code 或口頭結論都不能替代可驗證的交付證據。Deterministic gate 與必要的獨立 review 是不同層，不把所有工程判斷都誤稱為「零 LLM 裁判」。

**自主必須有邊界。** 失敗時依既有 retry、fallback、workaround 或 escalation 推進，避免每次遇到工具障礙就擴張成重做整個工作流。遇到權限、scope 或必要證據缺失，應明確停下，而不是降低 gate。

**實體結果與學習效果都要能回查。** 裝置事實以原始輸出為準；記憶的價值看後續工作是否真的使用並改善結果，不只看累積了多少筆筆記。

## 目前要收斂的方向

優先把既有能力接成可重複驗收的工作案例：減少旁邊再站一個 Agent 看顧的需求；讓工作卡住時能清楚說明原因與下一步；用相同 source / candidate / evidence 核對跨 repo 的認知；將經驗的 recall、實際採用與結果分開量測。這些是推進方向，不是本文已證明的完成狀態。

## 文件維護

`docs/facts.json` 是本圖唯一的語意來源；`docs/architecture.json` 保存 native Archify 投影與版面，`docs/index.html` 由固定版本的原始 Archify renderer 產生，不手改 HTML。

來源摘錄在 `docs/evidence/`。它們是[來源索引](docs/source-manifest.json)指定公開 commit 的原始位元組，不是從架構圖倒推的證據；每筆均可比對原 repo、原路徑、原行號與 SHA-256。`facts.repository.revision` 固定到含有這些摘錄的本 repo commit，不要求等於之後的 HTML 交付 commit。

更新時先核對新來源，再改 facts；只調版面不應改動元件 ID、責任或方向。重建與檢查方式見 [`docs/BUILD.md`](docs/BUILD.md)。文件驗證、瀏覽器驗證、視覺檢視、使用者接受，以及實機 E2E 是分開的結論。
