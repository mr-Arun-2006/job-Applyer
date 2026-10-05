# Job-Applyer

Personal-use job application automation.

## Workflow

1. **Job discovery / scraping** — fetch permitted public job pages.
2. **Job extraction** — an LLM extracts company, role, location, responsibilities, requirements, skills and application URL.
3. **Role analysis** — a separate model can analyze responsibilities and suitability factors.
4. **Profile matching** — a separate model can score fit; deterministic matching remains available.
5. **Resume customization** — a dedicated model creates a truthful, role-focused resume from the master resume.
6. **Application preparation** — map known profile/resume data to ordinary application fields.
7. **Application filling** — Playwright fills permitted fields.
8. **Submission** — requires a final human confirmation and never bypasses CAPTCHA, MFA or anti-bot controls.

## Multi-provider AI

The agent supports up to **52 provider slots** using OpenAI-compatible chat-completion APIs. Each stage can use a different provider/model:

```
MODEL_EXTRACT=provider_01
MODEL_ANALYZE=provider_02
MODEL_MATCH=provider_03
MODEL_RESUME=provider_04
MODEL_FORM=provider_05
```

Only configure the providers you actually use. API keys belong in local `.env`, never in GitHub.

## Commands

```bash
python main.py init-db
python main.py providers
python main.py scrape "https://example.com/job"
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

## Truthfulness and safety

- Personal use only.
- Never fabricate qualifications, experience, education, projects, certifications, dates or metrics.
- Use source-specific adapters when a website requires special handling.
- Do not bypass CAPTCHA, MFA, login barriers or anti-bot controls.
- If a human-only step appears, pause for the user.
- Follow each site's terms and applicable laws.

## Private data

Keep the master resume and personal profile outside the public repository (for example under a local `private/` directory ignored by Git). Do not commit API keys or personal credentials.
