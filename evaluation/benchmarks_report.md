# Medical QA Benchmarks — Literature Review

## What is OpenEvidence?

OpenEvidence is a clinical AI platform founded in 2021, used by physicians to answer medical questions with citations from the literature. Its architecture is not publicly disclosed. Based on its public product, it references sources such as NEJM, JAMA, and UpToDate. It is not known whether it uses RAG, fine-tuning, or both.

**Publicly reported performance (official NBME sample exam, not MedQA):**
- >90% on the official 2022 USMLE sample exam (July 2023 announcement)
- 100% on the same exam (August 2025 announcement)

No peer-reviewed paper from OpenEvidence reporting evaluation on MedQA, MMLU, MedMCQA, PubMedQA, BioASQ, or ClinicalBench has been identified. The benchmarks below are standard medical QA benchmarks used in the broader medical AI literature, and are recommended for evaluating our agent — they are **not** confirmed evaluation benchmarks of OpenEvidence itself.

---

## Standard Medical QA Benchmarks

### 1. MedQA (USMLE) ⭐⭐⭐
- **Source**: Jin et al. "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams." arXiv:2009.13081
- **Dataset**: ~12,700 questions from USMLE Step 1, Step 2, Step 3 (English set, original 5-option format). The GBaker HuggingFace variant reformats these as 4-option MCQ.
- **HuggingFace**: `GBaker/MedQA-USMLE-4-options`
- **Why use it**: Gold standard for clinical reasoning. Widely used across Med-PaLM, GPT-4, and Gemini papers, making results directly comparable.

### 2. MMLU (Medical Subsets) ⭐⭐⭐
- **Source**: Hendrycks et al. "Measuring Massive Multitask Language Understanding." arXiv:2009.03300
- **Medical categories**: Clinical Knowledge, Medical Genetics, Anatomy, Professional Medicine, College Medicine, College Biology
- **Format**: 4-option MCQ, ~1,100 test questions across the six medical subsets
- **HuggingFace**: `cais/mmlu` — subsets: `clinical_knowledge`, `medical_genetics`, `anatomy`, `professional_medicine`, `college_medicine`, `college_biology`
- **Why use it**: Broad coverage of medical knowledge domains; directly reported in GPT-4 and Med-PaLM 2 papers.

### 3. MedMCQA ⭐⭐
- **Source**: Pal et al. "MedMCQA: A Large-scale Multi-Subject Multi-Choice Dataset for Medical Exam Questions." PMLR, 2022
- **Dataset**: ~194,000 MCQs from AIIMS and NEET PG Indian medical entrance exams, covering 21 medical subjects
- **HuggingFace**: `openlifescienceai/medmcqa`
- **Why use it**: Large scale and diverse. No reliable "human doctor baseline" figure has been found in the source paper — omitted.

### 4. PubMedQA ⭐⭐
- **Source**: Jin et al. "PubMedQA: A Dataset for Biomedical Research Question Answering." EMNLP 2019
- **Dataset**: 1,000 expert-labeled questions (pqa_labeled), 61,000 unlabeled, from PubMed abstracts. Format: yes/no/maybe given abstract context.
- **HuggingFace**: `qiaojin/PubMedQA`, config `pqa_labeled`
- **Why use it**: Tests literature-grounded reasoning — directly relevant to any RAG-based clinical agent. Human performance on pqa_labeled: ~78% (reported in the original paper).

### 5. Kanjee et al. 2023 (NEJM Case Records) ⭐⭐
- **Source**: Kanjee Z et al. "Accuracy of a Generative Artificial Intelligence Model in a Complex Diagnostic Challenge." JAMA. 2023;330(1):78–80. doi:10.1001/jama.2023.8288
- **What**: Evaluated **GPT-4 only** on 70 NEJM clinicopathological conference case records. OpenEvidence was **not** part of this study.
- **Format**: Difficult open-ended diagnostic cases graded against expert physician answers
- **Key result**: GPT-4 listed the correct diagnosis in 64% of cases (top-1), 88% in top-3. Authors note GPT-4 performed at the level of a senior resident.
- **Note**: Frequently cited alongside OpenEvidence discussions, but the paper itself does not evaluate or mention OpenEvidence.

### 6. ClinicalBench ⭐
- **Source**: Chen et al. 2024
- **What**: Evaluates LLMs vs traditional ML models on clinical **prediction** tasks (e.g., mortality prediction, readmission) — not open-ended clinical reasoning QA. Less directly relevant to a clinical assistant agent.

### 7. BioASQ ⭐
- **Source**: Tsatsaronis et al. 2015. BioASQ challenge
- **Dataset**: Biomedical QA from PubMed: yes/no, factoid, list, and summary questions
- **Why use it**: Useful for evaluating retrieval-augmented systems specifically. Less commonly used as a primary benchmark in recent LLM papers.

---

## Summary Table

| Benchmark | Questions | Format | Free? | Best Use Case |
|-----------|-----------|--------|-------|---------------|
| MedQA (USMLE) | ~12,700 | 4-option MCQ | Yes | Clinical reasoning; comparisons with GPT-4/Med-PaLM |
| MMLU Medical | ~1,100 | 4-option MCQ | Yes | Broad medical knowledge |
| MedMCQA | ~194,000 | 4-option MCQ | Yes | Large-scale diverse evaluation |
| PubMedQA | 1,000 (labeled) | Yes/No/Maybe | Yes | Literature-grounded RAG evaluation |
| NEJM Cases (Kanjee) | 70 | Open-ended | No | Hard diagnostic reasoning (GPT-4 only) |
| BioASQ | Varies | Mixed | Yes* | Biomedical retrieval |

---

## Metrics Used

1. **Accuracy** — primary metric for MCQ benchmarks
2. **Top-1 / Top-3 diagnostic accuracy** — for open-ended case evaluations (Kanjee et al.)
3. **Physician-graded scores** — human expert evaluation of free-text answers
4. **Citation quality** — whether cited papers actually support the answer

---

## Published Results Table

Numbers are taken from the papers cited. Only figures explicitly reported in those papers are included.

| Model | MedQA | MMLU Clinical Knowledge | PubMedQA | Source |
|-------|-------|------------------------|----------|--------|
| Med-Gemini (Saab et al. 2024) | 91.1% | — | — | Saab et al., arXiv:2404.18416 |
| GPT-4 | 87.0% | 86.0% | 75.2% | Nori et al., arXiv:2303.13375 |
| Med-PaLM 2 | 86.5% | — | 81.8% | Singhal et al., arXiv:2305.09617 |
| GPT-3.5 | 57.0% | 72.6% | 74.4% | Nori et al., arXiv:2303.13375 |
| Human (PubMedQA) | — | — | 78.0% | Jin et al., EMNLP 2019 |

**Notes:**
- MMLU scores are per-subset. The 86.0% for GPT-4 is the Clinical Knowledge subset specifically (Nori et al., Table 2). Other subsets vary (Anatomy: 80.0%, Medical Genetics: 91.0%, Professional Medicine: 93.0%, College Medicine: 76.9%, College Biology: 95.1%).
- Med-Gemini (not Gemini 1.5 Pro base) achieves 91.1% on MedQA via specialist fine-tuning — not a base model result.
- Med-PaLM 2's best PubMedQA score is 81.8% (few-shot); 79.7% is an earlier checkpoint.
- No verified "human generalist" MedQA score found in the source papers. The ~60% figure often cited refers to the approximate USMLE passing threshold, not a measured human sample.

---

## Recommendations for This Project

**Use for evaluation (all free, on HuggingFace):**
1. **MedQA** — primary benchmark; 20–50 samples for quick eval, results are directly comparable to GPT-4 / Med-PaLM baselines
2. **PubMedQA** — specifically tests whether RAG (PubMed retrieval) improves yes/no/maybe reasoning — the most relevant benchmark for this agent's design
3. **MMLU Medical subsets** — good for breadth across knowledge domains

**Internal evaluation:**
- The 10-question mini-set in `evaluation/mini_set.py` for qualitative, fast iteration

**What not to claim:**
- Do not claim results are comparable to OpenEvidence's internal evaluations — OpenEvidence has not published on these benchmarks
- The NBME sample exam (OpenEvidence's reported benchmark) is a proprietary exam and not publicly available for replication

---

## References

1. Jin et al. (2021). "What Disease does this Patient Have?" arXiv:2009.13081
2. Hendrycks et al. (2020). "MMLU." arXiv:2009.03300
3. Pal et al. (2022). "MedMCQA." PMLR
4. Jin et al. (2019). "PubMedQA." EMNLP 2019
5. Kanjee Z et al. (2023). "Accuracy of a Generative Artificial Intelligence Model in a Complex Diagnostic Challenge." JAMA. 330(1):78–80. doi:10.1001/jama.2023.8288
6. Nori et al. (2023). "Capabilities of GPT-4 on Medical Challenge Problems." arXiv:2303.13375
7. Singhal et al. (2023). "Large Language Models Encode Clinical Knowledge." Nature. (arXiv submitted 2022, published 2023)
8. Singhal et al. (2023). "Towards Expert-Level Medical QA with LLMs." arXiv:2305.09617
9. Saab et al. (2024). "Capabilities of Gemini Models in Medicine." arXiv:2404.18416
10. Tsatsaronis et al. (2015). "An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition." BMC Bioinformatics
