# Getting started

Logmill began in 2019 as a weekend experiment in parsing syslog with awk. The
original prototype ran as a single shell script, and the lessons from it shaped
the pipeline architecture the project uses today: a reader stage, a parser
stage, and a fold stage, each independently testable.

That architecture matters because it determines how extensions hook in. A
reader may be swapped without touching the parser, which is why the project
treats the reader interface as stable and the parser internals as private.

Install it with `pipx install logmill`, then run `logmill init` in the directory
you want indexed.

The fold stage deserves particular mention: it is where aggregation happens,
and its design borrows from map-reduce without adopting the vocabulary.

## Configuration

Settings live in `~/.logmill/config.toml`.
