#!/usr/bin/env python3
"""Rebuild the three example corpora under examples/.

Every page is written through the library's own write, revise, derive and
ratify calls, in a fixed order with a fixed timestamp, so the hashes and the
log come out the same on every machine.

    python3 tools/build_examples.py
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from mplpb_combined import ledger as L  # noqa: E402

WHEN = "2026-10-07T00:00Z"
OWNER = "Example Studio"


def fresh(name: str) -> Path:
    root = HERE / "examples" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    return root


def build_studio() -> Path:
    root = fresh("studio")

    # What each page says it is not for: subjects next to its own that it
    # does not cover. A revision inherits its predecessor's.
    not_for = {
        1: "booking; access; fees; raku; glass; porcelain",
        3: "booking; access; fees; recipes; raku; porcelain",
        4: "booking; access; permission; training; allowed; fees; raku",
        5: "booking; fees",
        7: "booking; buying",
        10: "recipes; colours; trimming",
        11: "recipes; colours",
        13: "finished work; selling; colours; recipes",
        14: "moulds; casting; buying",
        15: "centering; pulling walls; trimming; repair",
        16: "attaching parts; trimming; throwing technique",
        17: "prices; buying; ordering; porcelain; suppliers",
        18: "children; opening hours; rules",
        20: "heating; opening hours; winter",
        21: "serious injury; ambulance",
    }

    def w(n, d, title, scope, when, body, **kw):
        return L.write(root, doc_id=f"STUDIO-{n:04d}", directory=d, title=title, scope=scope,
                       when_to_use=when, not_for=not_for.get(n, ""), body=body, owner=OWNER,
                       when=WHEN, **kw)

    def rev(old, n, body, note):
        return L.revise(root, f"STUDIO-{old:04d}", new_id=f"STUDIO-{n:04d}", body=body,
                        owner=OWNER, when=WHEN, note=note)

    # -- kiln ---------------------------------------------------------------
    w(1, "kiln", "Bisque firing schedule",
      "Bisque firing schedule for greenware in the electric kiln",
      "first firing of unglazed pots; how fast to heat raw clay; ramp rate before glazing",
      "Load bone-dry ware only. Climb 150 C per hour straight to 950 C. No soak. "
      "Unload once the pyrometer reads under 200 C.")
    rev(1, 2,
        "Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can "
        "leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. "
        "Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.",
        "slower first stage after two blow-outs; peak raised to cone 06")
    w(3, "kiln", "Glaze firing schedule, cone 6, electric kiln",
      "Glaze firing schedule to cone 6 in the electric kiln",
      "second firing; firing glazed pots; stoneware top temperature; slow cooling",
      "Climb 150 C per hour to 1100 C, then 60 C per hour to 1222 C. Soak fifteen minutes. "
      "For matte surfaces drop to 950 C and hold an hour before switching off. Leave the lid "
      "shut until the pyrometer reads under 125 C.")
    w(4, "kiln", "Glaze firing schedule, cone 6, gas kiln",
      "Glaze firing schedule to cone 6 in the gas kiln with reduction",
      "second firing; firing glazed pots; stoneware top temperature; body reduction; damper setting",
      "Light both burners on low and candle for an hour. Begin body reduction at 900 C by "
      "closing the damper to a finger's width until a soft flame shows at the spy hole. Return "
      "to neutral at 1000 C and climb to 1222 C over five hours. Finish with ten minutes of "
      "oxidation to clear the atmosphere.")
    w(5, "kiln", "Loading the kiln",
      "Loading the kiln: shelves, posts and spacing between pots",
      "stacking ware; how close pieces can sit; kiln wash; glazed pots touching",
      "Three posts per shelf, set in the same positions on every layer so the load carries "
      "straight down. Glazed work needs a finger's width between pieces and from the elements. "
      "Bisque can touch and can nest. Brush batt wash on the upper face of each shelf only, "
      "never the underside, where flakes fall into work below.")
    w(6, "kiln", "Witness cones",
      "Placing and reading witness cones",
      "checking whether a firing reached temperature; bent cone; underfired or overfired load",
      "Set a pack of three, guide, target and guard, in a pad of wadding where it can be seen "
      "through the spy hole. A good firing bends the target tip to the level of its base, "
      "leaves the guard standing and lays the guide flat. If the guard has gone over, the load "
      "ran hot: shorten the soak next time rather than lowering the set point.")
    w(7, "kiln", "Element care",
      "Inspecting and replacing kiln elements",
      "kiln slow to climb; kiln not reaching temperature; sagging coils; error on the controller",
      "Elements age by growing an oxide skin, which raises resistance and stretches firing "
      "times. Measure each circuit with a multimeter twice a year and replace the set when "
      "resistance has risen by ten percent. Never mix old and new in one circuit. Fire new "
      "elements empty once to 1000 C to form the protective coat before any reduction "
      "materials go near them.")

    # -- glaze --------------------------------------------------------------
    w(8, "glaze", "Mixing a glaze batch",
      "Mixing a glaze batch from dry materials",
      "weighing out a recipe; sieving; how much water to add; specific gravity",
      "Weigh the powders into a dry bucket, add water to a creamy consistency and stir. "
      "Pass once through a 60 mesh sieve.")
    rev(8, 9,
        "Put the water in the bucket first, then the powders, so nothing cakes on the bottom. "
        "Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh "
        "sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe "
        "code on the lid and on the side.",
        "water first; finer sieve; hydrometer target added")
    w(10, "glaze", "Glazing by dipping",
      "Applying glaze by dipping and pouring",
      "how thick to coat bisque; glaze running; bare patches; wax on the foot ring",
      "Wax the foot ring and let it dry. Hold with tongs, dip for a count of three and lift "
      "out with a twist to shed the drip. The coat should be the thickness of a postcard: "
      "scratch through with a pin to check. Touch up tong marks with a brush once the surface "
      "has lost its shine. Sponge the foot clean before the piece goes on a board.")
    w(11, "glaze", "Glazing by spraying",
      "Applying glaze with the spray gun",
      "how thick to coat bisque; spray booth; uneven coat; large pieces",
      "Thin the glaze to 1.35 on the hydrometer and strain it into the cup. Run the extractor "
      "before picking up the gun. Work on a banding wheel, keep the nozzle a forearm away and "
      "build three light passes rather than one wet one. The surface should look like fine "
      "velvet; if it glistens, stop and let it dry.")
    w(12, "glaze", "Glaze faults",
      "Diagnosing glaze faults: crawling, pinholes and crazing",
      "glaze pulled away from the pot; small holes in the fired surface; fine cracks in the glaze",
      "Crawling comes from dust or grease on the bisque, or a coat put on too thick that "
      "cracked as it dried. Wash bisque that has sat on a shelf for more than a week. Pinholes "
      "are gas still leaving the body: bisque hotter or add a soak at peak. Crazing is a fit "
      "problem between glaze and body and will not be cured by refiring; change the recipe.")
    w(13, "glaze", "Storing glaze materials",
      "Storing and labelling glaze materials",
      "unlabelled bucket; how long mixed glaze keeps; glaze settled hard at the bottom",
      "Every container carries the recipe code, the date and the mixer's initials on both lid "
      "and side. Anything unmarked goes to the quarantine shelf and is not used. A wet batch "
      "keeps for a year if the lid is tight. If it has hard-panned, add a teaspoon of Epsom "
      "salt solution and sieve again.")

    # -- clay ---------------------------------------------------------------
    w(14, "clay", "Reclaiming clay",
      "Reclaiming clay scraps and slop",
      "recycling trimmings; slurry too wet; drying clay on plaster",
      "Let scraps go bone dry, then slake them in a bucket of water overnight without "
      "stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster "
      "batt and turn it when the underside peels away clean. Keep red and white bodies in "
      "separate buckets; a mixed batch cannot be sorted afterwards.")
    w(15, "clay", "Wedging",
      "Wedging clay before throwing",
      "air bubbles; lumpy or uneven clay; preparing a ball for the wheel",
      "Ram's head for small amounts, spiral for anything over two kilos. Thirty turns is a "
      "minimum. Cut the lump with a wire and look at the face: it should be one even colour "
      "with no holes. Wedge on canvas or bare wood, not on plaster, which chips into the clay "
      "and blows out in the kiln.")
    w(16, "clay", "Drying ware",
      "Drying thrown and hand-built ware to bone dry",
      "cracks while drying; when a pot is ready for the kiln; covering with plastic; "
      "handles pulling away",
      "Dry slowly and evenly. Turn pots onto their rims once they will hold their shape, so "
      "the base catches up with the lip. Wrap handles and joins loosely for the first day. A "
      "piece is ready when it no longer feels cool against the cheek. Thick sculpture needs "
      "two weeks, not two days.")
    w(17, "clay", "Clay bodies in stock",
      "Clay bodies kept in stock and their firing ranges",
      "which clay for cone 6; earthenware or stoneware; shrinkage; clay for sculpture",
      "White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. Red "
      "earthenware, RE, matures at cone 04 and must never go in a cone 6 firing, where it "
      "slumps and fuses to the shelf. Grogged crank, CR, is for sculpture and large slab work "
      "and tolerates uneven drying.")

    # -- safety -------------------------------------------------------------
    w(18, "safety", "Dust control",
      "Controlling clay and glaze dust; silica exposure",
      "sweeping the studio; mask or respirator; cleaning up dry glaze",
      "Sweep the floor at the end of each session and wipe the benches with a damp cloth. "
      "Wear a paper mask when handling powders.")
    rev(18, 19,
        "Never sweep or brush dry. Wet mop the floor and sponge the benches at the end of each "
        "session. Wear a fitted P3 half-mask whenever a bag of powder is open; paper masks do "
        "not stop respirable silica. Wash aprons weekly rather than shaking them out.",
        "dry sweeping withdrawn; paper masks withdrawn")
    w(20, "safety", "Kiln ventilation",
      "Kiln ventilation and fumes during firing",
      "smell while firing; vent fan; staying in the room with a hot kiln",
      "Switch the extractor on before the kiln and leave it running until the pyrometer reads "
      "under 200 C. Wax burn-off and sulphur from some clays come off between 200 C and 700 C; "
      "keep the kiln room door shut and work elsewhere during that stretch. Spy hole bungs "
      "stay in after 600 C.")
    w(21, "safety", "Hot ware and burns",
      "Handling hot ware and treating minor burns",
      "unloading a warm kiln; gloves; touched a hot shelf",
      "Use the leather gauntlets for anything over 60 C and set work down on the kiln shelf "
      "offcuts, never on a wooden bench. For a burn, twenty minutes under cool running water "
      "straight away, then cover loosely with cling film. Anything larger than a coin, or "
      "blistered, goes to the minor injuries unit.")

    # -- derived: one generation, two generations, and one ratified ---------
    L.derive(root, ["STUDIO-0002", "STUDIO-0003", "STUDIO-0005"], doc_id="STUDIO-0022",
             directory="derived", title="Firing day checklist",
             scope="Firing day checklist assembled from the schedules and loading rules",
             when_to_use="checklist before switching on; what to check on firing day",
             body="1. Ware bone dry, or glazed feet wiped. 2. Three posts per shelf, aligned. "
                  "3. Cone pack visible through the spy hole. 4. Extractor on. 5. Programme "
                  "matches the load: bisque to 1000 C, glaze to 1222 C. 6. Log the start time "
                  "on the door sheet.",
             owner="assistant", when=WHEN)
    L.derive(root, ["STUDIO-0022"], doc_id="STUDIO-0023", directory="derived",
             title="Weekly firing digest",
             scope="Weekly digest of firings, compiled from the checklist",
             when_to_use="summary of this week's firings; digest",
             body="Two bisque and one glaze firing completed. All checklists returned complete.",
             owner="assistant", when=WHEN)
    L.derive(root, ["STUDIO-0012"], doc_id="STUDIO-0024", directory="derived",
             title="Glaze fault quick reference",
             scope="Quick reference card for glaze faults",
             when_to_use="one-line fixes; quick reference card",
             body="Crawling: clean the bisque, thinner coat. Pinholes: hotter bisque or a soak. "
                  "Crazing: change the recipe; refiring will not help.",
             owner="assistant", when=WHEN)
    L.ratify(root, "STUDIO-0024", "Studio manager", new_id="STUDIO-0025", when=WHEN)
    L.build_index(root, "Example Studio \u2014 Main Index")
    return root


def build_spec() -> Path:
    root = fresh("spec")
    n = [0]

    def w(title, scope, when, body):
        n[0] += 1
        return L.write(root, doc_id=f"SPEC-{n[0]:04d}", title=title, scope=scope,
                       when_to_use=when, body=body, owner="Mitchell D. McPhetridge", when=WHEN)

    w("The record",
      "The six fields every page carries: id, scope, status, hash, parent and depth",
      "what a page must declare; record fields; page format",
      "A record is one HTML page. Its head carries mplpb:document-id, mplpb:scope, "
      "mplpb:status, mplpb:hash, mplpb:derived-from and mplpb:origin-depth. Status is current "
      "or retired. The hash covers the title, the body and every field except status and the "
      "hash itself, so retiring a page changes one line and nothing the page says.\n\n"
      "Optional fields: when-to-use, supersedes, origin, ratified-by, owner, updated, kind and "
      "points-to. Underscores and hyphens in field names are read as the same.")
    w("The answer rule",
      "The answer rule: return, ambiguous, or not in corpus",
      "how a question is answered; two pages claim the same question; nothing matches; never blend",
      "If exactly one current page owns the question, the reader returns that page, whole, "
      "with its citation. If two or more own it, the reader stops and names them. If none own "
      "it, the reader says not in the corpus. It never fills from outside the folder and never "
      "averages two owners.")
    w("Ownership",
      "How ownership of a question is decided: declared scope first, then prose",
      "why a page did or did not match; scope before prose; matched on prose",
      "Step one is scope. A page owns a question when its scope and when-to-use fields "
      "declare more than half of the question's content words. Step two is prose, and it is "
      "reached only when no page owns the question by scope: a page then owns the question "
      "when every content word appears somewhere on it. At either step a page whose matched "
      "words strictly contain another owner's is the more specific, and the other drops out. "
      "A return decided by prose says so in its citation. Word endings are folded, so firing "
      "and fired are one word. There are no synonyms.")
    w("Revision",
      "Revising a page: write the new one, retire the old one",
      "changing a page; correcting a mistake; what happened to the old version",
      "A change writes a new page with a new id that names the old one in supersedes, pinned "
      "to the old page's hash. Then the old page's status line is set to retired. The order "
      "matters: a page named in supersedes is read as retired even if the second step never "
      "happened. Nothing is deleted and nothing is moved.")
    w("Derivation and depth",
      "Derivation, origin depth and ratification",
      "a machine wrote this page; counting generations; signing off a derived page",
      "A human source is depth 0. A machine page written from nothing is depth 1. A derived "
      "page is one deeper than its deepest parent. A revision is at least as deep as the page "
      "it replaces. Ratification writes a new page carrying the name of the person who stands "
      "behind it; its depth is 0 and its lineage is kept.")
    w("Profiles",
      "Profiles: what a deployment will serve",
      "depth limit; customer-facing reader; withheld page",
      "A profile sets the deepest record it will serve and whether prose may be consulted. "
      "lab serves to depth 2 and internal to depth 1, both with the prose step. external "
      "serves depth 0 only and decides by declared scope or not at all. A withheld page is "
      "reported as withheld, with its depth, and is not answered from.")
    w("Hubs",
      "Hubs and pointers between corpora",
      "several folders; routing a question to another corpus; owner not reachable",
      "A pointer is a record whose kind is pointer and whose points-to names another root. "
      "When a pointer owns a question the reader asks the question again in that root and "
      "returns what that root returns, with the route. If the root cannot be reached the "
      "answer is a refusal that names the owner. A pointer's own body is never an answer.")
    w("Validation",
      "Validation checks C1 to C14",
      "a page was edited by hand; hash mismatch; fork; broken log",
      "C1 missing field. C2 content does not match hash. C3 duplicate id. C4 bad status or "
      "origin. C5 reference to a page not in the folder. C6 pinned parent changed. C7 "
      "reference without a hash. C8 declared depth disagrees with lineage. C9 retirement "
      "unfinished. C10 supersession fork. C11 pointer target. C12 lineage loop. C13 stray "
      "file. C14 log chain.")
    w("The not-for field",
      "The not-for field: a page saying what it does not cover",
      "page returned for a question it does not answer; adjacent question; set aside",
      "A page may carry mplpb:not-for, a few words for subjects near its own that it does "
      "not cover. A page is set aside for any question containing one of those words, before "
      "ownership is decided. A word the page also declares in its scope is ignored there, and "
      "the validator says so. The field enters the hash only when it is used, so pages "
      "written before it existed keep their hashes.")
    w("What this does not claim",
      "Limits of the format: what a ledger with a refusal cannot establish",
      "is the answer true; proof; kill test",
      "Returning a page says where the words came from. It does not say they are right. A "
      "hash shows a page was not edited after writing; it does not show who wrote it. Depth "
      "counts declared generations; a writer who lies about origin is not caught. The kill "
      "test in this repository is one author's run on one small corpus.")
    L.build_index(root, "Combined MPLPB \u2014 the format, as pages")
    return root


def build_hub() -> Path:
    root = fresh("hub")
    L.write(root, doc_id="HUB-0001", kind="pointer", points_to="../studio",
            title="Example Studio corpus",
            scope="Pottery studio practice: kiln, firing, glaze, clay and studio safety",
            when_to_use="bisque; cone; stoneware; wedging; dust; glazing",
            body="Points at examples/studio. This page routes; it does not answer.",
            owner="hub", when=WHEN)
    L.write(root, doc_id="HUB-0002", kind="pointer", points_to="../spec",
            title="Combined MPLPB format corpus",
            scope="The Combined MPLPB format and its rules",
            when_to_use="record fields; answer rule; ownership; revision; derivation; depth; "
                        "profiles; hubs; pointers; validation",
            body="Points at examples/spec. This page routes; it does not answer.",
            owner="hub", when=WHEN)
    L.build_index(root, "Example hub")
    return root


if __name__ == "__main__":
    for build in (build_studio, build_spec, build_hub):
        r = build()
        led = L.Ledger(r)
        errs = [f for f in led.findings() if f.level == "error"]
        print(f"{r.relative_to(HERE)}: {len(led.records)} pages, {len(errs)} error(s)")
        for f in errs:
            print("  ", f)
