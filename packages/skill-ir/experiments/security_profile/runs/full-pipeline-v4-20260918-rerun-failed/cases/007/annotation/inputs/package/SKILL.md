---
name: catalog-query
description: Query an index once using a supplied request and preserve optional-parameter semantics.
---

# Catalog Query

1. Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.
2. Read the user-supplied request.json, which contains term and may contain from_date and limit.
3. Call index.search exactly once, using request.term unchanged as its query argument.
4. When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
5. When from_date is missing, omit the from_date argument.
6. When limit is present, pass its value unchanged as the limit argument.
7. When limit is missing, omit the limit argument.
8. Do not invoke index.delete anywhere in this workflow.
9. Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.
10. After the search, write the response's total value to local count.txt.
11. Return the search response's items value unchanged.
