"""
Internal mini evaluation set: 10 medical questions with reference answers.
Used for qualitative evaluation of the agent.
"""

MINI_SET = [
    {
        "id": "Q01",
        "question": "What is the first-line pharmacological treatment for type 2 diabetes mellitus according to current guidelines?",
        "reference_answer": "Metformin is the first-line pharmacological treatment for type 2 diabetes, unless contraindicated (e.g., eGFR < 30). Recent guidelines also recommend SGLT-2 inhibitors or GLP-1 agonists as first-line when there is established cardiovascular disease, heart failure, or chronic kidney disease.",
        "category": "Pharmacology",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q02",
        "question": "What are the diagnostic criteria for sepsis according to the Sepsis-3 definition?",
        "reference_answer": "Sepsis-3 (2016) defines sepsis as life-threatening organ dysfunction caused by a dysregulated host response to infection. Clinically identified by an acute change in SOFA score ≥2. Septic shock is defined by vasopressor requirement to maintain MAP ≥65 mmHg and serum lactate >2 mmol/L despite adequate fluid resuscitation.",
        "category": "Critical Care",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q03",
        "question": "What is the recommended antibiotic regimen for community-acquired pneumonia in a hospitalized non-ICU patient?",
        "reference_answer": "For non-ICU hospitalized CAP: combination of a beta-lactam (ampicillin-sulbactam, cefotaxime, or ceftriaxone) plus a macrolide (azithromycin or clarithromycin), OR monotherapy with a respiratory fluoroquinolone (levofloxacin or moxifloxacin). Per IDSA/ATS guidelines.",
        "category": "Infectious Disease",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q04",
        "question": "What is the mechanism of action of direct oral anticoagulants (DOACs) and when are they preferred over warfarin?",
        "reference_answer": "DOACs include: Factor Xa inhibitors (rivaroxaban, apixaban, edoxaban) and direct thrombin inhibitors (dabigatran). They are preferred over warfarin for non-valvular AF, VTE treatment/prophylaxis due to predictable pharmacokinetics, fewer drug interactions, no monitoring required. Warfarin remains preferred for mechanical heart valves and severe renal impairment.",
        "category": "Cardiology/Hematology",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q05",
        "question": "What are the current recommendations for colorectal cancer screening in average-risk adults?",
        "reference_answer": "USPSTF (2021) recommends CRC screening for adults 45-75 years. Options include: colonoscopy every 10 years, annual high-sensitivity FOBT or FIT, CT colonography every 5 years, flexible sigmoidoscopy every 5 years, or stool DNA test (Cologuard) every 1-3 years. Individualized decision for ages 76-85.",
        "category": "Oncology/Screening",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q06",
        "question": "What is the evidence for using corticosteroids in COVID-19 patients requiring oxygen supplementation?",
        "reference_answer": "The RECOVERY trial (NEJM 2021) demonstrated that dexamethasone 6mg/day for 10 days reduced 28-day mortality in patients requiring oxygen (RR 0.83) or mechanical ventilation (RR 0.64), but showed possible harm in those not requiring oxygen. WHO and most guidelines recommend dexamethasone for severe/critical COVID-19.",
        "category": "Infectious Disease/COVID-19",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q07",
        "question": "How should hypertensive urgency (BP > 180/110 without end-organ damage) be managed?",
        "reference_answer": "Hypertensive urgency does not require immediate IV therapy or hospitalization. Oral antihypertensives (captopril, clonidine, labetalol, or amlodipine) can be used to gradually reduce BP over 24-48 hours. Abrupt reduction can cause ischemia. Outpatient follow-up within 1-7 days is appropriate. Distinguish from hypertensive emergency (with end-organ damage) requiring IV therapy.",
        "category": "Cardiology",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q08",
        "question": "What is the evidence for aspirin use in primary prevention of cardiovascular events?",
        "reference_answer": "Recent large RCTs (ARRIVE, ASPREE, ASCEND) and 2022 USPSTF guidelines indicate aspirin for primary CVD prevention provides marginal benefit with increased bleeding risk, particularly in older adults (≥60). USPSTF now recommends against initiating aspirin for primary prevention in adults ≥60. For ages 40-59 with ≥10% 10-year CVD risk, shared decision-making is recommended.",
        "category": "Cardiology/Prevention",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q09",
        "question": "What are the diagnostic criteria and management of Clostridioides difficile infection?",
        "reference_answer": "CDI diagnosis: diarrhea (≥3 loose stools/24h) plus positive stool test (NAAT or EIA for toxin). Treatment: for non-severe CDI — oral vancomycin 125mg QID x 10 days OR fidaxomicin 200mg BID x 10 days (preferred to reduce recurrence). Metronidazole is now second-line. For fulminant CDI: vancomycin 500mg QID ± metronidazole IV. Per IDSA 2021 guidelines.",
        "category": "Infectious Disease/Gastroenterology",
        "expected_tools": ["search_pubmed"],
    },
    {
        "id": "Q10",
        "question": "What is the recommended approach to pain management in acute pancreatitis?",
        "reference_answer": "IV opioids (hydromorphone or morphine) are the standard for moderate-severe pain in acute pancreatitis — evidence does not support the old concern about morphine causing sphincter of Oddi spasm. Early oral feeding is now preferred over NPO when tolerated. NSAIDs can be used for mild cases. Epidural analgesia may benefit severe cases. Per IAP/APA and ACG guidelines.",
        "category": "Gastroenterology",
        "expected_tools": ["search_pubmed"],
    },
]


def get_mini_set() -> list[dict]:
    return MINI_SET


def get_question_by_id(qid: str) -> dict | None:
    return next((q for q in MINI_SET if q["id"] == qid), None)
