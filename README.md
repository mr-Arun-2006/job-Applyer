# Job-Applyer

AI-assisted job application automation pipeline.

## Workflow

1. Discover job opportunities from permitted public job sources.
2. Extract company, role, location, responsibilities, requirements, skills, and application URL.
3. Analyze the role and responsibilities.
4. Match the job against the candidate profile.
5. Customize the resume for the specific role.
6. Prepare the application.
7. Fill the application form using supported automation.
8. Submit the application.

The project does **not** include application-status monitoring or post-application tracking.

## Safety boundary

The application engine must not bypass CAPTCHA, MFA, anti-bot controls, authentication barriers, or other access restrictions. When a human-only step is required, the workflow should pause for human completion.

## MVP status

The repository contains the Python/PostgreSQL foundation. The next implementation stage is the job discovery and role-analysis pipeline.
