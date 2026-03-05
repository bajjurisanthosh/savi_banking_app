---
name: analyze-transactions
description: Analyzes spending patterns in the SaVi banking app. Use when the user asks about spending habits, top categories, unusual transactions, or account summaries.
---

Analyze the transaction data in mock_data.py (or banking.db if it exists).

1. Group transactions by category and calculate totals
2. Identify the top 3 spending categories
3. Flag any unusually large transactions (>2x the average for that category)
4. Calculate net cash flow (credits minus debits) per account
5. Present findings as a concise summary with a markdown table

Keep the analysis practical and actionable — this is a banking app user looking to understand their finances.
