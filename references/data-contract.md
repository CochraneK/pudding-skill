# Data contract

Column names are not semantics. When units, roles, or labels are ambiguous, provide a JSON data contract and pass it to the pipeline with `--schema`.

Use `examples/data-schema.example.json` as the model:

```json
{
  "fields": {
    "year": { "role": "time", "label": "Year" },
    "city": { "role": "category", "label": "City" },
    "income_index": {
      "role": "measure",
      "label": "Income index",
      "unit": "index, 2019 = 100",
      "description": "Synthetic income level indexed to 2019"
    }
  },
  "notes": ["Values are synthetic."]
}
```

Allowed roles:

- `time` — temporal ordering field;
- `category` — comparison/grouping field;
- `measure` — numeric quantity eligible for analysis;
- `identifier` — entity key, not an analytical category by default;
- `ignore` — exclude from candidate generation.

Labels and units flow into the story spec and renderer while raw field names remain the machine-readable keys.

A contract improves interpretation but does not prove that the data itself is valid. Review denominators, sampling, missingness, transformations, and collection methodology separately.
