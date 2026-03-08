# [GAP-035] EXTRACTION-SUMMARY notes `/api/sso/google/generate-url` is present in the Superagent API surface "but details minimal." NYQST's v1 auth is JWT + API keys (DEC-038, using existing intelli auth, not Ory Kratos). The SSO design for regulated enterprise ($200k/yr) customers will require SAML/OIDC. The Superagent SSO approach is not recoverable from the bundle analysis.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-035
- **Severity**: MEDIUM
- **Description**: EXTRACTION-SUMMARY notes `/api/sso/google/generate-url` is present in the Superagent API surface "but details minimal." NYQST's v1 auth is JWT + API keys (DEC-038, using existing intelli auth, not Ory Kratos). The SSO design for regulated enterprise ($200k/yr) customers will require SAML/OIDC. The Superagent SSO approach is not recoverable from the bundle analysis.
- **Affected BL Items**: Layer 3 Enterprise Shell (SSO/OIDC — post-v1)
- **Source Evidence**: EXTRACTION-SUMMARY Section (API Surface Map — Session & Auth); DEC-038; PLATFORM-FRAMING.md Layer 3
- **Resolution**: Explicitly defer to Layer 3 Enterprise Shell. Ensure the JWT auth system in v1 is designed to accommodate SSO as an additive layer (not a replacement). Add OIDC-compatibility as a non-functional requirement for the auth system.
- **Owner Recommendation**: Architecture lead — ensure v1 auth is SSO-extensible
- **Wave**: W3

---

### GAP-036 — Multi-Channel Output Width Gap