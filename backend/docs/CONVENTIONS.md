# Coding Conventions

## Naming
- Use clear, meaningful names for variables, functions, classes, and files so their purpose is immediately understandable without reading the implementation.

## File Organization
- Break large files into smaller, well-organized modules.
- Use imports appropriately across modules.

## Function Design
- One function = one responsibility. If a function does multiple things, split it.

## Layer Separation
- Views handle requests and responses only — no business logic.
- Serializers handle validation and serialization only.
- Business logic lives in dedicated service or helper layers.

## DRY
- Remove duplicate code.
- Extract reusable utilities, constants, validators, and common logic into separate files.

## Readability
- Add concise docstrings and type hints where they improve readability.

## Code Organization
- Structure folders and modules for long-term maintainability.

## Cross-Cutting Concerns
- Standardize logging, exception handling, and configuration management across the project.

## Constants
- Replace hardcoded values with named constants or configuration variables.

## Database Queries
- Improve readability of queries without changing their behavior.

## Consistency
- Follow consistent coding conventions throughout the entire project.

## Strucutring 
- For each class create a new file 