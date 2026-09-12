# Safety Scan Checklist

Run this checklist before making a repository public, featuring it on LinkedIn, or adding it to a pinned-project batch.

## Search Terms

Search source files, configuration, documentation, examples, scripts, commit history where appropriate, issues, releases, and public links for:

```text
API_KEY
OPENAI_API_KEY
GEMINI_API_KEY
GH_TOKEN
GITHUB_TOKEN
PASSWORD
SECRET
.env
client_secret
private_key
patient
OP number
insurance
Saada
doctor schedule
pricing
WhatsApp
proposal
contract
```

## Review Steps

- Confirm no credentials, tokens, private keys, or real environment files are committed.
- Confirm examples use synthetic or public data only.
- Confirm patient, insurance, OP number, doctor schedule, and hospital-internal data are absent.
- Confirm corporate contact data, pricing, proposals, contracts, and WhatsApp exports are absent.
- Review generated screenshots, logs, fixtures, notebooks, and sample payloads.
- Check documentation and comments for unsupported production, clinical, customer, or compliance claims.
- Verify README commands, technology names, test claims, and deployment claims.
- Check issue templates, CI output references, release assets, and external links.
- Remove or replace sensitive material, rotate exposed credentials, and review Git history when a secret was committed.
- Record the risk category and remediation owner before public promotion.

## Sensitive Findings Rule

If sensitive material is found, do not print secrets or sensitive values. Only describe the risk category and recommend remediation.

## Promotion Decision

- [ ] Scan completed
- [ ] Findings remediated or explicitly accepted
- [ ] README status label is accurate
- [ ] Public links reviewed
- [ ] Repository owner approved promotion