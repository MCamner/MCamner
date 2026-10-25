# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Add a schema-versioned v2 loopback server, capability-aware collection, and
  explicit collection errors. Keep v1 available for its existing page.
- Validate v2 source payloads before evaluation; distinguish missing evidence
  and unsupported collection from observed failures. Reject malformed versions
  and stop treating keychain metadata as certificate expiry.
- Show data source and freshness; add local JSON report import, masked JSON and
  standalone HTML export, and a support summary with clipboard fallback.
- Test v2 helper endpoints, evaluation, profiles, and report round trips in CI.

### Changed

* Restore `mq-hal` to the profile ecosystem table and describe it as the
  operator layer it is today, not only a command router.

## [0.1.0] - 2026-05-04

### Added

* Initial release setup
