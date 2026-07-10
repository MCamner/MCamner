# Security and public-data policy

These repositories are public portfolio and tooling projects.

Do not commit:

- customer or patient data
- credentials, tokens, or private keys
- internal hostnames or endpoint details
- production diagnostics or unsanitized exports
- personal notes or confidential decision records

Automation that can affect endpoints, repositories, or infrastructure should use explicit allowlists, review gates, and inspectable logs. Public examples must use synthetic or sanitized data.

[Back to profile](../README.md)
