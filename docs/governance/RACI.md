# RACI

## Purpose

This RACI defines accountability for governed scanner changes. It does not replace legal, privacy, SOX, ITGC, CISO, CTO, or architecture approval where those approvals are required by an organization.

## Roles

- Product Owner.
- Engineering Maintainer.
- Security Reviewer.
- AppSec Reviewer.
- CISO Approver.
- CTO / Architecture Approver.
- SOX / ITGC Reviewer.
- Legal / Privacy Reviewer.
- Release Manager.

## RACI Matrix

| Activity | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Analyzer changes | Engineering Maintainer | Engineering Maintainer | AppSec Reviewer, Security Reviewer | Product Owner, Release Manager |
| Baseline rule changes | Engineering Maintainer | CISO Approver | AppSec Reviewer, Security Reviewer, CTO / Architecture Approver | Product Owner, Release Manager |
| Custom rule changes | Engineering Maintainer | Product Owner | AppSec Reviewer or domain reviewer | Release Manager |
| Severity changes | Engineering Maintainer | CISO Approver | AppSec Reviewer, Security Reviewer, SOX / ITGC Reviewer where applicable | Product Owner, Release Manager |
| Scoring changes | Engineering Maintainer | CISO Approver | CTO / Architecture Approver, AppSec Reviewer | Product Owner, Release Manager |
| Decision logic changes | Engineering Maintainer | CISO Approver and CTO / Architecture Approver | AppSec Reviewer, SOX / ITGC Reviewer, Legal / Privacy Reviewer where applicable | Product Owner, Release Manager |
| Exception policy changes | Product Owner | CISO Approver | SOX / ITGC Reviewer, Legal / Privacy Reviewer, Engineering Maintainer | Release Manager |
| Validation threshold changes | Engineering Maintainer | CISO Approver | AppSec Reviewer, CTO / Architecture Approver | Product Owner, Release Manager |
| Release approval | Release Manager | Product Owner | Engineering Maintainer, CISO Approver, CTO / Architecture Approver | All reviewers |
| Documentation approval | Product Owner | Product Owner | Engineering Maintainer, domain reviewers | Release Manager |

## Role Notes

- Responsible means the role performs the work.
- Accountable means the role owns the decision.
- Consulted means the role provides input before approval.
- Informed means the role receives the result.

## Escalation

Escalate to CISO, CTO, SOX, ITGC, Legal, or Privacy when a change affects security posture, enterprise acceptance, financial controls, regulated data, legal claims, privacy claims, or final decision semantics.
