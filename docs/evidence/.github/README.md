# .github

`hamanpaul/.github` 提供 `hamanpaul/*` repositories 的帳號層級 community health defaults。
這個 repo 只放 GitHub 支援的社群預設檔案，不承載 workflow templates、policy engine 邏輯或其他下游自動化責任。

## Install

不需要額外安裝。當 `hamanpaul` 底下的 repository 沒有提供自己的 `CONTRIBUTING.md`、`SECURITY.md` 或預設 PR template 時，GitHub 會自動從這個 public `.github` repository 讀取支援的預設內容。

## Usage

請把這個 repository 視為帳號層級社群文件的 single source of truth：

- `.github/pull_request_template.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

若下游 repo 需要 workflow、policy rule 或 bootstrap 邏輯，請改到 `hamanpaul/paulsha-conventions` 或 `hamanpaul/new-project-template` 維護，不要把那些責任放進這個 repo。

## Version

`VERSION` 記錄這組 account defaults 的版本；調整預設內容時，請同步更新 `CHANGELOG.md` 與 `VERSION`。
