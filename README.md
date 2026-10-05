# Job-Applyer

Personal-use job discovery and application preparation system focused on official company career sources.

## Workflow

1. Read a configured list of official company career pages.
2. Crawl candidate job links within the company's allowed domains.
3. Extract job facts with an NVIDIA hosted LLM.
4. Deduplicate jobs in a local SQLite database.
5. Analyze and match every eligible job against the candidate profile.
6. Create a new tailored resume for each job.
7. Create a job-specific cover letter for each job.
8. Record the exact resume and cover-letter files used for each application.
9. Keep final submission human-confirmed and never bypass CAPTCHA, MFA, OTP or anti-bot controls.

There is intentionally no 10-job application cap. Set APPLY_TO_ALL_ELIGIBLE=true to process every eligible job.

## NVIDIA API

The application uses one NVIDIA_API_KEY with NVIDIA's OpenAI-compatible chat endpoint:
https://integrate.api.nvidia.com/v1/chat/completions

Default stage mapping:

    extract       -> openai/gpt-oss-20b
    analyze       -> nvidia/nemotron-3-super-120b-a12b
    match         -> openai/gpt-oss-20b
    resume        -> openai/gpt-oss-120b
    cover_letter  -> openai/gpt-oss-20b
    form          -> openai/gpt-oss-20b
    fallback      -> deepseek-ai/deepseek-v4-flash

All model IDs are configurable in .env.

## Official-source policy

A job is accepted only when its source URL and application URL pass the configured company-domain allowlist. The system is not designed to scrape LinkedIn, Indeed, Naukri, Glassdoor or other job aggregators.

For a company that uses a third-party ATS, add that ATS host to the company's allowed_domains only when it is the company's official hiring endpoint.

Copy the source template:

    cp config/company_sources.example.json config/company_sources.json

Then add your target companies and their official career URLs.

## Local setup

Create and activate a virtual environment, then install:

    pip install -r requirements.txt
    playwright install

Copy .env.example to .env and set NVIDIA_API_KEY.

Create your local private files:

    private/master_resume.txt
    private/profile.json

Initialize the database:

    python main.py init-db

Show configured AI models:

    python main.py models

Discover official-company jobs:

    python main.py discover

Prepare every eligible job with a fresh customized resume and cover letter:

    python main.py prepare

Run the browser application flow for every eligible job:

    python main.py apply

For each application, the browser fills ordinary fields when they can be mapped safely, then pauses and requires you to type SUBMIT or SKIP. CAPTCHA, MFA, OTP, legal declarations and other human-only controls are never bypassed.

## Truthfulness and safety

- Personal use only.
- Never fabricate candidate qualifications.
- Never bypass CAPTCHA, MFA/OTP, authentication barriers or anti-bot controls.
- Stop for human-only questions or legal declarations.
- Respect site terms, rate limits and applicable laws.


## ATS resume generation

Each eligible job gets a separate ATS-oriented DOCX resume. The generator uses a single-column layout, standard section headings, Arial typography, simple bullets, and no tables, graphics, icons, sidebars, text boxes or multi-column formatting.

The resume model first tailors the content to the specific job description, responsibilities, required skills and preferred skills. A second NVIDIA model validates the draft against the master resume and reports unsupported claims and ATS issues. When validation fails, the draft is corrected once before the DOCX is written.

The master resume remains the factual source of truth. The system may reorder and rewrite supported facts for relevance but does not add unsupported qualifications, experience, education, certifications, dates, employers, achievements or metrics.
