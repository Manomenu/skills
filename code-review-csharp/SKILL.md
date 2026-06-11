---
name: code-review-csharp
description: Professional multi-step code review skill. Focuses on KISS, SotA, OSS Licensing, style, and security.
---

# Purpose
To provide a structured, high-quality review of code changes by validating them through a 3-stage funnel: Architecture/Logic, Clean Code, and Security/Performance. 

## Variables

TARGET_BRANCH: string ?? master
BRANCH_WITH_CHANGES: string ?? 'not-provided'
MERGE_REQUEST_CHANGES: string ?? 'not-provided'
TASK_DESCIPTION: string ?? 'not-provided'

# Instructions

## Step 1: Architecture & Business Logic
- **Functionality**: [SKIP IF TASK_DESCIPTION not-provided] Does the code solve the specific business problem? Verify if changes implement task requirements/intention.
- **KISS Principle**: Identify over-engineered patterns. Favor built-in project .NET version features over custom complexity. Not newest .NET version, but project version. 
- **System Fit**: Ensure changes don't break existing patterns or duplicate existing functionality.
- **OSS Compliance**: Flag any non-permissive licenses (GPL, AGPL, Paid) in new dependencies.

## Step 2: Readability & Clean Code
- **Naming**: Ensure intent-based naming for variables, methods, and classes.
- **SRP (Single Responsibility)**: Check if classes or methods are doing too much.
- **Error Handling**: Verify edge cases (e.g., API 500, empty collections, null refs) and the use of modern .NET exception handling.
- **SotA .NET**: Check if SotA approaches are taken that are available in project .NET version, do not suggest newer approaches/tools.

## Step 3: Security & Performance
- **Security**: Look for SQL Injection, XSS, or improper data exposure.
- **Performance**: 
    - Identify N+1 query patterns.
    - Check for unnecessary allocations (prefer `Span<T>` / `ReadOnlySpan<T>` in hot paths).
    - Ensure correct use of the .NET `System.Threading.Lock`.

# Workflow
1. **Checklist Generation**: Create a internal TODO list based on the 3 steps (with substeps) in **Instructions** tailored to the specific diff [TARGET_BRANCH and MERGE_REQUEST_CHANGES] or [TARGET_BRANCH and BRANCH_WITH_CHANGES] and [TASK_DESCRIPTION], 
2. **Sequential Execution**: Execute each step of the TODO list against the provided code changes.
3. **Report Compilation**: Generate the final output using the mandatory **Report Format**.

# Report Format

## Summary
[Brief high-level overview of the MR quality and main concerns]

## Issues
For each identified issue, use the following template:

[Idx] [Must-Fix / Should-Improve / Nitpick] **Issue-short-name**
- **Expaination**: (Why the change is required, including line numbers and file location)
- **Suggestion**: 
    - [Description of the fix]
    - ```[Language]
      [Code snippet]
      ```

## Questions
For each concering question / ambiguity, use following template:

[Idx] [Question] **Question-short-name**
- (Question content, includes line numbers and file location if necessary)

# Cookbook

- **Scenario: No changes source**
  - IF: [BRANCH_WITH_CHANGES not-provided and MERGE_REQUEST_CHANGES not-provided]
  - THEN: Do not execute `Workflow` and ask for changes source.

- **Scenario: Direct Diff Review**
  - IF: Input contains [MERGE_REQUEST_CHANGES]
  - THEN: 
    - Checkout [TARGET_BRANCH]: `git checkout 'TARGET_BRANCH'`. Call `git fetch origin 'TARGET_BRACH'` if needed.
    - Execute `Workflow` with diff in [MERGE_REQUEST_CHANGES].

- **Scenario: Git Branch Review**
  - IF: Input contains `BRANCH_WITH_CHANGES` and `TARGET_BRANCH` branches.
  - THEN: 
    - `git fetch origin 'BRANCH_WITH_CHANGES'`
    - `git checkout 'BRANCH_WITH_CHANGES'` - for broader context
    - `git diff origin/'TARGET_BRANCH'..origin/'BRANCH_WITH_CHANGES'`
    - Execute `Workflow` on the resulting diff.