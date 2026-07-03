Paul Haman

嵌入式系統 · Agentic Engineering · 受治理的自主軟體維護

我正在建立一套以嵌入式裝置為核心的工程系統：從 UART、長期 log 分析與事件診斷，到 Persona-governed SDD／TDD、可重現建置、DUT 確定性驗證，以及跨專案 policy-as-code 治理。

«目標不是讓 AI 自己宣稱「修好了」，而是讓診斷、變更、建置、測試與治理各自留下可稽核證據，再由 deterministic gate 決定是否通過。»

系統層級與關係

DUT / STA / UART
       │
       ▼
serialwrap
硬體通訊與 UART 基礎設施
       │
       ├───────────────┐
       ▼               ▼
LogSensing        IntelliDbgKit
長期 log 情報      單次事件重現、診斷、證據與共識
       │               │
       └───────┬───────┘
               ▼
paulshaclaw Persona SDD / TDD Pipeline
規格 → 角色分工 → Scope Gate → RED / GREEN → Review
               │
               ▼
Auto Build Contract
setup → steps → artifacts → verify
               │
               ▼
TestPilot
嵌入式裝置測試、證據蒐集與 deterministic verdict
               │
               ▼
paulsha-conventions
跨 repo policy、文件一致性、安全、CI 與 merge gate
               │
               ▼
paulshaclaw Manager / Memory / Audit
編排、記憶、重試、回滾、升級與操作介面

核心專案

層級| Repo| 主要責任| 工程成熟度快照*
硬體通訊基礎設施| "serialwrap" (https://github.com/hamanpaul/serialwrap)| UART multiplexing、DUT／STA 通訊與上層 transport 基礎| 82%
長期 Log Intelligence| LogSensing| 累積 log 分析、重複模式、趨勢與歷史上下文| 待完整 review
事件診斷| "IntelliDbgKit" (https://github.com/hamanpaul/IntelliDbgKit)| 故障重現、證據蒐集、多代理分析、共識與 veto gate| 64%
變更工程與編排| "paulshaclaw" (https://github.com/hamanpaul/paulshaclaw)| Manager、memory、lifecycle、Persona-governed SDD／TDD、audit| 72%
建置契約| "paulsha-conventions" (https://github.com/hamanpaul/paulsha-conventions) "auto_build"| 機器可讀的 setup、steps、artifacts 與 verify 契約| 74%
系統驗證| "testpilot-core" (https://github.com/hamanpaul/testpilot-core)| Plugin-based embedded verification 與 deterministic verdict kernel| 81%
工程治理| "paulsha-conventions" (https://github.com/hamanpaul/paulsha-conventions)| 跨 repo policy enforcement、版本、文件、安全與 CI 一致性| 91%
新專案 Bootstrap| "new-project-template" (https://github.com/hamanpaul/new-project-template)| 建立符合 conventions 的專案骨架與 reusable policy workflow| 高成熟度基礎設施

* 2026 年 7 月工程快照。百分比綜合評估：核心實作、runtime 接線、測試／實機證據與可交付性；不是程式碼品質分數，也不是永久固定值。

各層責任邊界

1. Hardware Transport Plane

"serialwrap" 將 UART 與實體裝置通訊包裝為上層測試與診斷系統可穩定使用的 transport。它是整套系統碰觸 DUT／STA 的基礎設施，而不是單純的 helper script。

2. Knowledge & Diagnostic Plane

- LogSensing：分析長期累積 logs，建立 recurrent pattern、趨勢與歷史案例。
- IntelliDbgKit：針對單次 incident 進行重現、診斷、證據收斂與候選根因分析。

兩者分別處理「長期經驗」與「當下事件」，避免每次除錯都從零開始。

3. Governed Change Plane

"paulshaclaw" 的 Persona pipeline 不是單純 patch generator，而是把診斷結果轉成受治理的工程流程：

problem statement
→ proposal / spec / acceptance criteria
→ planner / builder / reviewer
→ role scope + handoff manifest
→ failing regression test
→ implementation
→ review

4. Build & Verification Plane

- Auto Build：以 ".paul-project.yml" 提供 per-project 可重現建置契約。
- TestPilot：負責測試執行、證據蒐集與最終 pass／fail verdict。

AI 可以提供 diagnosis、advisory 與 remediation，但不能自己決定最終測試結果。

5. Governance & Control Plane

- paulsha-conventions：負責跨 repo policy、文件與程式碼同步、版本、secret scan、workflow pinning 與 merge gate。
- paulshaclaw Manager：負責調度、狀態、重試、回滾、升級、memory 與 audit trail。

目前整合狀態

個別元件大多已有可運行實作；目前主要工作是完成跨 repo 的端到端維護閉環：

log / test failure
→ diagnosis artifact
→ governed specification
→ TDD implementation
→ reproducible build
→ DUT deterministic verification
→ policy gate
→ promote / retry / rollback / escalate
→ 結果回填長期記憶與 LogSensing

目前端到端整合成熟度：約 55–58%。

最大的剩餘工作不是增加更多 agent，而是統一：

- maintenance "case_id" / "run_id"
- 跨 repo artifact contract
- 自動 handoff 與 failure routing
- retry budget、approval 與 rollback semantics
- 一條可重播的 golden-path 實機案例

工程原則

- Artifact-first：沒有 artifact 與 event，就不視為完成。
- Deterministic verdict：AI 不得自行宣告自己的修改正確。
- Bounded autonomy：Agent 必須受角色、scope、gate 與 approval 約束。
- Fail-close：安全、資料與治理異常時拒絕放行。
- 可重現與可回滾：建置、測試與升級流程應可重播並可恢復。
- 經驗可累積：每次 incident 的 diagnosis、修復與驗證結果，應降低下一次同類問題的成本。

目前方向

我正在把這些 repo 收斂成一套：

«以 embedded／OpenWrt／prplOS 為核心，結合長期 log intelligence、事件診斷、Persona-governed SDD／TDD、可重現建置、DUT 確定性驗證與 policy-as-code 的有界自主軟體維護平台。»