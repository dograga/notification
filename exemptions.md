GCP Security Exemption & Attestation Governance
1. Introduction
The GCP Security Command Center (SCC) Exemption Process provides a formal mechanism for Application Teams to temporarily bypass security findings that cannot be immediately remediated. This framework ensures that all security "silencing" is documented, risk-accepted by leadership, and periodically reviewed to prevent long-term security debt.

1. Findings Ingestion Pipeline (Backend)
The Findings Ingestion Pipeline is an automated backend process designed to ensure that the Service Portal always reflects the most current security posture.

Trigger: A Cloud Scheduler Cron Job runs at set intervals 

Collection: The process executes a service that calls the GCP Security Command Center (SCC) API to pull active findings.

Data Enrichment: The raw finding data is cross-referenced with our CMDB/Internal Registry to append critical organizational context, including AppCode and BU_Code

Storage: The enriched data is saved into Firestore DB, allowing the Service Portal to perform fast, filtered queries based on application ownership.

2. Exemption Request Workflow (Intake)
This workflow handles the initial request when a user identifies an SCC finding in a UAT or Prod environment that requires an exception.
2.1 Process Logic
Access: User navigates to the Service Portal (IDP) and selects the "Request GCP Exemption" service.
Finding Selection: The form dynamically fetches active findings from the GCP SCC API based on the user's environment selection.
ISS Exemption Check:
If True: User provides an existing ISS Exemption ID. The workflow proceeds to standard approvals.
If False: The system flags ISS Approval as a mandatory step.
Approval Chain:
GCP Lead: Validates technical accuracy.
Application Lead: Accepts the business risk.
ISS Lead (Conditional): Conducts a security risk assessment if no prior ID exists.
2.2 Design Diagram (Intake)
(Insert the "GCP SCC Finding Exemption Request Workflow" image here)

3. Attestation & Renewal Workflow (Lifecycle)
All exemptions are time-bound. The Attestation process ensures that every active exemption is re-validated to confirm the risk remains acceptable to the business.
3.1 Step-by-Step Logic
Trigger: A scheduled system job monitors the Exemption Expiry Date.
Notification: Service Portal sends automated "Action Required" notifications to the ISS Lead and Application Lead 30 days prior to expiration.
The Attestation Action: Leads review the finding details in the portal and select one of two outcomes:
Attest/Renew: Leads confirm the risk is still acceptable; the system extends the expiry date.
Revoke: Leads determine the exemption is no longer needed; the system triggers an API call to Un-mute the finding in SCC.
3.2 Design Diagram (Attestation)
(Insert the "Periodic Exemption Attestation" image here)

4. Roles & Responsibilities
Role
Responsibility
Requester
Identifies findings, provides technical justification.
GCP Lead
Ensures the exemption doesn't create cloud-wide risk.
Application Lead
Business owner; signs off on the specific app risk.
ISS (Security)
Governance lead; ensures compliance with security standards.


5. Audit & Compliance
Every action—from the initial request to each periodic attestation—is logged in the Service Portal Audit Trail. This data is available for annual security audits to ensure no findings are silenced without proper visibility.

