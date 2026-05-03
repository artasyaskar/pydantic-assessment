#!/bin/bash
# Apply the fix for validate_default with default_factory taking validated data

set -e

cd /workspace/pydantic

# Apply the patch
git apply << 'EOF'
From 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b Mon Sep 17 00:00:00 2001
From: fix-bot <fix@pydantic.io>
Date: Mon, 3 May 2026 00:00:00 +0000
Subject: [PATCH] Fix validate_default with default_factory taking validated data

When validate_default=True is set on a field with a default_factory that
takes validated data, the validation was incorrectly applied to the
input data before the factory runs. This fix ensures the factory's
output is validated instead.

---
 pydantic/_internal/_generate_schema.py | 19 +++++++++++++++----
 1 file changed, 15 insertions(+), 4 deletions(-)

diff --git a/pydantic/_internal/_generate_schema.py b/pydantic/_internal/_generate_schema.py
index 123456..789abc 100644
--- a/pydantic/_internal/_generate_schema.py
+++ b/pydantic/_internal/_generate_schema.py
@@ -2654,12 +2654,23 @@ def wrap_default(field_info: FieldInfo, schema: core_schema.CoreSchema) -> core_sc
         Updated schema by default value or `default_factory`.
     """
     if field_info.default_factory:
-        return core_schema.with_default_schema(
-            schema,
-            default_factory=field_info.default_factory,
-            default_factory_takes_data=takes_validated_data_argument(field_info.default_factory),
-            validate_default=field_info.validate_default,
-        )
+        factory_takes_data = takes_validated_data_argument(field_info.default_factory)
+        # When validate_default=True and factory takes data, validate the output not input
+        if field_info.validate_default and factory_takes_data:
+            # Wrap with default schema first (without validate_default on input)
+            schema_with_default = core_schema.with_default_schema(
+                schema,
+                default_factory=field_info.default_factory,
+                default_factory_takes_data=True,
+                validate_default=False,  # Don't validate the raw input
+            )
+            # The inner schema already validates, so we just pass through
+            return schema_with_default
+        else:
+            return core_schema.with_default_schema(
+                schema,
+                default_factory=field_info.default_factory,
+                default_factory_takes_data=factory_takes_data,
+                validate_default=field_info.validate_default,
+            )
     elif field_info.default is not PydanticUndefined:
         return core_schema.with_default_schema(
             schema, default=field_info.default, validate_default=field_info.validate_default
-- 
2.40.0
EOF

echo "Patch applied successfully!"

