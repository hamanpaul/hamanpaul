# paulsha-patchmud

**PatchMUD**：成本優先的純文字回合制 coding-agent 評測框架——以軟體 issue 為關卡、程式代理模型為玩家、patch 為攻擊動作的 MUD 式評測引擎。

## 定位

- 量測閉環（laboratory），不是生產閉環：frozen fixture、deterministic 評分、可位元重播。
- 對 `paulsha-cortex` / `paulsha-hippo` 零 runtime 依賴；評測輸出以檔案契約供下游（如 model roster/routing）使用。
- 排名資料流零 LLM 裁判：所有關鍵結果由 artifact、測試、版本差異與可稽核事件日誌決定。
- 三維角色能力：經濟（Economy 55%）、火力（Power 25%）、控場（Control 20%），另設不重複計分的 token-efficiency 稽核指標。

研究設計、implementation spec 與實作計劃見 `docs/`：

- 研究報告：`docs/PatchMUD_research_report_zh-TW_v0.2.md`
- Spec（v1.1，經 codex gpt-5.6-sol 對抗審查）：`docs/superpowers/specs/2026-07-16-patchmud-mvp-design.md`
- 實作計劃（21 tasks）：`docs/superpowers/plans/2026-07-16-patchmud-mvp.md`
- 跨 provider adapter 設計（codex / agy OAuth headless）：`docs/superpowers/specs/2026-08-11-multi-provider-adapters-design.md`
- 玩家與旁觀者指南：[`docs/user-manual.md`](docs/user-manual.md)

## Install

```bash
python -m pip install -e ".[test]"
```

執行 candidate code 的隔離層需要 [bubblewrap](https://github.com/containers/bubblewrap)（`bwrap`）；無 namespace 能力時 ranked / pilot run 會 fail-closed 拒絕啟動，dev run 以 degraded 模式執行。

## Usage

MVP CLI（依實作計劃逐步落地）：

```bash
patchmud play <關卡>                            # 人類親自玩（開場有白話規則；見 docs/how-to-play.md）
patchmud run <關卡> --model sonnet --live        # 看模型即時玩（--delay N 放慢節奏）
patchmud versus <關卡> --models sonnet,haiku     # 多模型並排對戰 + 記分板
patchmud watch <run_dir> [--turn N]            # 離線觀戰：逐回合 zh-TW 戰報
patchmud validate-deck decks/pilot-v1          # deck 契約與 fixture 驗證
patchmud author-encounter <source.yaml> --into <deck_dir>   # 出題：closed bug → 凍結關卡（含品質閘）
patchmud score-diff --encounter <dir> --diff <file>   # 離線評分（milestone A）
patchmud pilot --deck pilot-v1 --models models.yaml --seed 42   # forced loadout 矩陣（跑 benchmark）
patchmud replay <run_dir> [--l2]               # 兩級重播驗證
patchmud report --runs "runs/*"                # 多榜研究報告（模型比較）
```

- 關卡可只打名字（自動找 `decks/pilot-v1/<名字>`），`--loadout` 預設 `P0T0R0`（SOLO）。最短：`patchmud play input-validation-v1`。
- 模型別名（三家共用同一組短名）：

  | Provider | 別名 | 展開後 | 認證 |
  |---|---|---|---|
  | Anthropic | `sonnet` / `haiku` / `opus` / `fable` | `anthropic:claude-*` | API key 或 OAuth bearer；缺憑證且有 `claude` CLI 時自動改走 CLI |
  | OpenAI | `spark` / `luna` / `terra` / `sol` | `codex:gpt-5.3-codex-spark` / `gpt-5.6-luna` / `gpt-5.6-terra` / `gpt-5.6-sol` | `codex login` 的 OAuth 登入態（`~/.codex/auth.json`） |
  | Google | `flash` / `pro` | `agy:gemini-3.6-flash` / `agy:gemini-3.1-pro` | `agy` CLI 登入態（`~/.antigravitycli`） |

  跨家對戰：`patchmud versus input-validation-v1 --models sonnet,sol,flash`。
- Anthropic 認證兩選一：`export ANTHROPIC_API_KEY=…`，**或** 用 Claude 帳號 OAuth——`ant auth login` 後 `set -a; eval "$(ant auth print-credentials --env)"; set +a`（設定 `ANTHROPIC_AUTH_TOKEN`，不必管 API key）。codex 與 agy 別名走各自 CLI 的登入態，不需要任何 API key 環境變數。
- CLI-based adapter（`claude` / `codex` / `agy`）一律以**純補全模式**執行：工具寫入能力全關、在臨時空目錄執行，執行 candidate code 的唯一 seam 仍是 `IsolationRunner`；`codex` / `agy` 的 reasoning effort 固定 `high`，不隨使用者的 CLI 設定漂移。代價是 CLI 自帶的 system prompt 與 skill 目錄會產生每回合固定的 input token overhead（實測 codex ≈17k、agy ≈18k），跨家比較 economy 維度時需知悉。
- 出題（把已解決的 closed bug 結構化凍結成新關卡、含 bug/fix 品質閘）見 [`docs/authoring/README.md`](docs/authoring/README.md)。

## Version

版本記錄於 `VERSION`，變更紀錄見 [CHANGELOG.md](CHANGELOG.md)；版號規則遵循 hamanpaul project policy v1.0.17（`<MAJOR>.<MINOR>.<PATCH>[-fix.N]`，flat profile）。

## 開發

- 分支：`feature/<slug>` 或 `wt/<feature>/<subtask>`；禁止直接 commit `main`。
- 每個 code PR 同步更新 `CHANGELOG.md [Unreleased]`，並通過 `python3 -m policy_check --repo .` 與 `python3 -m pytest -q`。
- 本 repo 受 hamanpaul project policy v1.0.17 管轄（`tier: shareable`），詳見 `CLAUDE.md`。
