# Security

Version 0.1.x is the currently maintained source release. These tools read local
untrusted exports and never execute their content or send network requests at runtime.
Input limits reduce exposure but are not a sandbox; use an isolated process for unknown files.
Report vulnerabilities through GitHub private vulnerability reporting when available,
or a sanitized issue without exploit payloads, secrets or private data. Do not assume
private reporting has been enabled. The CLI output may retain identifiers appropriate
to its workflow; review before sharing.

No runtime third-party dependencies. The build toolchain remains a dependency and
must be audited independently. Updates are reviewed under ordinary repository protections.
