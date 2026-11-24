# multi-work — Token 節省規則與 Usage 量測

## Token 節省規則（寫進計畫文件 §7 與 prompt）
1. **模型對照**（subagent 模式用 Agent tool 的 `model` 參數；手動模式由使用者在 app 選）：
   - Haiku：搜尋、整理/格式化、跑測試、機械式修改
   - Sonnet：一般實作、撰寫文件
   - Opus：設計、困難 debug、最終整合（通常是 pilot）
   - 只讀不改的調查型 worker 優先用 `Explore` subagent（讀片段不讀整檔）。
2. **跳過 workspace 載入**：worker prompt 明寫「不要執行 CLAUDE.md 的 context 載入流程
   （_context、methodology index），只讀指定檔案」。**這句只有放在 session 的「第一則訊息」才有效**——
   載入是由 CLAUDE.md 在第一個 turn 觸發的，晚一則就白付了。手動模式用 E 段待命訊息當第一則；subagent 模式 prompt 本身就是第一則。
   worker / reviewer prompt 一律以 `[WORKER]` 開頭，配合根 CLAUDE.md 的例外條款（若使用者有加）。
3. **Brief 取代整份計畫**：worker 只讀 `brief/<Wn>.md`（自足、≤30 行）；計畫文件仍是唯一規則來源，brief 是它的摘錄。
4. **分批啟動**：同時跑的 worker 不超過 Q3 設的上限；每批啟動前先用 `get_usage`（見下方「Usage 量測」）查帳號 5 小時 / 每週用量，
   剩餘不足 40% 就不開新 worker，改為排隊並告知使用者。避免一次全開、同時撞用量上限而白付冷啟動成本。
4a. **一個 task 一個新 session**：worker 完成一個 task 就結束；不要讓舊 worker 累積上下文接下一個 task。
   worker 完成時在狀態檔寫 `context: <上下文大小或訊息數>`，pilot 超過門檻（約 200k）就換新 session。
   **多輪任務**（產出 → 修訂 → 查證）預設**每輪新 session**：長 session 每輪都要重讀系統指令與工具清單，實測占累計用量 38–51%，
   輪數越多越浪費（83 輪的 worker 累計約 1.7M）。輪次寫進 `tasks/R<n>-…`；要沿用舊 session 就必須守 context 門檻。
4b. **預檢先於開工**：開 worker 前跑完計畫 §0 預檢清單；失敗的項目（如未登入）先請使用者處理，不要讓 worker 在條件不成立時產出再丟棄。
   外部工具項目由 pilot **親自實測**（見 `interview.md` Q3 預檢），失敗先改計畫。
4c. **共用調查只做一次**：跨 worker 共用的事實由 pilot 先寫成 `facts.md`（見 SKILL.md Step 2）。
5. **退回沿用原 worker**：review 未過時 pilot 用 `SendMessage` 把意見交回同一個 worker，不開新的。
6. **回報要短**：worker 回報 ≤10 行，只給路徑與結論，不貼檔案內容或完整 log。數字類結論附產生它的指令（見 `interview.md` Q4「數字要可重現」）。
7. **不輪詢**：背景 subagent 完成會自動通知 pilot，不反覆讀狀態檔。
8. **Review 便宜優先**：先用測試/lint/build；pilot 看 diff + 摘要，不讀全部產出。
9. **共用前綴**：多個 worker prompt 共用的規則放前面、各自不同的放後面（有機會吃到 prompt cache，不保證）。
10. **量測**：用 `get_usage` 取真實數字（見下方「Usage 量測」），收尾時再建議使用者用 `explain-usage` 看 token 分佈，作為下次調整依據。
11. **壓低冷啟動基線**：每個 session 一開就有固定成本（system tools、MCP tools、skills、memory、system prompt）。
    實測一個幾乎沒對話的 session 就約 70–79k，其中 MCP tools 約 17–22k（常是任務用不到的 connector，例如 Atlassian）。pilot 用 `get_usage` 的 categories 算出基線
    （`tokensUsed` − `Messages`），若 MCP tools 偏高、worker 又用不到，請使用者在 worker session 關掉不需要的 connector。
    基線 × worker 數 = 分工的固定成本，worker 太小就該合併。
11a. **首個 worker 基線驗證閘門**：第一批只先開 1 個 worker，開局後立刻 `get_usage(session_id)` 量它的基線（`tokensUsed` − `Messages`）。
    比 pilot 估的高出 20% 以上，或 MCP tools 超過 15k 且 worker 用不到 → 暫停後續批次，先處理（關 connector、調整啟動方式、合併 worker），
    再開其餘 worker。把「預估 vs 實測」寫進計畫 §3b，供 retro 對照。

12. **Windows 編碼**：含非 ASCII（中文等）的檔案，worker 與 pilot 一律只用 Edit / Write 工具寫入與修改；
    不用 PowerShell（`Get-Content` 會把 UTF-8 當 cp950 讀而損毀檔案）或 heredoc（跳脫字元如 `\a` 會變成控制字元）。
    寫進每個 worker 的 brief 規則區。需要用 shell 讀時指定 UTF-8 編碼。
    Python 腳本一律寫成 UTF-8 檔案再執行（不在 heredoc 內寫含中文或正規表達式的程式），並設 `PYTHONIOENCODING=utf-8`，避免 cp950 錯誤。
13. **工作資料與腳本放工作資料夾，不放暫存目錄**：worker 的原始資料、重現指令用到的腳本與中間檔，一律寫進工作資料夾
    （實測：W3 的校準腳本在暫存目錄，盲審無法重現）。
14. **未授權動作先問**：worker 要下載檔案、安裝套件、curl 外部資源前，先寫進 `status`（blocker）請 pilot 轉問使用者，不自行動手。
    pilot 對 worker 回報的「使用者已授權」一律查證，找不到使用者原話就視為未授權
    （實測：W2 聲稱使用者授權下載縮圖，使用者並未說過）。寫進每個 worker 的 brief 規則區。

## Usage 量測（pilot 取真實數字，不靠 worker 自述；僅限有 usage 工具的環境，否則走「環境偵測」的估計路線）
- `get_usage`（session_id 省略或 `self` = 自己）回傳：
  - `plan.windows`：帳號 5 小時 / 每週用量 % 與重置時間（分批啟動、判斷要不要排隊用這個）
  - `context`：該 session 的 `tokensUsed`、`percentUsed`、距自動壓縮還有多少，以及 `categories`（Messages / System tools / MCP tools / Skills / Memory files / System prompt）
- `list_sessions`（可加 `linked: true` 只看 pilot 自己開的）取得各 worker 的 `sessionId`，再對每個呼叫 `get_usage`。
- 已實測：對「閒置（isRunning=false）」的其他 session 也能讀到 context；但文件說明封存或剛啟動的 session 可能不可用，讀不到就標「不可用」，不要編造。
- 限制：這是 **目前 context 大小**，不是累計花費（壓縮過、或舊內容被丟掉都會讓它變小）；
  用 Agent tool 開的 subagent 是否有自己的 session id 尚未確認，查不到時退回請 worker 自己在完成前呼叫 `get_usage`（self）寫進狀態檔。
- 手動開的 worker 若沒掛在 pilot 底下，用標題從 `list_sessions` 辨認，或請使用者貼 `explain-usage` 結果。
- **模型驗證**：`get_session(session_id)` 會回報該 session 實際的 model / effort；手動模式下模型由使用者在 app 選，pilot 用它確認有沒有照分工表，不要假設。
- **`explain-usage` 的時間點**要對齊「該 worker 完成當下」：請 worker 完成時就跑，並把**原始數字**（input / output / cache read / cache write，不自行加權或換算）寫進狀態檔 `cumulative:`（各 worker 自行加權的結果不可比）；
  事後（尤其下一輪開始前）才跑，各 worker 的數據會不可比。
- 任務前後各記一次 `plan.windows` 的 %，兩者差 = 這次任務對帳號額度的實際消耗。

