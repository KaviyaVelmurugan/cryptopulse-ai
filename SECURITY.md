# Security policy

## Supported version

Security fixes are applied to the latest code on `main`. CryptoPulse AI is currently a local
research demonstration and must not be treated as an exchange, custodian, or investment service.

## Reporting a vulnerability

Do not include credentials, personal information, proprietary news content, or exploit details in
a public issue. Use GitHub's private vulnerability-reporting feature when it is enabled for the
repository. Otherwise, contact the repository owner privately before public disclosure.

Include the affected component, reproduction conditions, impact, and a safe proof of concept. The
maintainer should acknowledge a report within seven days and coordinate disclosure after a fix is
available.

## Operational boundaries

- Never commit API keys or `.env` files.
- Use explicit CORS origins in production; wildcard origins fail configuration validation.
- Containers run as non-root users with read-only filesystems in the supplied Compose file.
- The API is read-only and v1.0 has no authentication because it exposes only local derived demo
  reports. Authentication is required before exposing private or user-specific data.
- Do not add exchange credentials or trade-execution permissions to v1.0.
