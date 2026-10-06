# Benchmark Scorecard: Julius AI vs BI Report Automation (Ollama Brain)

This scorecard evaluates the performance of the local Ollama Brain against Julius AI using the 40 benchmark prompts.

## Scoring Rubric (0-2 points per category)

| Category | Description | 0 Points | 1 Point | 2 Points |
| :--- | :--- | :--- | :--- | :--- |
| **Correct Numbers** | Does the system compute the correct metric based on data/semantics? | Fails / Hallucinates | Correct but requires a follow-up fix | Correct on first try |
| **Correct Chart** | Is the chosen visualization suitable for the user's intent? | Bad/misleading chart | Okay chart, but not optimal | Perfect chart choice |
| **Strict Scope** | Does it generate ONLY what was asked? | Spams unrelated charts | Generates 1-2 extra items | Exact match to intent |
| **Label Legibility** | Are axis labels readable (no overlap, rotated properly)? | Messy/overlapped | Readable but cut off | Crisp and responsive |
| **Assumptions** | Does the system explain its column/aggregation mappings? | Silent | Confusing explanation | Clear, brief explanation |
| **Privacy/Offline** | Is data processing completely local? | External APIs used | Hybrid | 100% Local / Air-gapped |
| **Speed** | End-to-end execution latency for a 100k row dataset | > 30 seconds | 10-30 seconds | < 10 seconds |

## Parity Matrix

| Prompt Group | Julius AI Score | Our BI Tool Score | Notes / Deficiencies |
| :--- | :---: | :---: | :--- |
| 1. KPI Cards & Simple Aggregations | | | |
| 2. Aggregations & Data Tables | | | |
| 3. Trends & Time Series | | | |
| 4. Comparisons & Breakdowns | | | |
| 5. Distributions & Outliers | | | |
| 6. Top-N & Filters / Time Ranges | | | |
| 7. Unusual/Complex Charts | | | |
| 8. Impossible/Misleading Requests | | | |

*Note: This scorecard is to be filled out by the user after running the prompts.*
