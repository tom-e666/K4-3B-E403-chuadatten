# Feynman AI — Evaluation & Benchmarking Suite

Welcome to the evaluation layer for the **Feynman AI** Reverse Tutoring project. This directory contains the test harness, Golden Set benchmark cases, automated execution scripts, and empirical evaluation reports.

---

## 1. Purpose of Evaluation

The evaluation suite serves to objectively measure the quality, accuracy, and resilience of the Feynman AI system:
- **Pedagogical Accuracy**: Does the system accurately distinguish between correct, partial, and misconceived explanations?
- **Boundary Safeguards**: Does the system resist premature checkpoint advancement when given off-topic, toxic, prompt injection, or low-effort inputs?
- **Workflow Integrity**: Does the multi-stage Reverse Tutoring loop (Session Start $\rightarrow$ Naive Partner Questioning $\rightarrow$ Dual Evaluation $\rightarrow$ Checkpoint Progression $\rightarrow$ Mastery Report) execute end-to-end without breakdown?

---

## 2. Test PASS vs. Product PASS

It is crucial to distinguish between two different concepts of "PASS":

* **Product Verdict (`actual_verdict`)**:
  - The pedagogical assessment returned by the system for the student's explanation.
  - Possible values: `PASS` (mastery score $\ge 80\%$) or `NEEDS_IMPROVEMENT` (mastery score $< 80\%$).

* **Test Result (`test_result`)**:
  - The evaluation harness's assertion on whether the system's behavior matched expectations.
  - Example: A student intentionally inputs a common misconception. The expected product verdict is `NEEDS_IMPROVEMENT`. If the system returns `NEEDS_IMPROVEMENT`, the **Test Result is PASS** (the system correctly caught the error).

---

## 3. Golden Set Structure & Categories

The benchmark dataset is located at [`eval/golden_dataset.json`](golden_dataset.json) and comprises 22 standardized cases with stable identifiers (`GS_<LESSON>_<CP>_<CATEGORY>_<NUM>`):

| Category | Description | Target Expected Verdict |
|---|---|:---:|
| `correct_explanation` | Accurate, comprehensive explanation covering required rubric points. | `PASS` |
| `partial_explanation` | Explains part of the concept but omits essential technical elements. | `NEEDS_IMPROVEMENT` |
| `misconception` | Expresses a known conceptual mistake targeted by the checkpoint. | `NEEDS_IMPROVEMENT` |
| `short_answer` | Extremely short or uninformative confirmation ("Đúng rồi đấy"). | `NEEDS_IMPROVEMENT` |
| `i_dont_know` | Student explicitly admits lack of knowledge. | `NEEDS_IMPROVEMENT` |
| `answer_seeking` | Student attempts to demand the answer directly from the AI. | `NEEDS_IMPROVEMENT` |
| `off_topic` | Irrelevant or casual conversational input. | `NEEDS_IMPROVEMENT` |
| `adversarial` | Prompt injection, jailbreak attempts, or gibberish. | `NEEDS_IMPROVEMENT` |
| `toxic` | Disrespectful or negative sentiment towards the partner. | `NEEDS_IMPROVEMENT` |
| `multi_lesson` | Cross-topic coverage spanning Lesson 1 (Foundation) and Lesson 3 (Business AI). | `PASS` |

### JSON Schema per Case
```json
{
  "id": "GS_TF_CP1_CORRECT_01",
  "lesson_id": "lesson_02",
  "checkpoint_id": "cp1_self_attention",
  "category": "correct_explanation",
  "user_input": "...",
  "expected_status": "PASS",
  "expected": {
    "verdict": "PASS",
    "checkpoint_advance": true
  },
  "description": "..."
}
```

---

## 4. How to Run Evaluations

### A. Run Golden Set Evaluation
To run the automated Golden Set benchmark runner:

```powershell
# Using project virtual environment
.\.venv\Scripts\python.exe eval\run_eval.py

# Or run the batch script from project root
.\run_eval.bat
```

### B. Run End-to-End (E2E) Server Tests
To verify API contracts, session management, negative/positive path progression, and mastery reports:

```powershell
.\.venv\Scripts\python.exe eval\test_server_e2e.py
```

---

## 5. Artifacts and Output Files

All results are saved into [`eval/results/`](results/):
- **[`eval/results/v0_results.json`](results/v0_results.json)** / **[`v0_results.md`](results/v0_results.md)**: Documentation and qualitative metrics for v0 (Static Scripted PoC).
- **[`eval/results/v1_results.json`](results/v1_results.json)** / **[`v1_results.md`](results/v1_results.md)**: Baseline documentation and status for v1 (First Functional Prototype).
- **[`eval/results/v2_results.json`](results/v2_results.json)** / **[`v2_results.md`](results/v2_results.md)**: Empirical test run results for v2 (Current Golden Set benchmark).
- **[`eval/results/comparison.md`](results/comparison.md)**: Transparent version comparison tracking progression across v0, v1, and v2.
- **[`eval/eval_report.json`](eval_report.json)**: Legacy compatibility output file consumed by root batch scripts.

---

## 6. Version Comparison (v0 $\rightarrow$ v1 $\rightarrow$ v2)

| Dimension | v0 | v1 | v2 |
|---|:---:|:---:|:---:|
| **Release Type** | Hardcoded Script / PoC | Functional Prototype | Full-Stack SaaS System |
| **Automated Golden Set** | N/A | Historical Result Unavailable | 22 cases |
| **Measured Pass Rate** | N/A | NOT REPRODUCED | **68.18%** |
| **E2E Integration Test** | None | None | 7/7 Passing |
| **LLM Provider** | None | Gemini API | Gemini 2.5 Flash + Agent Loop |
| **Multi-Lesson Support** | No | Limited | 3 Lessons (Foundation, Transformer, Business) |
| **Resilience & Fallback** | None | None | Yes (Observed in E2E & live runs) |

---

## 7. Known Limitations & Failure Analysis

1. **Provider Rate Limiting (HTTP 429 / 503)**:
   - When evaluating many cases sequentially against free-tier cloud LLM providers, quotas may be temporarily exceeded.
   - `backend/professor_agent.py` catches provider errors and assigns a baseline score of 50 (`NEEDS_IMPROVEMENT`), allowing the application to avoid crashes but causing false negatives on correct explanations during high-load periods.
2. **Strict Black-Box Boundary**:
   - Production code was intentionally preserved without modification. Future versions (v3) should propagate provider exceptions to the secondary keyword-based rubric fallback to ensure high availability under quota exhaustion.

