# GA4 omitted-case-segments regression

`processing.json` retains the exact `ir_027` processing record and its three referenced locations from the failed online processing response recorded in `provenance.json`. `instruction.json` retains its exact instruction from the run's initial CFG. The `failure` candidate omits the optional `segments` field; it is not rewritten to `[]`.

The two source files are byte-identical copies used to preserve the original evidence paths and line numbers. Tests create only a one-block wrapper, terminal return, and source-backed Task around this extraction. Separate authored examples cover a candidate that directly yields an existing input or member and the same case forms inside `for_each`.

These are offline interface/compiler regressions. They neither execute the Skill nor replay the historical run, and passing them does not establish that the entire original GA4 answer compiles or is semantically complete.
