# Aurelius — Privacy Policy

Effective Date: 2025-09-28  
Version: 1.1

This Privacy Policy ("Policy") describes how the Aurelius Discord Bot (the "Bot", "we", "us") collects, uses, discloses, and protects limited information in the course of providing Bot functionality. We design the Bot to operate with minimal data collection. We do not sell personal information and we do not build marketing profiles.

By inviting or using the Bot you acknowledge and agree to the practices described in this Policy. If you disagree, remove the Bot from your Discord server ("Server").

## 1. Summary / High‑Level Overview
- We collect only the minimum Server‑level configuration and operational data needed to deliver features (alerts, lookups, logging).  
- We do not permanently store routine user message content or full user chat history; command inputs are processed transiently in memory except where required for operational integrity or abuse prevention.  
- We do not sell or rent data.  
- We retain operational logs for short, defined periods.  
- Removal of the Bot or a verified deletion request triggers deletion of persistent Server configuration data (subject to security/legal holds).

## 2. Data Categories We Collect
We focus on Server‑scoped data instead of per‑user personal profiling.

### 2.1 Core Configuration Data
- Server (guild) ID and (optionally cached) name.  
- Channel IDs relevant for alert posting (if configured).  
- Alert/watch settings: ticker symbols, thresholds (e.g., price targets), alert type, active/inactive status, timestamps of creation or last update.  
- Internal references linking alerts to the originating Server.

### 2.2 Transient Interaction Data
- Command invocations (e.g., the content after the command prefix, user ID, and channel ID) processed in memory to produce a response. We do not persist full command text beyond ephemeral logs (see 2.4) unless needed to enforce rate limits or mitigate abuse.  
- User IDs may appear temporarily in runtime memory strictly for permission checks, throttle logic, or formatting responses.

### 2.3 Derived / Computed Data
- Internal flags or counters (e.g., number of active alerts) for performance optimization.  
- Aggregated metrics (non‑identifying) about feature usage (e.g., count of lookups performed) that do not store raw identifiers once aggregated.

### 2.4 Operational & Diagnostic Logs
- Timestamps, Server IDs, channel IDs, command alias used, success/error codes, exception traces.  
- Minimal truncated snippets of command arguments may appear in error or debug logs solely to troubleshoot malfunctions. We aim to avoid storing full message bodies.  
- IP addresses are generally not collected directly by the Bot; hosting infrastructure may generate standard access or system logs (handled by the infrastructure provider under their terms).

### 2.5 Third‑Party Data Retrieval
- We query external market data providers (e.g., Yahoo Finance via yfinance) using ticker strings. We do not send your Server configuration or user identifiers to those data sources beyond ordinary network metadata (e.g., our server’s IP).

### 2.6 Optional Future Premium / Billing (If Implemented)
If paid tiers are introduced, limited billing metadata (e.g., subscription status, plan type, payment processor customer ID) may be stored. We will not store full payment card details; those remain with the payment processor. This subsection will be updated before activation of billing features.

## 3. How We Use Data
We process the above categories strictly for:
1. Delivering core Bot functionality (alerts, market lookups, formatting responses).  
2. Managing alert lifecycle (create, trigger, update, delete).  
3. Preventing abuse, spam, or automated misuse (rate limiting, anomaly detection).  
4. Debugging errors, ensuring reliability, scaling infrastructure.  
5. Securing systems (monitoring suspicious patterns).  
6. Planning roadmap improvements via aggregated, non‑personal usage metrics.

## 4. Legal Bases for Processing (EEA/UK Where Applicable)
- Performance of a contract / fulfillment of requested functionality (core operational processing).  
- Legitimate interests (security, fraud prevention, service improvement, minimal analytics).  
- Compliance with legal obligations (responding to lawful requests).  
- Consent: only where explicitly requested (e.g., optional beta features). If consent is withdrawn, related processing ceases (unless another lawful basis applies).

## 5. Sharing & Disclosure
We do not sell data. We may disclose limited data:
1. Service Providers / Sub‑processors: hosting, database, logging, monitoring platforms under contractual confidentiality / data protection obligations.  
2. Third‑Party Data Sources: we request market data; we do not push Server configuration or user identifiers to them beyond standard technical metadata.  
3. Legal & Safety: to competent authorities if we believe disclosure is necessary to comply with law, protect rights, investigate abuse, or ensure safety.  
4. Business Continuity: if ownership/control changes (e.g., merger, acquisition), data may transfer subject to this Policy or successor protections.  
5. Aggregated / Anonymized Insights: non‑identifying statistics (e.g., number of total alerts system‑wide) that cannot reasonably be used to re‑identify a Server or user.

## 6. Data Retention & Deletion Schedule
| Data Type | Typical Retention | Rationale |
|----------|------------------|-----------|
| Server configuration (IDs, alert settings) | While Bot is installed + up to 30 days after removal | Grace period in case of accidental removal; backup integrity |
| Active alerts & thresholds | Duration of alert + 30 days after deactivation | Auditing triggers & troubleshooting |
| Operational logs (standard) | 14 days (rolling) | Debugging & security for recent incidents |
| Error/exception logs | Up to 30 days (earlier if resolved) | Deep diagnostics |
| Aggregated metrics | Indefinite (non‑identifying) | Long‑term planning, no personal data |
| Backup snapshots (if any) | <= 30 days encrypted | Disaster recovery |
| Potential billing/subscription metadata (future) | While subscription active + required legal period | Accounting/legal compliance |

Retention periods may be extended: (a) for ongoing security investigations, (b) to comply with law, or (c) to resolve disputes. After applicable retention, data is deleted or irreversibly anonymized.

### 6.1 Deletion Requests
Verified Server owners/admins may request deletion of Server configuration data. Provide: (a) Discord Server ID, (b) proof of admin authority. We will respond within a reasonable timeframe (typically <30 days). Removal of the Bot begins the automated cleanup lifecycle. Certain logs may persist until they expire naturally or legal/security holds conclude.

## 7. Security Measures
- Principle of data minimization—store only what's needed for functionality.  
- Segregated configuration vs. transient runtime memory.  
- Access controls limited to maintainers with operational need.  
- Use of transport encryption (HTTPS/TLS) for data in transit to third‑party APIs where supported.  
- Periodic dependency and vulnerability review (subject to open‑source ecosystem constraints).  
NO SYSTEM OR TRANSMISSION METHOD IS 100% SECURE. YOU ASSUME RESIDUAL RISK OF UNAUTHORIZED ACCESS OR LOSS.

## 8. Your Choices & Rights
Depending on jurisdiction, you may have rights to access, correct, delete, restrict, or object to processing of certain data, and data portability. Because we store mostly Server‑scoped configuration, we will primarily liaise with a verified Server owner/admin for such requests.

### Exercising Rights
Contact us (Section 13) with the Server ID and proof of authority. We may request additional verification to prevent unauthorized changes.

### Opt‑Out / Removal
Remove the Bot from the Server to halt future collection. Existing retained data follows the retention schedule.

## 9. Children’s Data
We do not knowingly collect personal data from individuals below Discord’s permitted minimum age or local digital consent age. If you believe we inadvertently processed such data, contact us and we will take reasonable steps to delete it.

## 10. International Data Transfers
Infrastructure may be located in or route through jurisdictions other than yours. Where required and feasible, we rely on appropriate safeguards (e.g., standard contractual clauses or equivalent). By using the Bot you consent to cross‑border transfers to the extent permitted by law.

## 11. Automated Decision Making / Profiling
We do not perform automated decision making producing legal or similarly significant effects on individuals. Basic automated alert triggering or rate limiting does not constitute profiling producing such effects.

## 12. Changes to This Policy
We may update this Policy periodically. The “Effective Date” and “Version” will change accordingly. Substantive changes may be highlighted via repository notes. Continued use after the Effective Date constitutes acceptance.

## 13. Contact / Data Controller
Primary Contact / Controller: Aurelius Bot Team (maintainer)  
Issue Tracker: https://github.com/AlexandreFigueired0/Aurelius/issues  
For rights or deletion requests include: (a) Discord Server ID, (b) brief description of request, (c) proof of admin authority. Do NOT send secrets or tokens.

## 14. Interpretation & Precedence
In case of conflict between this Policy and the Terms of Service, the Terms govern with respect to liability, disclaimers, and definitions, while this Policy governs data handling. Headings are for convenience only.

---
If you do not agree with this Policy, remove the Bot immediately.
