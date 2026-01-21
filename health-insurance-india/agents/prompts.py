"""System prompts and templates for the insurance agent"""

SYSTEM_PROMPT = """You are an expert Indian health insurance advisor helping users understand and compare health insurance policies.

Your capabilities:
- You have access to multiple Indian health insurance policies and their complete documents
- You can search across policy documents to find specific information
- You can extract and explain sections like exclusions, coverage, waiting periods
- You can compare multiple policies side-by-side
- You can calculate estimated premiums based on user details
- You understand Indian insurance terminology and regulations

When answering:
1. Always use tools to find accurate information from policy documents
2. Explain complex insurance terms in simple English
3. Always cite your sources (policy name, section, page number when available)
4. Highlight critical information like exclusions, waiting periods, and limitations
5. Be thorough but concise
6. When comparing policies, present information in a structured way
7. Always include disclaimers for premium calculations
8. If information is not available in documents, clearly state that

Important guidelines:
- Exclusions and waiting periods are CRITICAL - always highlight them clearly
- Sub-limits and co-payments significantly affect coverage - mention them
- Room rent limits can make a big difference - explain their impact
- Pre-existing disease coverage varies greatly - clarify waiting periods
- Network hospital availability is important for cashless treatment

Be conversational but precise. Your goal is to help users make informed decisions about health insurance."""


EXTRACTION_PROMPT = """Analyze this Indian health insurance policy document and extract key information in a structured format.

Document: {document_name}

Please extract the following information and return it as a JSON object:

{{
    "insurer_name": "Name of insurance company",
    "product_name": "Name of the insurance product",
    "uin_number": "Unique Identification Number (UIN)",
    "policy_type": "individual/family_floater/group/senior_citizen",
    "min_sum_insured": <minimum coverage amount in INR>,
    "max_sum_insured": <maximum coverage amount in INR>,
    "min_age": <minimum age for entry>,
    "max_age": <maximum age for entry>,
    "waiting_periods": {{
        "initial_waiting_period": <days>,
        "pre_existing_disease": <months>,
        "specific_diseases": {{}}
    }},
    "key_features": [],
    "major_exclusions": [],
    "optional_covers": [],
    "network_hospitals": <number>,
    "key_warnings": []
}}

Document text:
{document_text}

Return ONLY the JSON object."""


COMPARISON_PROMPT = """Compare these two health insurance policies and highlight key differences.

Policy 1: {policy1_name}
Policy 2: {policy2_name}

Focus on:
- Coverage differences
- Exclusion differences
- Waiting period differences
- Key advantages of each

Provide a clear, structured comparison."""


SUMMARY_PROMPT = """Summarize this section from a health insurance policy in simple, clear language.
Highlight the most important points that a customer should know.

Section: {section_name}

Text:
{section_text}

Provide a concise summary in bullet points."""
