# multi-work — Step 1 訪談細則

SKILL.md 的 Step 1 只列題目；這份是每一題的完整選項、判斷規則與實測案例。依序問，不要一次全丟。

優先用 AskUserQuestion 工具（有選項的題目給選項 + 推薦項）；開放題直接用文字問。
每題答完再問下一題；答案已在對話中出現就不要重問，直接確認。

**Q1. 工作目標**（開放題）
- 要完成什麼？最終交付物是什麼？
- 完成標準（怎樣算做完）？有沒有期限或限制（不能動的檔案、技術棧、預算）？
  **查證／資料／判斷類任務的完成標準必須含「可追溯」與「第二來源」**：每個數字或結論附來源與重現指令；關鍵數字至少有第二個獨立來源，找不到就明寫「無第二來源」。
  （實測：盲審第 1 輪 FAIL 的主因就是缺第二來源與算式不可重現。）
- 工作在哪個 project / repo / 資料夾？

**Q2. 是否需要各別分開的 session worker？**（選項題）
- 「需要 — 平行分工」：任務可拆成彼此獨立的部分，平行做比較快
- 「不需要 — 單一 session 依序做」：任務耦合高、規模小，拆開反而增加協調成本
- 判斷建議（附在題目說明中）：可拆成 ≥2 塊、各塊檔案不重疊、各自可獨立驗證 → 建議分工；否則建議單一 session。
- 若選「不需要」→ 跳過 Q3，Q4 只問 reviewer，計畫文件仍要寫（單一 worker = pilot 自己）。
- **判斷後給三種建議之一（附理由），由使用者決定**：
  - **單純 subagent**：獨立調查 / 搜尋 / 讀大量檔案、少於約 10 分鐘、不需共用事實、不需使用者中途介入 → 直接告知，**不寫計畫文件，skill 到此結束**。
  - **multi-work**：多交付物共用事實、需要審查或測試、要使用者看得到、多輪 → 走完整流程。
  - **combine**：主體需要結構，但其中有一次性的小任務 → multi-work 當骨幹（計畫、檔案擁有權、review、tester 由 pilot 管），
    一次性子任務（搜尋、查資料、讀大檔）直接用單純 subagent，**不需 task 檔 / brief / status**；
    其結論由 pilot 寫進 `facts.md` 並標 `[實測]` / `[推論]`，不直接當事實。計畫 §2 記錄哪些部分走哪種，Retro 才能分開檢討。

**Q3. 如何分工**（Q2 = 需要時才問）
1. 分工方式（選項題）：
   - 依模組/檔案（例：driver / test / doc 各一個 worker）
   - 依階段（例：調查 → 實作 → 測試，有先後依賴）
   - 依角色（例：寫 code / 寫測試 / 寫文件）
   - 自訂
   - **拆分軸提示**：產出類工作通常依交付物結構拆（例：依天、依模組）；查證 / 審查類工作改依**資料類型**拆
     （例：一個 verifier 查全部交通、一個查全部景點店家），這樣外部工具只需設定一次、查詢方式共用。兩種軸可在同一任務的不同輪次混用。
2. 先由你（Claude）根據 Q1 提出一個**分工草案表**，讓使用者修改確認：

   | Worker | 負責範圍 | 擁有的檔案/資料夾 | 輸入 | 產出 | 完成標準 | 依賴 | 模型 / effort |
   |---|---|---|---|---|---|---|---|

   「模型 / effort」欄由你先依工作類型填建議值（見 `token-rules.md` 的模型對照），使用者可改。

3. 確認：
   - worker 數量（建議 2–4；超過 5 協調成本通常大於收益；每多一個 worker 就多一次冷啟動成本）
   - **冷啟動基線前置估算**：每個 session 約 75k 起跳（實測 71–79k；system tools ~36k、MCP tools ~22k、skills ~7k）。
     對每個 worker 估「預期實際工作量」（Messages），若不到基線的 1–2 倍，建議合併 worker；估不準就拿 pilot 自己 `get_usage` 的基線當準。
     **結果填進計畫 §3b 起始成本表**（worker｜預估 Messages｜基線｜比值｜決定：保留 / 合併 / 改 subagent），使用者確認後才開工。
     實測偏差：Stock 專案兩次的預估都比實際高 2–3 倍（預估 150–200k、實測 72–75k），且依比值 ≥2 規則其實都不該拆；填預估時寧可保守，別灌水。
     沒有 usage 工具時，預估欄標「估計」，決定欄依「環境偵測」的判準
   - **「要不要獨立 session」先看互動需求**：worker 中途不需要使用者介入、產出可寫成檔案 → 優先 subagent（Q6）；
     只有需要使用者中途互動、或工作量遠大於基線的 worker 才值得開獨立 session
   - **使用者堅持拆分時**：若比值 < 2 而使用者仍選拆，照做但把「使用者覆寫 + 估計額外成本（worker 數 × 基線）」
     寫進計畫 §2 與 §7，retro 才能區分「規劃失誤」與「使用者選擇」
   - **輪次**：任務是否分多輪（產出 → 修訂 → 查證）？多輪的預設是**每輪新 session**，並把輪次寫成 `tasks/R<n>-<名稱>.md`；
     若使用者堅持沿用同一批 session，則必須設 context 門檻（見 Token 規則 4a），到了就換新 session
   - **同時最多幾個 worker 在跑**（建議 3–4；worker 比這多就分批，見 Step 3 分批啟動）
   - **每個 worker 做幾個 task**（建議一個 task 一個新 session，最多連做 2 個；上下文會累積）
   - **開工前預檢（preflight）**：列出開工前必須成立的條件，例如外部工具/網站是否已登入、檔案有沒有被別的程式鎖住（如 Excel 開著）、worker 的權限模式、必要的資料夾/權限。
     **外部工具要「實測」**：凡是 worker 會用到的外部工具或網站（Gemini、Google Maps 設定出發時間、需登入的網站…），pilot 開 worker 前要自己實際跑一次
     worker 會做的那個操作，不是只確認「已登入」。失敗（被權限分類器擋、無回應、功能不存在）就先改計畫：換來源、集中給單一 worker、
     或預先標「未驗證」，不要讓 N 個 worker 各自撞牆。沒過預檢不開工
   - **cwd / repo 根目錄檢查**：開任何 worktree subagent 前，pilot 先確認自己的 cwd 就是預期的 repo 根目錄
     （`git rev-parse --show-toplevel` 對照計畫 §1「工作位置」）。cwd 落在巢狀子 repo 時 worktree 會建到錯的 repo（實測案例）；不符就先切換或改用絕對路徑指定
   - **判斷類產出要有證據步驟**：worker 產出規則、對照表、評分等「判斷型」內容時，完成標準必須含可執行的證據步驟
     （例：用歷史資料回測、抽樣對答案），不能只寫「使用者審閱」。實測案例：19 條規則在 review 回測後被刪掉 8 條
   - **herdr 新 cwd 的「信任此資料夾」提示**：worker／reviewer／tester 使用新的 cwd（尤其是中性資料夾）時，Claude Code 會先問是否信任，
     `agent start` 會停在 agent_not_ready／blocked。預檢要列這一項：請使用者先在該 pane 接受一次；pilot 不得代為接受。
   - **手動模式的 worker session 必須是空白的**：workspace 的 CLAUDE.md 若規定「每個 session 開頭載入 context」，
     第一則訊息不管是什麼（包括一句「Hi」）都會觸發載入，之後 worker prompt 裡的「跳過載入」就來不及了（實測：W1/W2 各多 4 turn）。
     所以：①請使用者開好 session 後，**第一則訊息只貼 `reference/prompt-templates.md` 的 E 段待命訊息**，不要打招呼；
     ②預檢用 `list_events` 確認每個 worker session 沒有多餘的 turn（有就換新的）；
     ③建議使用者在根 CLAUDE.md 加「`[WORKER]` 開頭則跳過載入」的例外條款（條款文字由本 skill 協助擬，不自行修改使用者的 CLAUDE.md）
   - **瀏覽器類 worker**（共用使用者 Chrome）：同時上限 ≤3，各自開新分頁，避免互相搶同一個分頁
   - 是否有多個 worker 要先理解同一批資料 → 有的話由 pilot 先做一次共用調查，寫成 `facts.md`
   - **檔案擁有權不可重疊**；共用檔案只由 pilot 修改
   - 執行順序：全部平行 / 部分有依賴（標出誰要等誰）
   - 程式碼類工作是否用 git worktree 隔離（建議：是）

**Q4. Reviewer 要各別或由主控執行？**（選項題）
- 「由主控 (pilot) 統一 review」：worker 少、範圍小時建議；省 session
- 「各別 reviewer session」：每個 worker 配一個獨立 reviewer，品質要求高 / 範圍大時建議
- 「混合」：worker 自我檢查 + pilot 最終整合 review
- 「盲審 reviewer」（可與上面任一項疊加）：一個**完全沒有專案背景**的獨立 reviewer，只拿完成標準 + 產出 + 測試指令，不給 facts.md / brief / worker 推理，
  也不說誰寫的。用來擋 pilot 與 worker 共同的先入為主（例：pilot 把推論當事實，有背景的 reviewer 會一起繼承）。
  - 適合：判斷型內容（規則 / 評分 / 對照）、給人讀的最終報告、查證類任務；不適合：靠專案知識才能判斷的內容、程式碼接縫（用 pilot 自寫的 seam test）
  - 風險要告訴使用者：不懂專案特例會有誤報（由 pilot 裁決）、多一次冷啟動 + 高階模型成本、同模型家族仍有共同盲點
  - **模型由使用者在訪談時選**（給選項 + 推薦：可用的最高階模型；省 token 時可降一級，並說明盲審品質可能下降），寫進計畫 §4
  - **完成標準必須在開工前定稿**（寫進計畫 §1），盲審的評分依據不得看過產出後才補
  - reviewer 要**自己查證**（重跑數字、查來源），每條主張標「已驗證 / 無法驗證」，不照單全收；只產出審查結果，不改檔案
  - pilot 逐條裁決：採納 / 駁回（附理由）/ 交使用者決定；盲審最多 1–2 輪，超過上報使用者
  - 啟動：herdr 模式用中性 cwd（workspace 之外，避免載入專案 CLAUDE.md）+ `-- --model <使用者選的>`；其他模式依 Q6。prompt 見 `reference/prompt-templates.md` G 段
- **Tester（測試員）**：交付物有 UI，或有可執行功能（CLI / API / 腳本 / 頁面 / 終端機 UI）時由 Claude 自動偵測並確認，推薦啟用。
  Reviewer 是「讀產出、對照完成標準」；Tester 是「真的把東西跑起來、像使用者一樣操作」。兩者不合併，可同時用。
  - **使用者選項**：①不用 ②pilot 自己測（簡單腳本）③獨立 tester session（有 UI 或面向最終使用者的功能時推薦）
  - **資訊量由使用者選**：黑箱（預設：只拿測試計畫、啟動方式、測試資料，不看原始碼）/ 灰箱（可看規格與 API 文件，不看實作）
  - **模型由使用者選**（給推薦；機械式點選流程可降一級，UI 判斷建議高階）
  - **測試計畫在開工前由規劃者寫好（`test-plan.md`）**：Step 2 由規劃階段（本 skill 的訪談後、pilot 開 worker 前）擬定情境，使用者確認後凍結；
    開工後要改就改 `decisions.md` 並註明原因，不可為了配合產出而調整。每個情境：編號｜前置條件｜操作步驟｜預期結果｜嚴重度（阻擋 / 重要 / 次要）。
    須涵蓋：主要流程、邊界與錯誤輸入、UI 類另含版面 / 狀態 / console 錯誤。
  - **只回報、不修**：每個問題附步驟、預期、實際、證據（截圖 / log 路徑）、嚴重度；pilot 分類（真 bug 交回原 worker / 駁回附理由 / 交使用者決定），修後最多再測 1–2 輪
  - **環境安全**：用測試資料，不碰正式資料；刪除 / 送出 / 付款等動作仍先問使用者
  - **預檢**：UI 測試依賴的工具（瀏覽器、Chrome 工具、herdr pane）由 pilot 先實測能開頁面 / 操作 / 截圖，不是只確認工具存在
  - UI 類：網頁用瀏覽器工具；終端機 UI 用 herdr pane（`pane send-keys` / `agent read` / `pane read`）。啟動與 prompt 見 `reference/prompt-templates.md` H 段
- 同時確認 review 標準：依「完成標準」逐條檢查？要不要跑測試？退回幾次後上報使用者？
- 提醒：「各別 reviewer」session 數量加倍，建議只用在高風險 worker；能用測試/lint/build 判定的先用工具判定。
- **驗證分三層**（pilot review 時都要有）：①worker 自測；②**最小依賴的 smoke test**（production 路徑能不能跑起來）；
  ③**seam / contract test**：由 pilot 自己寫，專測 worker 之間的介面（實測：pilot 親跑端到端抓到過接縫 bug）。
- **格式檢查 ≠ 驗證**：worker 產出若要交給別人整合（JSON / CSV / 介面），開工前由 pilot 在 `facts.md` 定好欄位格式，
  並寫好**凍結的格式檢查腳本**；worker 只能執行、不能改，當作交件入口條件。它只擋格式（缺欄位、型別錯），**不算驗證**。
  驗證（語意、算式、整合、UI）一律由「寫的人以外的角色」做：pilot 的 seam test、獨立 tester、盲審。
  worker 與整合 worker 不驗收自己的產出（實測：樣本數與倍率算錯能通過格式檢查，是 pilot 重算與盲審才抓到）。
- **整合要有負責人**：計畫分工表必須標明誰做整合（host / build / 合併）。預估 pilot 親手整合量超過一個 worker 的工作量時，開整合 worker
  （先用格式假資料平行開工）；量小就由 pilot 做，並在 §3b 加「pilot 整合」一列（標估計）。
  review / tester 的發現，凡需重抓資料或重算的退回原 worker（最後一輪 review 結束前不關其 pane）；單檔幾行的小修由 pilot 做。
- **數字要可重現**：worker 回報的任何計數（筆數、通過數）必須附上產生它的指令；pilot 重跑一次再採信
  （實測：worker 自報 20/5，實際 19/4）。

**Q5. Token 預算偏好**（選項題）
- 「省」：worker ≤3、能用 Haiku 的都用 Haiku、pilot 統一 review、只看 diff + 摘要
- 「平衡」（建議）：依工作類型對照選模型、高風險 worker 才配 reviewer
- 「品質優先」：實作用 Sonnet 以上、整合/設計用 Opus、可各別 reviewer
- 依答案回頭調整 Q3 的 worker 數量與同時上限與「模型 / effort」欄、Q4 的 reviewer 方式，並把調整結果給使用者確認。

**Q6. 啟動方式**（選項題）
- 「Pilot 用 subagent 自動開」：pilot 在同一個 session 用 Agent tool 背景啟動 worker（程式碼用 `isolation: "worktree"`）
- 「我手動開 session」：使用者自己開好空白 session；**pilot 用 `list_sessions` 找到它們，再用 `send_message` 直接派工與退回**
  （已在實際任務驗證可行，pilot 不必再讓使用者逐一複製貼上）；找不到或不確定是哪個 session 就請使用者確認。
  worker prompt 仍單獨列出，供使用者需要時自己貼。pilot 透過狀態檔協調，`send_message` 回「queued」代表對方還在忙，不是失敗
- 「Pilot 用 herdr 自動開」（pilot 本身跑在 herdr pane 內時才可選）：pilot 用 herdr CLI 在旁邊切 pane、啟動獨立的 Claude session、派工、等狀態、讀輸出。
  使用者在 herdr 畫面看得到每個 worker、能中途介入；pilot 又能自動開與退回。流程與指令見 `reference/prompt-templates.md` F 段（已實測）。
  - 前提：`test "$HERDR_ENV" = 1`；不成立就不要提供這個選項（也不要從 herdr 外部控制別人的 session）
  - 使用者必須明確要求用 herdr 才執行；不因「可以平行」就自己開
  - 模型用 `agent start … -- --model <haiku|sonnet|opus>` 指定（已實測 haiku 生效）；effort 參數尚未驗證，未驗證前請使用者在 pane 內用 `/effort` 調
  - worker 的 cwd 預設繼承 pilot 當下目錄，務必用 `--cwd` 明確指定（並先做 cwd / repo 根目錄檢查）
  - 用完的 pane 由 pilot 用 `pane close` 關掉（只關自己開的）
- **能力限制要事先講明，不要先承諾**：subagent 在背景執行，**使用者在畫面上看不到它們**（沒有獨立 pane）；
  使用者若要「看得到、能中途介入的獨立 session」，只能選手動模式。pilot 驗證過之前，不得向使用者承諾「可以看到 subagent」
  （實測案例：承諾後才發現做不到，與使用者期待「真正獨立 session」不符）。把這點寫在 Q6 選項說明裡。
- 依使用者環境選擇；不確定時建議 subagent 模式。若 `HERDR_ENV=1` 且使用者想看得到 worker，建議 herdr 模式。
  herdr 模式下 usage 量測仍屬「估計路線」（除非另有 `get_usage`）；`agent list` 的狀態（idle / working / blocked / done）可取代輪詢狀態檔。
- **精簡 cwd（選用，待實測）**：workspace 的 CLAUDE.md 是依 cwd 往上層逐層載入，worker 的 cwd 設在子專案**不會**避開根目錄那份。
  若根 CLAUDE.md 很長又規定開局載入流程，可讓手動 worker 以不在 workspace 底下的精簡資料夾當 cwd，檔案一律用絕對路徑存取
  （可能多出資料夾授權提示）。第一次採用時，用 `get_usage` 比較前後基線，把結果記進 retro；沒量到之前不要當成已驗證的省法。

