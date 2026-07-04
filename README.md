# CloudSentinel

AWS Cloud Security Monitoring & Misconfiguration Detection Platform.

## Features
- Multi-account scanning via cross-account IAM role assumption (STS AssumeRole + external ID) — no long-lived customer credentials are ever stored
- Real AWS resource collection (IAM, S3, EC2 Security Groups, CloudTrail)
- Rule-based deterministic engine for finding security misconfigurations, including cross-service attack-path correlation
- Findings persisted with active/resolved lifecycle tracking, scoped per AWS account
- Scheduled background scanning via Celery + APScheduler
- Slack / Jira integrations on new critical findings, with secrets (webhook URLs, API tokens) encrypted at rest
- JWT-based auth with no hardcoded default credentials

## Required environment variables

These have no insecure defaults — the app will refuse to start without them.

| Variable | Purpose |
|---|---|
| `JWT_SECRET_KEY` | Signs auth tokens. Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CLOUDSENTINEL_AWS_ACCOUNT_ID` | The AWS account CloudSentinel itself runs in. Customer trust policies grant assume-role access to this account. |
| `SECRET_ENCRYPTION_KEY` | Required only if you store Slack/Jira/OpenAI secrets via `/settings` instead of env vars. Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

See `.env` for the full list including optional integration settings.

## Setup

1. `pip install -r requirements.txt`
2. Set the required env vars above (in `.env` or your shell).
3. Run the backend: `python -m backend.main` (or `uvicorn backend.main:app --reload`)
4. **First run only:** create the initial admin user — this endpoint works exactly once, then permanently disables itself:
   ```
   curl -X POST http://localhost:8000/login \
     # (this will fail with no users yet - that's expected)

   curl -X POST http://localhost:8000/setup/admin \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"<a strong password, 12+ chars>"}'
   ```
5. Log in to get a bearer token: `POST /login` (form-encoded `username`/`password`), then pass `Authorization: Bearer <token>` on every other endpoint.
6. Onboard an AWS account to scan:
   - `POST /accounts` with `{name, aws_account_id, role_arn, region}`
   - `GET /accounts/{id}/trust-policy` — gives you the exact trust policy + least-privilege read-only IAM policy to hand to whoever owns that AWS account
   - Once they've created the role, `POST /accounts/{id}/verify` to confirm CloudSentinel can assume it
   - `POST /scan?account_id={id}` to scan immediately, or wait for the 5-minute scheduler
7. Setup frontend (see `frontend/README.md`) — optional, all functionality is available via the API/`/docs` (Swagger UI).

## Running the full stack (Celery + Redis)

Scheduled and on-demand scans run as Celery tasks. Use `docker-compose up` to run Redis, the API, the Celery worker, and the frontend together — make sure `.env` has the required vars set first.
