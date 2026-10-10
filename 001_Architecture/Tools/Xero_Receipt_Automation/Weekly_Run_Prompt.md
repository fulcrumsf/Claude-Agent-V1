# Weekly Run Prompt — Xero Receipt Automation

Run this in Claude Desktop every Saturday at 08:00 local time (`0 8 * * 6`).

1. Change directory to the promoted `Xero_Receipt_Automation` folder.
2. Run `python3 xero_receipts.py run --scheduled --live --json` and note the `run_id` it prints.
3. Execute the Gmail search plan with the connected Gmail connector using the queries in `<data_dir>/Run_<id>_Search_Plan.json`.
4. Save candidate metadata and plain text as `<data_dir>/Run_<id>_Gmail_Candidates.json`, then finish with `python3 xero_receipts.py run --scheduled --live --run-id <id>`.
5. Run `python3 xero_receipts.py notify-check --json`.
6. If it says `SEND`, run `python3 xero_receipts.py notify --channel macos`.
7. Record delivery with `python3 xero_receipts.py notify --sent macos --result "<tool result>"`.
8. Stop. No retries and no second notification in the same ISO week.

Do **not** use `PushNotification`; the macOS banner is the one and only delivery channel. Do not call any Gmail or Xero write tool. If an outage occurs, record the failure and wait for the next scheduled run.
