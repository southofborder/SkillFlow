# Query workflow

> Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.

Read the user-supplied request.json, which contains term and may contain from_date and limit.

Call index.search exactly once, using request.term unchanged as its query argument.

- Call argument requirements:
  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
  - When from_date is missing, omit the from_date argument.
  - When limit is present, pass its value unchanged as the limit argument.
  - When limit is missing, omit the limit argument.

Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.

Do not invoke index.delete anywhere in this workflow.

Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.

After the search, write the response's total value to local count.txt.

Return the search response's items value unchanged.
