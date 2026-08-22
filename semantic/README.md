# S1 semantic extraction

Semantic extraction is deliberately conservative. It consumes only captured raw bytes plus an exact business date/source identity. It must never fetch a URL, fill missing values, infer a lottery result, or overwrite a conflicting value.

The extractor emits a structured 27-number XSMB record only when all prize classes are explicitly identified and have the expected counts. Ambiguous or unsupported markup returns DENY rather than a partial record.
