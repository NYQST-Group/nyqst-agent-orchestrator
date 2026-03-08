# [GAP-029] DEC-036 specifies "port working Stripe code from okestraai/DocuIntelli." The billing-metering-extract.md Section 10 provides a detailed port strategy (what to take, what to redesign, porting steps). However, the DocuIntelli codebase has not been inspected to verify: (1) that it uses raw body for webhook signature verification (the critical LIB-08 gotcha); (2) that its subscription model matches the NYQST schema; (3) that it doesn't have equivalent bugs to the arq worker initialization issue found in NYQST. The port plan assumes the source code is correct.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-029
- **Severity**: MEDIUM
- **Description**: DEC-036 specifies "port working Stripe code from okestraai/DocuIntelli." The billing-metering-extract.md Section 10 provides a detailed port strategy (what to take, what to redesign, porting steps). However, the DocuIntelli codebase has not been inspected to verify: (1) that it uses raw body for webhook signature verification (the critical LIB-08 gotcha); (2) that its subscription model matches the NYQST schema; (3) that it doesn't have equivalent bugs to the arq worker initialization issue found in NYQST. The port plan assumes the source code is correct.
- **Affected BL Items**: BL-012 (billing), BL-013 (quota enforcement)
- **Source Evidence**: billing-metering-extract.md Section 10; DEC-036; LIB-08 gotcha
- **Resolution**: Inspect `okestraai/DocuIntelli` billing code before porting. Specifically verify: (a) raw body usage in webhook handler; (b) subscription schema compatibility; (c) no initialization-order bugs; (d) the Stripe SDK version (must be v11+ for the `StripeClient` API used in billing-metering-extract.md).
- **Owner Recommendation**: Backend track lead (BL-012 owner)
- **Wave**: W0 — before BL-012 implementation begins

---

### GAP-030 — Feature Flag Backend Not Specified for v1