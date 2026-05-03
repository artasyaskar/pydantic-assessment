# Reference Plan: Fix validate_default with default_factory taking validated data

## Root Cause Analysis

The issue is in the `wrap_default` function in `pydantic/_internal/_generate_schema.py`. When a field has both `validate_default=True` and a `default_factory` that takes validated data, the current implementation:

1. Wraps the schema with `with_default_schema` 
2. Passes `validate_default` to the core schema
3. However, pydantic-core validates the *input* value before applying the default factory, rather than validating the factory's *output*

The core schema `with_default_schema` with `validate_default=True` validates the data *before* the default factory runs, which is incorrect for factories that transform data.

## Fix Strategy

The fix needs to ensure that when `validate_default=True` is set with a `default_factory`, the validation happens on the *output* of the factory, not the input.

There are two approaches:

1. **Defer validation to after factory execution**: Wrap the schema with an `after` validator that runs after the default factory produces a value.

2. **Adjust the core schema generation**: Modify how `with_default_schema` is created so validation happens post-factory execution.

The correct approach is to handle this in `wrap_default()` by:
- When `validate_default=True` AND `default_factory_takes_data=True`, add an after-validator to validate the factory's output
- The after-validator should run the same type validation as the original schema

## Files to Modify

1. `pydantic/_internal/_generate_schema.py`:
   - Modify `wrap_default()` function (around line 2647)
   - When `validate_default=True` and factory takes data, add after-validator

2. Test case verification:
   - Create test showing the bug
   - Verify fix passes

## Implementation Steps

1. Locate `wrap_default()` function
2. Identify the code path for `default_factory_takes_data=True`
3. When `validate_default=True` in this path:
   - Instead of passing `validate_default` directly to `with_default_schema`
   - Create an after-validator that validates the factory's output
   - Wrap the schema with this validator
4. Ensure the fix handles both factory types (with and without data)
5. Add tests to prevent regression

## Edge Cases to Consider

- Default factory that doesn't take data (should still work as before)
- Default factory that takes data but produces None
- Nested models with validated default factories
- Union types with validate_default
- Annotated types with validators
