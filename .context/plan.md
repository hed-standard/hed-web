# HED web development plan

<!-- PLAN ROTATION POLICY:
  - Only active/in-progress plans belong in "Active Tasks" below.
  - When a plan is fully executed, collapse it to 1-2 summary lines
    under "Completed" (include date and PR/issue number if applicable).
  - Delete detailed steps of completed plans; do not let this file grow
    into an archive. If historical detail is needed, link to the PR or
    issue instead.
  - Review this file at the start of each session; prune anything stale.
-->

## Active tasks

### Test Review and Completeness (2026-03-18)

**Status:** Phase 1 Complete - Review finished, moving to Phase 2 - Additions

**Completed:**
- Reviewed all 169 unit tests + 33 service tests (202 total)
- Confirmed NO MOCKS are used anywhere ✅
- Analyzed coverage for all operation types
- Documented findings in TEST_REVIEW.md

**Next Steps:**
- Add high-priority tests for library schemas
- Add Unicode/special character handling tests
- Add edge case tests for large files
- Document existing tests with better docstrings

## Completed

<!-- One-line summaries of finished plans, newest first -->

<!-- Example: 2026-02-20 - Added CLI unified entry point (hedpy) - PR #1200 -->
