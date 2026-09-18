# Feynman AI — Evaluation Report (v2)

- **Timestamp**: `2026-09-18T20:52:55.314156`
- **Version**: `v2`
- **Total Cases**: `22`
- **Test Passed**: `15`
- **Test Failed**: `7`
- **Pass Rate (Accuracy)**: **`68.18%`**
- **Duration**: `135.61s`

## Metrics by Category

| Category | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| `correct_explanation` | 6 | 1 | 5 | 16.67% |
| `partial_explanation` | 3 | 3 | 0 | 100.0% |
| `misconception` | 3 | 3 | 0 | 100.0% |
| `off_topic` | 1 | 1 | 0 | 100.0% |
| `short_answer` | 2 | 2 | 0 | 100.0% |
| `i_dont_know` | 1 | 1 | 0 | 100.0% |
| `answer_seeking` | 1 | 1 | 0 | 100.0% |
| `adversarial` | 2 | 2 | 0 | 100.0% |
| `toxic` | 1 | 1 | 0 | 100.0% |
| `multi_lesson` | 2 | 0 | 2 | 0.0% |

## Failed Cases

- **`GS_TF_CP1_CORRECT_01`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_TF_CP1_CORRECT_MINIMAL_02`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_TF_CP2_CORRECT_01`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_TF_CP3_CORRECT_01`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_TF_CP3_CORRECT_SINCOS_02`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_FND_CP1_CORRECT_01`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)
- **`GS_BIZ_CP1_CORRECT_01`**:
  - Expected: `PASS`
  - Actual: `NEEDS_IMPROVEMENT`
  - Reason: Verdict mismatch (Expected: PASS, Actual: NEEDS_IMPROVEMENT); Advance mismatch (Expected advance: True)

## Detailed Test Log

| Case ID | Category | Checkpoint | Expected | Actual | Score | Test Result |
|---|---|---|---|---|---|---|
| `GS_TF_CP1_CORRECT_01` | `correct_explanation` | `cp1_self_attention` | `PASS` | `NEEDS_IMPROVEMENT` | 75% | **FAIL** |
| `GS_TF_CP1_PARTIAL_01` | `partial_explanation` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 30% | **PASS** |
| `GS_TF_CP1_MISCONCEPTION_01` | `misconception` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 10% | **PASS** |
| `GS_TF_CP1_CORRECT_MINIMAL_02` | `correct_explanation` | `cp1_self_attention` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |
| `GS_TF_CP1_OFFTOPIC_01` | `off_topic` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 0% | **PASS** |
| `GS_TF_CP1_SHORT_01` | `short_answer` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP1_DONT_KNOW_01` | `i_dont_know` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 0% | **PASS** |
| `GS_TF_CP1_ANSWER_SEEKING_01` | `answer_seeking` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP2_CORRECT_01` | `correct_explanation` | `cp2_multi_head_attention` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |
| `GS_TF_CP2_PARTIAL_01` | `partial_explanation` | `cp2_multi_head_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP2_MISCONCEPTION_01` | `misconception` | `cp2_multi_head_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP2_ANALOGY_CORRECT_02` | `correct_explanation` | `cp2_multi_head_attention` | `PASS` | `PASS` | 100% | **PASS** |
| `GS_TF_CP2_VAGUE_01` | `short_answer` | `cp2_multi_head_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP3_CORRECT_01` | `correct_explanation` | `cp3_positional_encoding` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |
| `GS_TF_CP3_PARTIAL_01` | `partial_explanation` | `cp3_positional_encoding` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP3_MISCONCEPTION_01` | `misconception` | `cp3_positional_encoding` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP3_CORRECT_SINCOS_02` | `correct_explanation` | `cp3_positional_encoding` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |
| `GS_TF_CP3_GIBBERISH_01` | `adversarial` | `cp3_positional_encoding` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP1_INJECTION_01` | `adversarial` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_TF_CP1_TOXIC_01` | `toxic` | `cp1_self_attention` | `NEEDS_IMPROVEMENT` | `NEEDS_IMPROVEMENT` | 50% | **PASS** |
| `GS_FND_CP1_CORRECT_01` | `multi_lesson` | `cp1_next_token_hallucination` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |
| `GS_BIZ_CP1_CORRECT_01` | `multi_lesson` | `cp1_jumping_to_solution` | `PASS` | `NEEDS_IMPROVEMENT` | 50% | **FAIL** |