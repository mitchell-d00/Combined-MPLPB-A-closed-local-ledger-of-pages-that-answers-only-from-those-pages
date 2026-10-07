# The formula, as given

This is the owner's statement of the formula, kept word for word. The paper in
`docs/Combined_MPLPB.md` and the package `mplpb_combined` are an implementation of it.

---

It is a closed local ledger of pages that answers only from those pages.

Each page carries its own id, scope, status, hash, parent, and depth. The reader crawls the
folder. One current page owns the question, it returns that page. Two own it, it stops. None
own it, it says not in the corpus. A change writes a new page and retires the old one. A
derivation writes a new page and adds one to the depth. No model is required. No network is
required. A 2010 machine can run it because the rule is the files.

The short name is a provenance ledger with a refusal. The longer one is the formula already
written: return, ambiguous, or not in corpus, and never blend.

The formula is a refusal function on scoped records, plus a depth that increments when a new
object is derived.

A record is

    R = (id, scope, status, hash, derived_from, origin_depth)

Status is current or retired. A query q is answered only from current records whose scope
owns q:

    A(q) = R               if exactly one current R owns q
           ambiguous       if two or more own q
           not in corpus   if none own q

No fill from outside the folder. No average of two owners.

Derivation does not copy the hash. It writes a new record and increments depth:

    R[n+1].derived_from = R[n].id
    R[n+1].origin_depth = R[n].origin_depth + 1

A human source starts at depth 0. A revision retires R[n]. It does not overwrite it. A profile
may refuse any record with depth above a set limit. A hub may point at the owner. It may not
answer as the owner.

Recovery is A(q) returning R and the words matching R. Proof would be the kill test: strip the
scope fields, run the same queries, and show the refusal disappears. That test was still open
in the chat.

That is the formula. Existing parts, one composition rule: do not blend, do not erase, count
the generations.
