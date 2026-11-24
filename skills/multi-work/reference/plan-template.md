# Multi Work 計畫：<任務名>  (v<N>)

> 本文件是本次分工的唯一規則來源（single source of truth）。Pilot、worker、reviewer 都以此為準。
> 修改規則 → 產生新版本 `_v<N+1>`，並通知 pilot。

## 0. 預檢清單（pilot 開 worker 前逐項確認，沒過不開工；外部工具項目要由 pilot 親自實測，不是只確認已登入）
- [ ] <外部工具/網站已登入：…>
- [ ] <檔案未被鎖住 / 未被其他程式開啟：…>
- [ ] <worker 權限模式已設定：…>
- [ ] <手動模式：worker session 皆為空白（list_events 無多餘 turn），第一則訊息為待命訊息、未打招呼>
- [ ] <無重複 pilot / 同任務 session（list_sessions 已檢查）>
- [ ] <herdr 模式：HERDR_ENV=1 已確認；herdr agent list 無同名 agent；worker 名稱符合 [a-z][a-z0-9_-]{0,31}>
- [ ] <pilot cwd = 預期 repo 根目錄（git rev-parse --show-toplevel 已核對；開 worktree 前必做）>
- [ ] <facts.md 每條已標 [實測]/[推論]，[實測] 附證據>
- [ ] <其他前置條件：…>

## 1. 工作目標
- 目標：
- 最終交付物：
- 完成標準（逐條可檢查）：
  - [ ]
- 限制 / 不能動的東西：
- 工作位置（project / repo / 路徑）：

## 2. 執行模式
- 環境：<有 usage 工具（get_usage…）→ 量測路線 / 無 → 估計路線（§3b 只填估計、略過 11a 閘門與用量門檻）>
- Q2 建議與使用者決定：<單純 subagent（不寫本文件）/ multi-work / combine — 走 multi-work 的部分：…；走單純 subagent 的一次性子任務：…>
- 是否分工：<是 — 平行 N 個 worker / 否 — 單一 session>
- 啟動方式：<pilot 用 subagent（使用者看不到 subagent 畫面）/ 使用者手動開 session（可見、可中途介入）/ pilot 用 herdr 開 pane（可見、可介入、自動派工；需 HERDR_ENV=1）>
- 程式碼隔離：<git worktree / 不需要>
- 同時最多 worker 數：<3–4>；超過的分批啟動，每批前查用量，剩餘 <40%> 以下不開新 worker
- 輪次：<單輪 / 多輪：R1 產出 → R2 修訂 → R3 查證；預設每輪新 session，輪次寫進 tasks/R<n>-…>
- 套用方式：<全新 / 中途套用（已完成批次：… ；規則只套用於之後批次）>
- 每個 worker 的 task 數：<1（預設）/ 最多 2>
- 使用者覆寫：<無 / 使用者堅持拆分（比值 <2）：估計額外成本 __k（worker 數 × 基線），原因：…>

## 3. 分工表

| Worker | 負責範圍 | 擁有的檔案/資料夾 | 輸入 | 產出 | 完成標準 | 依賴 | 模型 / effort |
|---|---|---|---|---|---|---|---|
| W1 | | | | | | — | |
| W2 | | | | | | | |

- 共用檔案（只有 pilot 可以改）：
- 執行順序：<全部平行 / W2 等 W1 完成…>

## 3b. 起始成本表（開工前填；首個 worker 開局後補「實測基線」）

| Worker | 預估 Messages | 預估基線 | 比值 (Messages÷基線) | 決定 (保留 / 合併 / 改 subagent) | 實測基線 |
|---|---|---|---|---|---|
| W1 | | ~75k | | | |

- 比值 < 1–2 的 worker 預設合併或改 subagent；保留的要寫理由（例：需使用者互動）。
- 無 usage 工具時：「預估」欄標「估計」，「實測基線」留空；拆分理由改填 真平行 / 可用便宜模型 / 減輕 pilot context。
- 啟動方式補充：<預設 / 精簡 cwd（待實測）>；首個 worker 實測基線超過預估 20% 以上，先停後續批次（見 SKILL 規則 11a）。

## 4. Review
- 方式：<pilot 統一 / 各別 reviewer / 混合>
- Tester：<不用 / pilot 自己測 / 獨立 session — 資訊量：<黑箱 / 灰箱>；模型：<使用者選的>；工具預檢：<瀏覽器 / Chrome / herdr pane 已實測>；測試計畫：見 `test-plan.md`（開工前定稿並凍結）；修後最多再測 <1–2> 輪>
- 盲審：<不用 / 用 — 模型：<使用者選的>；審查對象：<產出路徑>；評分依據＝§1 完成標準（開工前已定稿）；最多 <1–2> 輪；cwd：<workspace 外的中性資料夾>>
- 檢查項目：依 §1 完成標準 + §3 每個 worker 的完成標準；<是否跑測試：指令>
- 驗證三層：worker 自測 → 最小依賴 smoke test（<指令>）→ pilot 自寫的 seam/contract test（<指令>）
- 判斷型產出（規則 / 對照 / 評分）的證據步驟：<回測 / 抽樣：指令與通過門檻>
- worker 回報的數字必須附產生它的指令，pilot 重跑後才採信
- 退回規則：同一個 worker 被退回 <2> 次仍未通過 → pilot 上報使用者

## 5. 溝通與狀態
- 狀態檔：`<abs path>/output/multi-work/<任務名>/status/<worker>.md`
- Brief：`<abs path>/output/multi-work/<任務名>/brief/<worker>.md`（pilot 開工前產生，≤30 行）
- 共用調查：`<abs path>/output/multi-work/<任務名>/facts.md`（<需要 / 不需要>）
- 決策紀錄：`<abs path>/output/multi-work/<任務名>/decisions.md`（日期｜決定｜原因；不得被新指令悄悄推翻）
- Task 檔：`<abs path>/output/multi-work/<任務名>/tasks/<task>.md`（所有 task 都走這裡，含使用者直接下的指令）
- 狀態格式：
  ```
  status: todo | doing | blocked | review | done
  updated: <yyyy-mm-dd hh:mm>
  done: <完成了什麼>
  next: <下一步>
  blocker: <卡在哪 / 需要誰>
  outputs: <產出檔案路徑>
  context: <完成前呼叫 get_usage(self) 的 tokensUsed、Messages tokens；超過 ~200k 由 pilot 換新 session>
  cumulative: <完成當下跑 explain-usage 的原始數字：input / output / cache read / cache write；不自行加權、不事後補>
  ```
- 遇到超出範圍的需求：worker 不自己做，寫進狀態檔 blocker，由 pilot 決定。

## 6. 整合與收尾（pilot）
- [ ] 所有 worker status = done 且 review 通過
- [ ] 整合產出，對照 §1 完成標準做最終驗收
- [ ] 回報使用者：完成項目、未完成項目、風險
- [ ] 更新 project tracking（journal / progress）
- [ ] 建議使用者用 `explain-usage` 檢視 token 分佈

## 7. Token 預算
- 偏好：<省 / 平衡 / 品質優先>
- 起點用量（pilot 開工前記錄，`get_usage` plan.windows）：5 小時 <__%>、每週 <__%>；結束時再記一次，差值寫進 retro
- 冷啟動基線：<pilot 用 get_usage 自己的 tokensUsed − Messages 估一次，每個 session 約 __k>
- 使用者覆寫的額外成本：<無 / __k（見 §2）>
- 規則：worker 跳過 workspace context 載入（須在 session 第一則訊息就帶上）、只讀 brief（+ facts）；回報 ≤10 行；
  退回用 SendMessage 交回原 worker；pilot 不輪詢；review 先用測試/lint/build，看 diff + 摘要。

## 附：Brief 格式（每個 worker 一份）
```
# Brief: <Wn> — <負責範圍一句話>
規則來源：<PLAN_ABS_PATH>（有疑問才查，平常不用讀）
必要事實（自足：直接摘入，不指向長檔；共用事實引用 facts.md 的條目，保留 [實測]/[推論] 標記；與實際矛盾 → 寫 blocker 停手）：
編碼規則：含非 ASCII 的檔案只用 Edit/Write 寫，不用 PowerShell / heredoc
目標（一句）：
可修改：<檔案列表>      只讀參考：<檔案列表 / facts.md>
輸入：            產出：
完成標準：
- [ ]
依賴：<等 Wx done / 無>
狀態檔：<STATUS_DIR_ABS_PATH>/<Wn>.md
```

## 附：測試計畫格式（`test-plan.md`；啟用 Tester 時，開工前由規劃者擬定、使用者確認後凍結）
```
# 測試計畫：<任務名>
資訊量：<黑箱 / 灰箱>      被測對象：<啟動方式 / URL / 指令 / 路徑>      測試資料：<位置；不得使用正式資料>
環境：<埠號、帳號、前置設定、清理方式>
情境（開工前定稿；修改須記入 decisions.md）：
| ID | 前置條件 | 操作步驟 | 預期結果 | 嚴重度（阻擋/重要/次要） |
|---|---|---|---|---|
| T1 | | | | |
涵蓋檢查：[ ] 主要流程  [ ] 邊界與錯誤輸入  [ ] UI：版面 / 狀態 / console 錯誤  [ ] 重新整理或重跑後的狀態
通過門檻：<例：阻擋級 0 個、重要級 ≤ N 個>
```
