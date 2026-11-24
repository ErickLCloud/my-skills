---
name: multi-work
description: 多工/分工工作模式。當使用者說 "multi work"、"multi-work"、"多工模式"、"分工"、"開多個 session"、"拆給多個 worker"，或分工已經在進行中想「中途套用」規則時使用。先逐步訪談（工作目標 → 是否需要分開的 session worker → 如何分工 → reviewer 由各別或主控執行 → token 預算偏好 → 啟動方式），再把規則寫成一份分工計畫文件，最後產出給 pilot（主控 session）開 worker session 用的 prompt，並內建節省 token 的規則，另附任務結束後用的回顧（Retro）prompt。
---

# Multi Work — 分工工作模式

目的：把一個較大的任務，透過「訪談 → 計畫文件 → pilot prompt」三步，變成可由一個 pilot（主控）
協調多個 worker session 執行的工作。**本 skill 只負責規劃與產出文件/prompt，不直接開工。**

## 角色定義
- **Pilot（主控）**：持有計畫文件、開 worker session、分派工作、整合結果、做最終驗收。
- **Worker**：只做被分配的範圍，只改自己擁有的檔案，完成後回報狀態。
- **Reviewer**：檢查 worker 產出是否符合「完成標準」。可以是各別的 reviewer session，或由 pilot 兼任。

## Step 0 — 偵測是否「中途套用」

使用者說 multi work 時，先判斷分工是否**已經在進行**：對話或資料夾裡已有 worker session、`status/`、`tasks/`、已派出去的批次，
或使用者說「已經開了 N 個 worker」。若是，走「中途套用」，不從 Q1 開始：
1. **盤點現況**：用 `list_sessions` 找已存在的 worker（依標題 / cwd / 群組），`get_usage` 看各自 context，列出「已完成 / 進行中 / 尚未開始」的批次。
2. **只問缺的題**：Q1–Q6 中，現況已能回答的直接確認（例：模式已是手動、worker 數已定），只問還缺的（通常是預檢、reviewer 方式、輪次、token 偏好）。
3. **補寫計畫與 decisions**：依現況回填 `<任務名>_plan_v1.md`（§2 標「中途套用」與已完成批次）；把已發生的決定寫進 `decisions.md`；
   已存在的 worker 檔案擁有權、已完成的 task 補進 `tasks/`。
4. **規則只套用在尚未開始的批次**：進行中的 worker 不打斷、不重派；下一批才套用預檢、分批、brief、facts、context 門檻。
5. 其餘（Step 2–4）照常，Retro 時註明哪些批次是中途套用、規則只涵蓋後段。

**不論是否中途套用，都先 `list_sessions` 檢查是否已有 pilot / 同任務、同名的 session**，避免重複 pilot
（實測案例：重複的 pilot 空轉 13 turn，產出全部丟棄）。有就問使用者要沿用哪一個，再往下走。

**環境偵測（Step 0 同時做）**：本 skill 的量測規則（`get_usage`、`list_sessions`、`get_session`、`list_events`、`send_message`）來自 Cowork；
Claude Code CLI 沒有這些工具，改用 `ListAgents` / `SendMessage` / Agent tool。先看手上有哪些工具，把結果寫進計畫 §2「環境」：
- **有 usage 工具**：照 `reference/token-rules.md` 的量測路線（§3b 實測基線、分批查用量、11a 閘門）。
- **沒有 usage 工具**：走**估計路線**——§3b 只填「估計」欄，11a 閘門與用量門檻略過（不要保留一個無法執行的閘門）；
  拆分與否改看：能否真平行、能否換便宜模型、能否減輕 pilot context。Retro 的 token 數字一律標「估計」或只引用 harness 回報值並註明語意。

## Step 1 — 訪談（依序問，不要一次全丟）

**開始訪談前先讀 `reference/interview.md`**：每題的選項、推薦判斷、預檢清單、驗證規則和實測案例都在那裡。
優先用 AskUserQuestion（有選項的題目給選項＋推薦項）；每題答完再問下一題；答案已在對話中出現就直接確認。

- **Q1 工作目標**：交付物、完成標準（查證類要可追溯＋第二來源）、限制、工作位置。
- **Q2 要不要分開的 session worker**：判斷後建議「單純 subagent / multi-work / combine」其一；選單純 subagent 就不寫計畫，skill 到此結束。
- **Q3 如何分工**（Q2 = 需要時）：拆分軸、分工草案表（含模型 / effort）、worker 數、冷啟動基線估算（計畫 §3b）、輪次、同時上限、預檢、檔案擁有權。
- **Q4 Reviewer**：pilot 統一 / 各別 / 混合 / 盲審；是否加 Tester；驗證三層、格式檢查 ≠ 驗證、整合負責人、數字可重現。
- **Q5 Token 預算偏好**：省 / 平衡（建議）/ 品質優先，依答案回頭調整 Q3、Q4。
- **Q6 啟動方式**：subagent 自動開 / 手動開 session / herdr（僅 `HERDR_ENV=1`）；事先講明各模式能力限制。

## Step 2 — 寫入計畫文件

- 路徑：目前 project 的 `output/multi-work/<任務名>_plan_vN.md`
  （沒有 project 就用 root `output/`；版本規則：新文件 `_v1`，修改則 +1，不覆蓋舊版）。
  **執行中範圍、分工或完成標準有變動，就升 `_vN` 並在 decisions.md 記一行**，不要口頭改而計畫還停在舊版。
- 格式：依 `reference/plan-template.md` 填寫，把 Step 1 的所有答案寫進去；§7 依 `reference/token-rules.md` 填。
- 工作資料夾 `output/multi-work/<任務名>/`：
  - `status/<worker>.md`：每個 worker 的狀態檔，pilot 用它追蹤進度（也是手動模式下唯一的溝通管道）。
  - `brief/<worker>.md`：由 pilot 開工前從計畫文件摘出的精簡工作說明（≤30 行），worker 只讀這份。**必須自足**：必要事實直接摘入，
    不指向長的共用規則檔（否則 worker 仍會去讀整份長檔，等於白做 brief）。
    **大檔不整份丟給 worker**：輸入若是長檔（原始資料、長文件、大型 log），pilot 先抽出該 worker 需要的段落，
    寫進 brief 或 `facts.md`；非得讀原檔時，在「只讀參考」註明檔案 + 行號範圍 / 章節，避免 worker 自己探索。
  - `facts.md`：凡是**跨 worker 共用的事實**（例：住宿與日期、去重表、共同假設、共用名詞定義）都要在開工**前**由 pilot 寫成 facts.md；
    沒有跨 worker 事實才可省略。不要等 worker 做完發現衝突才補。
    **每條事實標 `[實測]` 或 `[推論]`**：`[實測]` 附證據（指令 / 端點 / 檔案行號）；`[推論]` 不得寫成事實語氣，brief 引用時要保留標記。
    worker 發現 brief / facts 與實際矛盾時，**寫 blocker 並停手**，不照 brief 硬做（實測案例：pilot 把推論當事實，W1 照做後整合時返工）。
  - `test-plan.md`（啟用 Tester 時）：開工前寫好並經使用者確認的測試計畫（格式見 `reference/plan-template.md` 附錄），開工後凍結。
  - `decisions.md`：已定案的決定紀錄（一行一條：日期｜決定｜原因）。任何新指令（包含使用者直接對 worker 下的）不得悄悄推翻其中的項目；要改就先改這份並註明原因。
  - `tasks/<task>.md`：每個 task 一份（目標、負責 worker、完成標準）。**所有 task 都走這裡**，包含使用者直接對 worker 下的指令——worker 先把它寫成 task 檔再做，並先讀 `decisions.md`。
- 寫完後把計畫摘要（分工表含模型欄 + reviewer 方式 + token 偏好 + 啟動方式）給使用者確認；有修改就改成新版本。

## Step 3 — 產出 pilot prompt

- 依 `reference/prompt-templates.md`（A–D 段）產出：
  1. **Pilot prompt**（一定要有）：讓一個新 session 讀計畫文件、產 brief/facts、開 worker、協調、review、整合。
  2. **Worker prompt**（每個 worker 一段）：subagent 模式時內嵌在 pilot prompt 裡讓 pilot 使用；
     手動模式時單獨列出給使用者貼。
  3. **Reviewer prompt**（只有 Q4 選「各別 reviewer」或「混合」時）；選了「盲審」另產 G 段盲審 prompt；選了「獨立 tester」另產 H 段 tester prompt。
  4. **Retro prompt**（一定要有，見 Step 4）：任務結束後貼回 pilot session 做成果與 token 回顧。
- prompt 必須用**計畫文件的絕對路徑**，讓新 session 不需要本對話的上下文就能開工。
- 把 prompt 存成 `output/multi-work/<任務名>_prompts_vN.md`，同時在回覆中用 code block 列出 pilot prompt，
  方便直接複製。

## Step 4 — 收尾回顧（Retro）

- 產出 pilot prompt 時，**一併產出 Retro prompt**（`reference/prompt-templates.md` 的 D 段），
  存進同一份 `_prompts_vN.md`，並在回覆中提醒使用者：任務跑完後，把它貼回**當初的 pilot session**
  （只有那個 session 看得到 worker 回報與 token 數據）。
- **收尾若有 push 到 GitHub／遠端**：先問使用者範圍（只放最新檔？是否移除遠端舊檔、本機保留？）；範圍由使用者決定，pilot 不自行清庫。
  提醒：若使用者有自動備份工具，被移除的舊檔可能被重新加回，需要時改 `.gitignore`。
- Retro 涵蓋：成果對照完成標準、token 花費表與前 3 大浪費點、分工檢討、目標拆分檢討、
  改良版分工表、對本 skill 的改進建議。報告寫成 `<工作資料夾>/retro_vN.md`。
- Token 數字拿不到的標「估計」。手動開的 worker session 不在 pilot 內，建議使用者在各 worker
  跑 `explain-usage` 後貼給 pilot。
- 使用者可把 Retro 的「對 skill 的改進建議」帶回來，據此迭代 skill 下一版。

## Token 節省規則與 Usage 量測

寫計畫 §7、產 prompt 前先讀 `reference/token-rules.md`：模型對照、跳過 workspace 載入、brief 取代整份計畫、分批啟動、
一個 task 一個新 session、冷啟動基線閘門、Windows 編碼、未授權動作先問，以及 `get_usage` 等量測方法。

## 規則
- 訪談完成並經使用者確認前，不寫計畫文件、不開 session。
- 本 skill 不自動啟動 pilot；由使用者把 pilot prompt 貼到新 session（或明確要求現在就開）。
- 任何送出、發佈、刪除的動作，pilot 與 worker 都要先跟使用者確認（沿用 workspace Safety 規則）。
- 單一事實只寫一處：分工規則寫在計畫文件，prompt 只引用計畫文件路徑，不重抄規則內容。
