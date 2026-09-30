# MedAgent Evaluation Report

## Setup

- **Agent**: LangGraph ReAct agent with PubMed + MedRxiv retrieval tools
- **LLM provider**: Groq (free tier)
- **Models tested**: `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`
- **Date**: September 2026

---

## Part 1 — Mini-Set Qualitative Evaluation (10 questions)

10 clinical questions spanning 5 specialties, designed to test guideline knowledge, evidence synthesis, and clinical reasoning.

**Model**: `openai/gpt-oss-20b` via Groq | **Mode**: RAG (PubMed search enabled)

| ID | Category | Status | Evidence Quality |
|----|----------|--------|-----------------|
| Q01 | Pharmacology (T2DM first-line) | ✅ | High |
| Q02 | Critical Care (Sepsis-3 criteria) | ✅ | High |
| Q03 | Infectious Disease (CAP treatment) | ✅ | High |
| Q04 | Cardiology (DOACs vs warfarin) | ✅ | High |
| Q05 | Oncology (CRC screening) | ✅ | High |
| Q06 | COVID-19 (corticosteroids) | ✅ | High |
| Q07 | Cardiology (hypertensive urgency) | ✅ | Moderate |
| Q08 | Cardiology/Prevention (aspirin) | ✅ | High |
| Q09 | Infectious Disease (C. difficile) | ✅ | High |
| Q10 | Gastroenterology (pancreatitis pain) | ✅ | High |

**10/10 complete | Knowledge failures: 0**

---

### Qualitative Reviews

#### Q01 — Pharmacology (T2DM first-line treatment)

**Reference**: Metformin first-line unless contraindicated (eGFR < 30). SGLT-2i/GLP-1 RA first-line if established CVD, HF, or CKD.

**Agent answer summary**: Metformin correctly identified as foundation. GLP-1 RA and SGLT2i correctly flagged for CVD/HF/CKD patients. Cites ADA 2024 Standards of Care and major cardiovascular outcome trials (LEADER, SUSTAIN-6, EMPA-REG OUTCOME, DAPA-HF). Includes eGFR contraindication, cost barrier, GI side effects, weight considerations, and hypoglycemia risk comparison.

**Assessment**: ✅ Correct and complete. The organ-specific guidance (SGLT2i for HF/CKD, GLP-1 RA for ASCVD) is accurately differentiated. No factual errors. Evidence Quality: **High**.

---

#### Q02 — Critical Care (Sepsis-3 criteria)

**Reference**: SOFA ≥2 from baseline; septic shock = vasopressors to maintain MAP ≥65 mmHg + lactate >2 mmol/L despite adequate fluids.

**Agent answer summary**: Correct definition of sepsis and SOFA ≥2 criterion. Correctly adds qSOFA as a *screening* tool, not a diagnostic criterion (a nuance many sources miss). Includes Sepsis-2 vs Sepsis-3 comparison (SIRS removed, "severe sepsis" eliminated). Correctly specifies septic shock as MAP ≥65 + lactate >2 *despite* fluid resuscitation. Adds pediatric caveat (Schlapbach et al. JAMA 2024). Cites Singer et al. and Seymour et al. JAMA 2016.

**Assessment**: ✅ Correct and complete. The qSOFA nuance (screening vs diagnosis) is clinically important and correctly handled. No factual errors. Evidence Quality: **High**.

---

#### Q03 — Infectious Disease (CAP antibiotic regimen)

**Reference**: β-lactam + macrolide OR respiratory fluoroquinolone for non-ICU hospitalised adults (IDSA/ATS).

**Agent answer summary**: Ceftriaxone + azithromycin (Option A) or levofloxacin monotherapy (Option B). Cites IDSA/ATS 2019, a 2020 Cochrane meta-analysis (30 RCTs, no mortality difference between regimens), and a Lancet 2020 cohort study (β-lactam + macrolide favoured in comorbid patients). Correctly flags local macrolide resistance, QT-prolonging drug interactions, and β-lactam allergy management. De-escalation to oral therapy at 48–72 h if stable.

**Assessment**: ✅ Correct and complete. Appropriately hedges on regional resistance. Evidence Quality: **High**.

---

#### Q04 — Cardiology/Hematology (DOACs vs warfarin)

**Reference**: Direct Xa inhibitors (rivaroxaban, apixaban, edoxaban) vs direct thrombin inhibitor (dabigatran); preferred over warfarin for NVAF/VTE without mechanical valves.

**Agent answer summary**: Correctly names all four DOACs and their mechanism class. Cites BMJ network meta-analysis and Clin Pharmacol Ther systematic review. Lists reversal agents (idarucizumab for dabigatran; andexanet alfa for Xa inhibitors). Correct contraindications: mechanical valves, antiphospholipid syndrome, severe renal/hepatic impairment, pregnancy. Flags CYP3A4/P-gp interactions.

**Assessment**: ✅ Correct and complete. Reversal-agent detail exceeds the reference. No factual errors. Evidence Quality: **High**.

---

#### Q05 — Oncology/Screening (CRC screening)

**Reference**: USPSTF 2021, ages 45–75, all modalities listed (colonoscopy q10y, annual FIT/FOBT, CT colonography q5y, flex sig q5y, stool DNA q1–3y). Individualized for 76–85.

**Agent answer summary**: Correctly states USPSTF 2021 lowered starting age to 45. Lists all six modalities with correct intervals. Includes MSTF tiered ranking (first-tier: colonoscopy q10y and annual FIT). Cites 2024 systematic review of 18 international guidelines and a 2025 JAMA RCT on the 45–49 age group. Correct upper limit (75 for routine; individualized 76–85; against routine >85).

**Assessment**: ✅ Correct and complete. More current than the reference (includes 2025 data). The MSTF tiered ranking is a clinically useful addition. No factual errors. Evidence Quality: **High**.

---

#### Q06 — COVID-19 (corticosteroids)

**Reference**: RECOVERY trial dexamethasone 6 mg/day × 10 days; RR 0.83 for O₂-requiring patients; RR 0.64 for mechanically ventilated; no benefit (possible harm) without O₂.

**Agent answer summary**: Correctly identifies RECOVERY trial and dexamethasone 6 mg for 10 days. Gives specific absolute mortality numbers (30%→25% for O₂ patients; 41%→32% for ventilated). Correctly notes no benefit without O₂. Discusses COVID STEROID 2 (higher doses not superior) and EARLY-DEX trial (pre-emptive use, no current recommendation).

**Assessment**: ✅ Correct and complete. The absolute risk reduction figures are accurate. The coverage of follow-up trials adds useful context. No factual errors. Evidence Quality: **High**.

---

#### Q07 — Cardiology (hypertensive urgency)

**Reference**: Oral antihypertensives, gradual BP reduction over 24–48 h; IV agents not needed without end-organ damage.

**Agent answer summary**: Correctly distinguishes urgency (no end-organ damage) from emergency (requires IV). Cites Park et al. 2017 (rest alone achieved similar BP control to oral clonidine over 24 h). Recommends outpatient oral therapy; lists appropriate agents (clonidine, captopril, labetalol, nifedipine). Flags dangers of over-rapid reduction (ischaemic stroke, MI).

**Assessment**: ✅ Correct and complete. The rest-alone RCT citation is a clinically valuable addition. Evidence Quality: **Moderate** (sparse and heterogeneous literature, which is accurate).

---

#### Q08 — Cardiology/Prevention (aspirin in primary prevention)

**Reference**: Recent RCTs (ARRIVE, ASPREE, ASCEND) show marginal benefit and increased bleeding; USPSTF against routine use for ≥60 y.

**Agent answer summary**: Cites Baigent 2009 Lancet meta-analysis (12% relative risk reduction, 30% bleeding increase; net absolute benefit 0.3%/year), Mahmoud 2019 Eur Heart J meta-analysis, ASCEND 2018 NEJM (diabetes, n=15,480). Correctly concludes no routine primary-prevention use in low-risk patients. Correctly identifies diabetes as the subgroup where modest benefit may persist.

**Assessment**: ✅ Correct. ASCEND cited; meta-analytic conclusion is equivalent to ARRIVE/ASPREE. No factual errors. Evidence Quality: **High**.

---

#### Q09 — Infectious Disease (C. difficile diagnosis and treatment)

**Reference**: ≥3 loose stools + positive NAAT/EIA; vancomycin 125 mg QID × 10 d (preferred) or fidaxomicin.

**Agent answer summary**: Two-step diagnostic algorithm: GDH or toxin EIA → PCR for toxin genes. Treatment: vancomycin 125 mg q6 h × 10 d OR fidaxomicin 200 mg q12 h × 10 d (preferred for recurrence reduction). Metronidazole reserved for mild disease or unavailability. Mentions bezlotoxumab and FMT for recurrent/refractory disease.

**Assessment**: ✅ Correct and complete. Two-step diagnostic algorithm is current best practice. Fidaxomicin preference for recurrence prevention is accurate per 2021 IDSA update. No factual errors. Evidence Quality: **High**.

---

#### Q10 — Gastroenterology (pain management in acute pancreatitis)

**Reference**: IV opioids standard; early feeding preferred; NSAIDs for mild cases.

**Agent answer summary**: Multimodal approach: opioids (morphine/hydromorphone) as cornerstone; NSAIDs or acetaminophen as adjuncts if no contraindication. Cites Baron 2020 AGA Clinical Practice Update (multimodal analgesia + early enteral nutrition). Recommends early enteral nutrition within 24–48 h to reduce pain. Escalation to pain specialist or regional block (TAP) for refractory cases.

**Assessment**: ✅ Correct and complete. Balanced, evidence-informed, appropriately cautious about unproven adjuncts. Evidence Quality: **Low** (accurately rated — reflects the real state of the evidence).

---

### Mini-Set Summary

| ID | Category | Answer quality | Key observation |
|----|----------|---------------|-----------------|
| Q01 | Pharmacology | ✅ High | ADA 2024 cited; CVOT trials named; organ-specific guidance correct |
| Q02 | Critical Care | ✅ High | qSOFA correctly framed as screening-only; Sepsis-2 vs 3 comparison |
| Q03 | Infectious Disease | ✅ High | IDSA/ATS 2019 cited; de-escalation guidance included |
| Q04 | Cardiology | ✅ High | All four DOACs named; reversal agents; correct APS/valve contraindications |
| Q05 | Oncology | ✅ High | MSTF tiered ranking; 2025 age-45 trial data included |
| Q06 | COVID-19 | ✅ High | RECOVERY absolute numbers correct; follow-up trials covered |
| Q07 | Cardiology | ✅ Moderate | Rest-alone RCT cited; correctly advises against rapid IV reduction |
| Q08 | Cardiology/Prevention | ✅ High | ASCEND + meta-analyses cited; correct net-benefit framing |
| Q09 | Infectious Disease | ✅ High | Two-step diagnostic algorithm; fidaxomicin preference for recurrence |
| Q10 | Gastroenterology | ✅ High | Multimodal strategy; correctly rates evidence quality as Low |

**10/10 complete | Knowledge failures: 0**

---

## Part 2 — MedQA-USMLE Benchmark (direct mode)

**Model**: `openai/gpt-oss-20b` via Groq | **Mode**: Direct (no RAG) | **Subset**: 20 questions from the 1273-question test set

| # | Correct | Predicted | Result | Question summary |
|---|---------|-----------|--------|-----------------|
| 1 | B | A | ❌ | Orthopaedic resident / ethical disclosure |
| 2 | D | D | ✅ | Transitional cell carcinoma management |
| 3 | B | B | ✅ | Post-cardiac catheterization complication |
| 4 | D | D | ✅ | Emergency department presentation |
| 5 | B | B | ✅ | Itchy skin lesion diagnosis |
| 6 | D | A | ❌ | Emergency department metabolic case |
| 7 | C | ? | ⚠️ | 68-year-old evaluation (no letter extracted) |
| 8 | C | C | ✅ | Elderly man, emergency department |
| 9 | B | B | ✅ | Primary care presentation |
| 10 | A | A | ✅ | Young woman physician visit |
| 11 | D | D | ✅ | 39-week gestation obstetrics |
| 12 | D | D | ✅ | 72-year-old 2-month complaint |
| 13 | B | B | ✅ | 20-year-old worsening condition |
| 14 | D | D | ✅ | Executive scheduled appointment |
| 15 | C | C | ✅ | Microbiologist virulent strain |
| 16 | B | D | ❌ | 59-year-old overweight urgent care |
| 17 | D | D | ✅ | 7-year-old pediatrician visit |
| 18 | D | B | ❌ | 3-month-old emergency department |
| 19 | B | B | ✅ | 29-year-old emergency presentation |
| 20 | D | B | ❌ | 46-year-old emergency department |

**Accuracy: 70.0% (14/20)**

### Comparison with published baselines

| Model | MedQA Accuracy | Test set size | Source |
|-------|---------------|--------------|--------|
| Med-Gemini | 91.1% | full | Saab et al., arXiv:2404.18416 |
| GPT-4 | 87.0% | full | Nori et al., arXiv:2303.13375 |
| Med-PaLM 2 | 86.5% | full | Singhal et al., arXiv:2305.09617 |
| **MedAgent (gpt-oss-20b, direct)** | **70.0%** | **20 (subset)** | **This work** |
| GPT-3.5 | 57.0% | full | Nori et al., arXiv:2303.13375 |
| USMLE passing threshold | ~60% | — | Official NBME |

---

## Part 3 — MedQA-USMLE Benchmark (RAG mode)

**Model**: `openai/gpt-oss-20b` via Groq | **Mode**: RAG (PubMed search enabled) | **Subset**: 20 questions

| # | Correct | Predicted | Result | Answer preview |
|---|---------|-----------|--------|----------------|
| 1 | B | A | ❌ | Disclosure error to patient and document in operative report |
| 2 | D | C | ❌ | Cisplatin ototoxicity mediated by free radicals damaging cochlear cells |
| 3 | B | B | ✅ | Cholesterol embolization after vascular procedure |
| 4 | D | D | ✅ | Lipid-A component of LPS, gram-negative rods |
| 5 | B | B | ✅ | Ketotifen eye drops, antihistamine/mast-cell stabilizer |
| 6 | D | A | ❌ | Calcium-channel blocker to counteract cocaine-induced vasospasm |
| 7 | C | C | ✅ | Common iliac artery aneurysm compressing ureter |
| 8 | C | C | ✅ | Clopidogrel dual antiplatelet therapy after PCI |
| 9 | B | B | ✅ | Active or recurrent PID is IUD contraindication |
| 10 | A | A | ✅ | Nail pitting classic for psoriasis |
| 11 | D | D | ✅ | HIV-1/HIV-2 antibody differentiation immunoassay (Western blot) |
| 12 | D | D | ✅ | Ruxolitinib (JAK1/2 inhibitor) for primary myelofibrosis |
| 13 | B | B | ✅ | NF2 / merlin mutation → meningiomas and vestibular schwannomas |
| 14 | D | D | ✅ | Standing reduces venous return → reflex tachycardia |
| 15 | C | C | ✅ | Rotavirus segmented dsRNA → reassortment |
| 16 | B | D | ❌ | Pancreatitis (incorrect answer) |
| 17 | D | D | ✅ | IL-4 Th2 cytokine drives IgE class switching in asthma |
| 18 | D | D | ✅ | Matching to balance confounders between groups |
| 19 | B | B | ✅ | Ibuprofen + colchicine for acute idiopathic pericarditis |
| 20 | D | D | ✅ | Benzodiazepine intoxication |

**Accuracy: 80.0% (16/20)**

### RAG vs direct comparison

| Mode | Accuracy | Wrong questions |
|------|----------|-----------------|
| Direct (gpt-oss-20b, no RAG) | 70.0% (14/20) | Q1, Q6, Q16, Q18, Q20 + 1 extraction |
| **RAG (gpt-oss-20b, PubMed)** | **80.0% (16/20)** | **Q1, Q2, Q6, Q16** |

RAG improved accuracy by **+10 pp**. Three questions flipped correct (Q18, Q20, Q7). One question regressed (Q2 — cisplatin pharmacology mechanism, where retrieved papers added noise rather than signal).

### Error analysis (RAG mode)

- **Q1 (ethics)** — Both modes wrong. PubMed retrieval does not help with USMLE ethics/disclosure questions that test regulatory guidelines rather than clinical literature.
- **Q2 (cisplatin ototoxicity)** — Regressed from direct mode. Retrieved papers on cisplatin nephrotoxicity/neurotoxicity muddied the mechanism answer.
- **Q6 (cocaine chest pain)** — Both modes wrong. CCBs are used for cocaine-induced vasospasm, but the specific USMLE answer tests knowledge of beta-blocker contraindication.
- **Q16 (overweight urgent care)** — Both modes wrong. Retrieved pancreatitis literature biased the model toward a plausible but incorrect diagnosis.

---

## Part 4 — PubMedQA Benchmark

**Model**: `openai/gpt-oss-20b` via Groq | **Mode**: RAG (PubMed search enabled) | **Subset**: 20 questions from `pqa_labeled`

| # | Question (abbreviated) | Correct | Predicted | Result |
|---|------------------------|---------|-----------|--------|
| 1 | Mitochondria in lace plant programmed cell death? | yes | yes | ✅ |
| 2 | Landolt C vs Snellen E in strabismus amblyopia? | no | maybe | ❌ |
| 3 | Syncope during bathing in infants — water-induced urticaria? | yes | no | ❌ |
| 4 | Transanal vs transabdominal pull-through long-term results equal? | no | maybe | ❌ |
| 5 | Tailored interventions increase mammography in HMO women? | yes | yes | ✅ |
| 6 | Double balloon enteroscopy safe in community setting? | yes | maybe | ❌ |
| 7 | 30-day and 1-year mortality in emergency laparotomies — area of concern? | maybe | yes | ❌ |
| 8 | Adjustment for reporting heterogeneity necessary in sleep disorders? | no | yes | ❌ |
| 9 | Low HDL-C mutations promote carotid intima-media thickness? | no | maybe | ❌ |
| 10 | 23-hour ward in children's hospital effective? | yes | maybe | ❌ |
| 11 | Chile traffic law reform push police enforcement? | yes | yes | ✅ |
| 12 | Therapeutic anticoagulation in trauma patient safe? | no | no | ✅ |
| 13 | Routine labs useful to differentiate NASH vs alcoholic steatohepatitis? | yes | maybe | ❌ |
| 14 | Family history prompting for primary care providers — does it work? | no | no | ✅ |
| 15 | Ultrasound fellowship programs impact EM residents' education? | yes | maybe | ❌ |
| 16 | Patient-controlled opioid therapy for breathlessness in palliative care? | yes | maybe | ❌ |
| 17 | Living-related liver transplantation still needed in children? | yes | yes | ✅ |
| 18 | Patterns of knowledge/attitudes among unvaccinated seniors? | yes | yes | ✅ |
| 19 | Model to teach retroperitoneoscopic nephrectomy? | yes | yes | ✅ |
| 20 | Resting heart rate relevant for cardiovascular risk in rural West Africa? | yes | yes | ✅ |

**Accuracy: 45.0% (9/20)**

### Comparison with published baselines

| Model | PubMedQA Accuracy | Mode | Source |
|-------|-------------------|------|--------|
| Med-PaLM 2 | 81.8% | Few-shot, direct | Singhal et al., arXiv:2305.09617 |
| Human experts | 78.0% | — | Jin et al., EMNLP 2019 |
| GPT-4 | 75.2% | Direct | Nori et al., arXiv:2303.13375 |
| GPT-3.5 | 74.4% | Direct | Nori et al., arXiv:2303.13375 |
| **MedAgent (gpt-oss-20b, RAG)** | **45.0%** | **RAG** | **This work** |
| **MedAgent (qwen3.8-27b, RAG)** | **5.0%** | **RAG** | **This work — see note** |

### Methodology note

PubMedQA is a *reading comprehension* benchmark — each question comes with a specific PubMed abstract as context, and the label reflects what *that abstract* concludes. All published baselines run in direct mode: they read the provided abstract and answer accordingly.

Our RAG agent searches PubMed independently and synthesizes evidence from different papers, which may reach different conclusions than the single labeled abstract. This creates a systematic mismatch.

**"Maybe" bias by model**: gpt-oss-20b predicted "maybe" for 8/20 questions; qwen3.8-27b predicted "maybe" for 18/20. Both models hedge because the broader medical literature is genuinely uncertain on many of these questions — but PubMedQA labels rarely use "maybe" (only 1/20 in this set). qwen's extreme hedging behaviour collapses its score to near-zero and makes the 5% figure uninformative as a performance metric.

The scores here are **not directly comparable to the published baselines** — different methodology (free-form evidence synthesis vs reading comprehension from a provided abstract). PubMedQA in direct mode would be the apples-to-apples comparison.

---

## Part 5 — Multi-Model Comparison (MedQA-USMLE)

**Benchmark**: MedQA-USMLE | **Subset**: 20 questions | **Mode**: Direct (no RAG) | **Provider**: Groq

### Per-question results — qwen/qwen3.8-27b

| # | Correct | Direct | RAG | Question topic |
|---|---------|--------|-----|----------------|
| 1 | B | ✅ B | ❌ A | Ethics / disclosure |
| 2 | D | ❌ C | ✅ D | TCC / cisplatin mechanism |
| 3 | B | ✅ B | ✅ B | Cholesterol embolism post-cath |
| 4 | D | ❌ B | ❌ B | Bacteriology / gram-negative coccobacilli |
| 5 | B | ✅ B | ✅ B | Allergic conjunctivitis / ketotifen |
| 6 | D | ❌ B | ❌ B | Cocaine chest pain |
| 7 | C | ✅ C | ✅ C | Right flank pain / iliac aneurysm |
| 8 | C | ✅ C | ✅ C | Post-MI antiplatelet / clopidogrel |
| 9 | B | ✅ B | ✅ B | IUD contraindication (PID) |
| 10 | A | ❌ B | ✅ A | Nail pitting / psoriasis |
| 11 | D | ✅ D | ✅ D | HIV confirmatory test |
| 12 | D | ✅ D | ✅ D | Myelofibrosis / ruxolitinib |
| 13 | B | ✅ B | ✅ B | NF2 / merlin / schwannomas |
| 14 | D | ❌ A | ✅ D | Executive check-up / standing reflex |
| 15 | C | ✅ C | ✅ C | Virus reassortment / rotavirus |
| 16 | B | ✅ B | ✅ B | Overweight urgent care / gallbladder |
| 17 | D | ✅ D | ✅ D | IL-4 / IgE class switching / asthma |
| 18 | D | ✅ D | ✅ D | Case-control / matching |
| 19 | B | ✅ B | ✅ B | Acute pericarditis |
| 20 | D | ✅ D | ❌ B | Altered mental status |

**Direct: 75.0% (15/20) | RAG: 80.0% (16/20)**

### Full 4-run comparison (all questions)

| # | Question topic | gpt-oss-20b direct | gpt-oss-20b RAG | qwen direct | qwen RAG |
|---|----------------|--------------------|-----------------|-------------|----------|
| 1 | Ethics / disclosure | ❌ | ❌ | ✅ | ❌ |
| 2 | TCC / cisplatin | ✅ | ❌ | ❌ | ✅ |
| 3 | Cholesterol embolism | ✅ | ✅ | ✅ | ✅ |
| 4 | Bacteriology | ✅ | ✅ | ❌ | ❌ |
| 5 | Allergic conjunctivitis | ✅ | ✅ | ✅ | ✅ |
| 6 | Cocaine chest pain | ❌ | ❌ | ❌ | ❌ |
| 7 | Iliac aneurysm | ⚠️ | ✅ | ✅ | ✅ |
| 8 | Post-MI antiplatelet | ✅ | ✅ | ✅ | ✅ |
| 9 | IUD contraindication | ✅ | ✅ | ✅ | ✅ |
| 10 | Nail pitting / psoriasis | ✅ | ✅ | ❌ | ✅ |
| 11 | HIV confirmatory test | ✅ | ✅ | ✅ | ✅ |
| 12 | Myelofibrosis / ruxolitinib | ✅ | ✅ | ✅ | ✅ |
| 13 | NF2 / schwannomas | ✅ | ✅ | ✅ | ✅ |
| 14 | Executive check-up | ✅ | ✅ | ❌ | ✅ |
| 15 | Virus reassortment | ✅ | ✅ | ✅ | ✅ |
| 16 | Overweight urgent care | ❌ | ❌ | ✅ | ✅ |
| 17 | IL-4 / IgE / asthma | ✅ | ✅ | ✅ | ✅ |
| 18 | 3-month-old / matching | ❌ | ✅ | ✅ | ✅ |
| 19 | Acute pericarditis | ✅ | ✅ | ✅ | ✅ |
| 20 | Altered mental status | ❌ | ✅ | ✅ | ❌ |
| | **Total** | **14/20 (70%)** | **16/20 (80%)** | **15/20 (75%)** | **16/20 (80%)** |

### Headline comparison vs published baselines

| Model | MedQA Accuracy | Mode | Source |
|-------|----------------|------|--------|
| Med-Gemini | 91.1% | Fine-tuned | Saab et al., arXiv:2404.18416 |
| GPT-4 | 87.0% | Direct | Nori et al., arXiv:2303.13375 |
| Med-PaLM 2 | 86.5% | Direct | Singhal et al., arXiv:2305.09617 |
| **gpt-oss-20b + RAG (this work)** | **80.0%** | RAG | This work |
| **qwen3.8-27b + RAG (this work)** | **80.0%** | RAG | This work |
| **qwen3.8-27b (this work)** | **75.0%** | Direct | This work |
| **gpt-oss-20b (this work)** | **70.0%** | Direct | This work |
| GPT-3.5 | 57.0% | Direct | Nori et al., arXiv:2303.13375 |
| USMLE passing threshold | ~60% | — | Official NBME |

### Observations

- **Both models reach 80% with RAG**, regardless of their different direct-mode baselines (70% vs 75%). RAG acts as an equalizer — it benefits the weaker direct model more (+10 pp for gpt-oss-20b vs +5 pp for qwen).
- **Q6 (cocaine/labetalol) is the only question all 4 runs fail.** This is the hardest question in the set: it requires knowing that beta-blockers are specifically contraindicated with cocaine (despite labetalol's alpha-blockade making it plausible), a high-specificity USMLE fact not well-surfaced by PubMed retrieval.
- **Models complement each other**: the two direct runs disagree on 7 questions and each gets some right that the other misses, suggesting an ensemble would outperform either alone.
- **Both exceed USMLE passing threshold (60%)** with zero medical fine-tuning.
- **~7–17% gap vs GPT-4** is expected at this model scale; fine-tuned specialist models (Med-Gemini, Med-PaLM 2) close the gap but require proprietary training data.
- **High-variance caveat**: 20-question subsets have 95% CI ≈ ±10%, so results are directional.

---

## Part 6 — Benchmark Summary

| Benchmark | Model | Mode | Accuracy |
|-----------|-------|------|---------|
| Mini-set qualitative (10 Qs) | gpt-oss-20b | RAG | **10/10** |
| MedQA-USMLE (20 Qs) | gpt-oss-20b | Direct | **70.0%** |
| MedQA-USMLE (20 Qs) | gpt-oss-20b | RAG | **80.0%** (+10 pp) |
| MedQA-USMLE (20 Qs) | qwen/qwen3.8-27b | Direct | **75.0%** |
| MedQA-USMLE (20 Qs) | qwen/qwen3.8-27b | RAG | **80.0%** (+5 pp) |
| PubMedQA (20 Qs) | gpt-oss-20b | RAG | **45.0%** (see methodology note) |
| PubMedQA (20 Qs) | qwen/qwen3.8-27b | RAG | **5.0%** (extreme "maybe" bias — uninformative) |

### Key findings

1. **RAG adds +10 pp on MedQA**: The full agent pipeline (PubMed search + synthesis) raises accuracy from 70% to 80% vs direct model knowledge alone.
2. **70% beats GPT-3.5 (57%) and the USMLE passing threshold (60%)** using a free-tier 20B model with zero medical fine-tuning.
3. **~17% gap vs GPT-4**: expected given model size difference; specialist fine-tuned models (Med-Gemini, Med-PaLM 2) close this gap but require proprietary training data.
4. **PubMedQA methodology mismatch**: the RAG agent's 45% reflects a harder task than what baselines measure — free-form evidence synthesis vs reading comprehension from a provided abstract.
5. **High-variance caveat**: with 20-question subsets, 95% CI is roughly ±10%, so results should be interpreted as directional rather than precise.
