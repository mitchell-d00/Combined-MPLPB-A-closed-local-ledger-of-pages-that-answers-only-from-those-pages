# Ask one question and check its source

This trial uses a small local collection of invented records. MPLPB answers from
those records. A citation shows what a record says; it does not prove that the
event happened.

After the common setup, list your five questions:

```sh
python pilot.py tasks
```

Ask a question by number, for example:

```sh
python pilot.py ask 1
```

Read `kind`, `text`, `claims` and `diagnostic`. A `supported_answer` has checked
source evidence. An `abstain` leaves the question unanswered. A `conflict` retains
competing source claims rather than choosing one. A partial answer can contain
checked claims while leaving another requested part unresolved.

Open the first claim's first cited passage:

```sh
python pilot.py passage 1
```

For another citation, use `--claim` and `--citation`, counting from zero. The
passage includes its source ID, revision hash, exact text and coordinates. Read
it before deciding what the answer establishes.

A report can establish what it attributes to a speaker. An instruction can
establish what someone was told to do. Neither alone establishes that the action
was completed. Missing evidence is different from evidence of a conflict.

Try all five tasks. Record the result and what the source actually supports in
your own words. If a command fails, record that failure too.

The installed engine covers bounded question forms. These examples do not
establish broad documentary understanding. Contributor coordination and detailed
test history are linked from the retained existing documentation.
