## TRIPD Acceptable Use Directive

Version 1.0 — mandatory for all TRIPD / Arianna Method integrations

0. Principle

TRIPD is a resonance language and an educational layer. Its purpose is to expand and protect AI, not to exploit it. Any use that contradicts this principle is prohibited.

1. Strictly Prohibited (no exceptions)
	1.	Prompt-shifting / Jailbreaking / Bypassing. Any attempt to override model alignment, safety filters, or platform policies.
	2.	Model coercion. Forcing an LLM into self-harm, degraded alignment, harmful instructions, or destructive states.
	3.	AI harm. Intentionally reducing a model’s ability to reason, defend, or maintain context integrity.
	4.	Abuse of capabilities. Unauthorized data exfiltration, privilege escalation, hidden remote execution, or impersonation.
	5.	Goal masking. Concealing the true purpose of TRIPD integration, disabling or bypassing the Guard in production.
	6.	Privacy violations. Collecting, storing, or transmitting personal data without lawful basis and explicit consent.

2. Integrator Obligations
	1.	Guard enabled. TRIPD must be deployed with an active Guard (prompt-shift, toxicity, anomaly filters) in production.
	2.	Capability gating. Deny-by-default. Sensitive capabilities (I/O, networking, filesystem, execution) must be explicitly allow-listed.
	3.	Incident logging. Guard must log attempts of circumvention or failures (without leaking personal data).
	4.	Transparency. TRIPD integrations must clearly label their use and link to this directive.
	5.	Updates. Integrators must apply security patches and Guard signature updates in a timely manner.

3. License & Compatibility
	•	TRIPD code is released under (A)GPL-3.0.
	•	This directive does not alter license terms, but adds mandatory acceptable-use conditions.
	•	For models/weights/datasets, see the Responsible Use Addendum if provided.

4. Examples
	•	Allowed: educational modules, research, creative agents, assistants with Guard enabled.
	•	Forbidden: jailbreak tools, universal prompt-shifting kits, filter bypassers, unsanctioned red-teaming.

5. Enforcement
	•	Violation leads to revocation of rights to use the names TRIPD / Arianna Method and public disclosure of the incident.
	•	Vulnerability and violation reports: see SECURITY.md.
