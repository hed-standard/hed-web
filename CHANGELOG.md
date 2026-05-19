# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-19

Initial release -- separation of browser-based validation
from the [hed-javascript](https://github.com/hed-standard/hed-javascript).

### Added

- Browser-based HED validation tools built with React and Vite.
- **Validate dataset** — upload a BIDS dataset folder and check it for HED errors.
- **Validate file** — validate a BIDS-style TSV file against its JSON sidecar.
- Powered by [`hed-validator`](https://www.npmjs.com/package/hed-validator) v4.2.
- CI workflow (GitHub Actions) running tests and build on every push and pull request.

[1.0.0]: https://github.com/hed-standard/hed-web/releases/tag/v1.0.0
