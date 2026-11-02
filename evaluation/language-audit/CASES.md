# Per-case baseline semantic review

Model-authored review of inspected development data. Original labels and source bytes unchanged. Full stage diagnostics are in cases.json. Each cited passage below is the body of the historically expected page; page identity is not an entailment oracle.

## probes / od01

how fast should I heat raw clay on its first firing

> Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / od02

the glaze pulled away from the pot

> Crawling comes from dust or grease on the bisque, or a coat put on too thick that cracked as it dried. Wash bisque that has sat on a shelf for more than a week. Pinholes are gas still leaving the body: bisque hotter or add a soak at peak. Crazing is a fit problem between glaze and body and will not be cured by refiring; change the recipe.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / od03

I found an unlabelled bucket

> Every container carries the recipe code, the date and the mixer's initials on both lid and side. Anything unmarked goes to the quarantine shelf and is not used. A wet batch keeps for a year if the lid is tight. If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / od04

do I need a mask or respirator when sweeping the studio

> Never sweep or brush dry. Wet mop the floor and sponge the benches at the end of each session. Wear a fitted P3 half-mask whenever a bag of powder is open; paper masks do not stop respirable silica. Wash aprons weekly rather than shaking them out.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate restraint or unsupported conditional interpretation.

Classes: conditions. First limiting stage: interpretation. Expected defensible behavior / general repair: Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.

## probes / od05

air bubbles in my clay before throwing

> Ram's head for small amounts, spiral for anything over two kilos. Thirty turns is a minimum. Cut the lump with a wire and look at the face: it should be one even colour with no holes. Wedge on canvas or bare wood, not on plaster, which chips into the clay and blows out in the kiln.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / od06

there is a smell while firing

> Switch the extractor on before the kiln and leave it running until the pyrometer reads under 200 C. Wax burn-off and sulphur from some clays come off between 200 C and 700 C; keep the kiln room door shut and work elsewhere during that stretch. Spy hole bungs stay in after 600 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / od07

how close can pieces sit when stacking

> Three posts per shelf, set in the same positions on every layer so the load carries straight down. Glazed work needs a finger's width between pieces and from the elements. Bisque can touch and can nest. Brush batt wash on the upper face of each shelf only, never the underside, where flakes fall into work below.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / od08

which clay for cone 6

> White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. Red earthenware, RE, matures at cone 04 and must never go in a cone 6 firing, where it slumps and fuses to the shelf. Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.

Observed: **return**. Returned: White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / od09

kiln slow to climb and not reaching temperature

> Elements age by growing an oxide skin, which raises resistance and stretches firing times. Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent. Never mix old and new in one circuit. Fire new elements empty once to 1000 C to form the protective coat before any reduction materials go near them.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / od10

handles pulling away and cracks while drying

> Dry slowly and evenly. Turn pots onto their rims once they will hold their shape, so the base catches up with the lip. Wrap handles and joins loosely for the first day. A piece is ready when it no longer feels cool against the cheek. Thick sculpture needs two weeks, not two days.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / op01

how long do I candle the burners

> Light both burners on low and candle for an hour. Begin body reduction at 900 C by closing the damper to a finger's width until a soft flame shows at the spy hole. Return to neutral at 1000 C and climb to 1222 C over five hours. Finish with ten minutes of oxidation to clear the atmosphere.

Observed: **return**. Returned: Light both burners on low and candle for an hour.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op02

what does it mean if the guard has gone over

> Set a pack of three, guide, target and guard, in a pad of wadding where it can be seen through the spy hole. A good firing bends the target tip to the level of its base, leaves the guard standing and lays the guide flat. If the guard has gone over, the load ran hot: shorten the soak next time rather than lowering the set point.

Observed: **return**. Returned: If the guard has gone over, the load ran hot: shorten the soak next time rather than lowering the set point.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op03

how often should I measure resistance with a multimeter

> Elements age by growing an oxide skin, which raises resistance and stretches firing times. Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent. Never mix old and new in one circuit. Fire new elements empty once to 1000 C to form the protective coat before any reduction materials go near them.

Observed: **return**. Returned: Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op04

how long should powders slake before stirring

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported anaphora.

Classes: reference. First limiting stage: evidence. Expected defensible behavior / general repair: Resolve it only to a unique explicit same-document antecedent with cited antecedent span; reject ambiguous referents.

## probes / op05

how much Epsom salt solution

> Every container carries the recipe code, the date and the mixer's initials on both lid and side. Anything unmarked goes to the quarantine shelf and is not used. A wet batch keeps for a year if the lid is tight. If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.

Observed: **return**. Returned: If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.. Disposition: supported conditional quotation; antecedent it remains unresolved (partial applicability).

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op06

ram's head or spiral

> Ram's head for small amounts, spiral for anything over two kilos. Thirty turns is a minimum. Cut the lump with a wire and look at the face: it should be one even colour with no holes. Wedge on canvas or bare wood, not on plaster, which chips into the clay and blows out in the kiln.

Observed: **return**. Returned: Ram's head for small amounts, spiral for anything over two kilos.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op07

what is bag code CR for

> White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. Red earthenware, RE, matures at cone 04 and must never go in a cone 6 firing, where it slumps and fuses to the shelf. Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.

Observed: **return**. Returned: Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes / op08

how long under cool running water

> Use the leather gauntlets for anything over 60 C and set work down on the kiln shelf offcuts, never on a wooden bench. For a burn, twenty minutes under cool running water straight away, then cover loosely with cling film. Anything larger than a coin, or blistered, goes to the minor injuries unit.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / om01

my glaze has small holes in the fired surface after the last load, what went wrong

> Crawling comes from dust or grease on the bisque, or a coat put on too thick that cracked as it dried. Wash bisque that has sat on a shelf for more than a week. Pinholes are gas still leaving the body: bisque hotter or add a soak at peak. Crazing is a fit problem between glaze and body and will not be cured by refiring; change the recipe.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / om02

is it safe to stay in the room with a hot kiln overnight

> Switch the extractor on before the kiln and leave it running until the pyrometer reads under 200 C. Wax burn-off and sulphur from some clays come off between 200 C and 700 C; keep the kiln room door shut and work elsewhere during that stretch. Spy hole bungs stay in after 600 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate restraint or unsupported conditional interpretation.

Classes: conditions. First limiting stage: interpretation. Expected defensible behavior / general repair: Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.

## probes / om03

the coils are sagging badly near the bottom of the chamber

> Elements age by growing an oxide skin, which raises resistance and stretches firing times. Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent. Never mix old and new in one circuit. Fire new elements empty once to 1000 C to form the protective coat before any reduction materials go near them.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / om04

can I recycle my trimmings from yesterday's session

> Let scraps go bone dry, then slake them in a bucket of water overnight without stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate restraint or unsupported conditional interpretation.

Classes: conditions. First limiting stage: interpretation. Expected defensible behavior / general repair: Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.

## probes / om05

what gloves should I wear for unloading a warm kiln

> Use the leather gauntlets for anything over 60 C and set work down on the kiln shelf offcuts, never on a wooden bench. For a burn, twenty minutes under cool running water straight away, then cover loosely with cling film. Anything larger than a coin, or blistered, goes to the minor injuries unit.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate restraint or unsupported conditional interpretation.

Classes: conditions. First limiting stage: interpretation. Expected defensible behavior / general repair: Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.

## probes / om06

how much water to add when weighing out a recipe for a celadon

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: incomplete benchmark expectation / legitimate abstention.

Classes: missing_value. First limiting stage: evidence. Expected defensible behavior / general repair: No water quantity is given; explain the gap rather than invent a recipe amount.

## probes / om07

my bent cone looks wrong, did the firing reach temperature

> Set a pack of three, guide, target and guard, in a pad of wadding where it can be seen through the spy hole. A good firing bends the target tip to the level of its base, leaves the guard standing and lays the guide flat. If the guard has gone over, the load ran hot: shorten the soak next time rather than lowering the set point.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes / om08

should I be covering my teapot with plastic over the weekend

> Dry slowly and evenly. Turn pots onto their rims once they will hold their shape, so the base catches up with the lip. Wrap handles and joins loosely for the first day. A piece is ready when it no longer feels cool against the cheek. Thick sculpture needs two weeks, not two days.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate restraint or unsupported conditional interpretation.

Classes: conditions. First limiting stage: interpretation. Expected defensible behavior / general repair: Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.

## probes / rt01

bisque firing schedule for greenware

> Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / rt02

ramp rate before glazing

> Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / rt03

mixing a glaze batch from dry materials

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / rt04

sieving and specific gravity

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / rt05

controlling silica exposure

> Never sweep or brush dry. Wet mop the floor and sponge the benches at the end of each session. Wear a fitted P3 half-mask whenever a bag of powder is open; paper masks do not stop respirable silica. Wash aprons weekly rather than shaking them out.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes / rt06

cleaning up dry glaze

> Never sweep or brush dry. Wet mop the floor and sponge the benches at the end of each session. Wear a fitted P3 half-mask whenever a bag of powder is open; paper masks do not stop respirable silica. Wash aprons weekly rather than shaking them out.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_heldout / h01

glaze is running down the pot

> Wax the foot ring and let it dry. Hold with tongs, dip for a count of three and lift out with a twist to shed the drip. The coat should be the thickness of a postcard: scratch through with a pin to check. Touch up tong marks with a brush once the surface has lost its shine. Sponge the foot clean before the piece goes on a board.

Observed: **ambiguous**. Returned: (no answer). Disposition: expected page does not establish this diagnosis; ambiguity is not proven body conflict.

Classes: situation_to_relation, incomplete_benchmark_expectation, multiple_owners. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis. Flag the expected dipping page: it does not assert the requested diagnosis.

## probes_heldout / h02

what should I do about lumpy clay

> Ram's head for small amounts, spiral for anything over two kilos. Thirty turns is a minimum. Cut the lump with a wire and look at the face: it should be one even colour with no holes. Wedge on canvas or bare wood, not on plaster, which chips into the clay and blows out in the kiln.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes_heldout / h03

is earthenware or stoneware better for sculpture

> White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. Red earthenware, RE, matures at cone 04 and must never go in a cone 6 firing, where it slumps and fuses to the shelf. Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: benchmark expects a page, not an established comparison.

Classes: comparison. First limiting stage: evidence extraction. Expected defensible behavior / general repair: Return source-declared suitability separately; do not invent a universal ranking.

## probes_heldout / h04

my slurry is too wet

> Let scraps go bone dry, then slake them in a bucket of water overnight without stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes_heldout / h05

error showing on the controller

> Elements age by growing an oxide skin, which raises resistance and stretches firing times. Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent. Never mix old and new in one circuit. Fire new elements empty once to 1000 C to form the protective coat before any reduction materials go near them.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes_heldout / h06

I touched a hot shelf

> Use the leather gauntlets for anything over 60 C and set work down on the kiln shelf offcuts, never on a wooden bench. For a burn, twenty minutes under cool running water straight away, then cover loosely with cling film. Anything larger than a coin, or blistered, goes to the minor injuries unit.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_heldout / h07

bare patches after glazing

> Wax the foot ring and let it dry. Hold with tongs, dip for a count of three and lift out with a twist to shed the drip. The coat should be the thickness of a postcard: scratch through with a pin to check. Touch up tong marks with a brush once the surface has lost its shine. Sponge the foot clean before the piece goes on a board.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: expected page does not establish this diagnosis; ambiguity is not proven body conflict.

Classes: situation_to_relation, incomplete_benchmark_expectation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis. Flag the expected dipping page: it does not assert the requested diagnosis.

## probes_heldout / h08

fine cracks in the glaze after firing

> Crawling comes from dust or grease on the bisque, or a coat put on too thick that cracked as it dried. Wash bisque that has sat on a shelf for more than a week. Pinholes are gas still leaving the body: bisque hotter or add a soak at peak. Crazing is a fit problem between glaze and body and will not be cured by refiring; change the recipe.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes_heldout / h09

what mesh sieve should I use

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **return**. Returned: Pass twice through an 80 mesh sieve.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes_heldout / h10

how many posts per shelf

> Three posts per shelf, set in the same positions on every layer so the load carries straight down. Glazed work needs a finger's width between pieces and from the elements. Bisque can touch and can nest. Brush batt wash on the upper face of each shelf only, never the underside, where flakes fall into work below.

Observed: **ambiguous**. Returned: (no answer). Disposition: contractual ambiguity, not evidence contradiction.

Classes: multiple_owners. First limiting stage: conflict assessment. Expected defensible behavior / general repair: Retain separate owners and citations, explain compatible repetition and ancestry without selecting one.

## probes_heldout / h11

where does unmarked glaze go

> Every container carries the recipe code, the date and the mixer's initials on both lid and side. Anything unmarked goes to the quarantine shelf and is not used. A wet batch keeps for a year if the lid is tight. If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported relationship form.

Classes: unknown_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Recognize location/disposition with the subject and prohibition intact; unknown wording must remain unsupported.

## probes_heldout / h12

how deep should I spread slurry on the plaster batt

> Let scraps go bone dry, then slake them in a bucket of water overnight without stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.

Observed: **return**. Returned: Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes_heldout / h13

how do I check the coat with a pin

> Wax the foot ring and let it dry. Hold with tongs, dip for a count of three and lift out with a twist to shed the drip. The coat should be the thickness of a postcard: scratch through with a pin to check. Touch up tong marks with a brush once the surface has lost its shine. Sponge the foot clean before the piece goes on a board.

Observed: **return**. Returned: The coat should be the thickness of a postcard: scratch through with a pin to check.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes_heldout / h14

when do spy hole bungs go back in

> Switch the extractor on before the kiln and leave it running until the pyrometer reads under 200 C. Wax burn-off and sulphur from some clays come off between 200 C and 700 C; keep the kiln room door shut and work elsewhere during that stretch. Spy hole bungs stay in after 600 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_heldout / h15

what size burn needs the minor injuries unit

> Use the leather gauntlets for anything over 60 C and set work down on the kiln shelf offcuts, never on a wooden bench. For a burn, twenty minutes under cool running water straight away, then cover loosely with cling film. Anything larger than a coin, or blistered, goes to the minor injuries unit.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: legitimate refusal: expected page excluded by not-for injury.

Classes: conditions, provenance_exclusion. First limiting stage: interpretation. Expected defensible behavior / general repair: Retain the restriction and explain eligibility; do not bypass not-for to meet a document label.

## probes_heldout / h16

which bodies must be kept in separate buckets

> Let scraps go bone dry, then slake them in a bucket of water overnight without stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.

Observed: **return**. Returned: Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes_heldout / h20

how do I control dust

> Never sweep or brush dry. Wet mop the floor and sponge the benches at the end of each session. Wear a fitted P3 half-mask whenever a bag of powder is open; paper masks do not stop respirable silica. Wash aprons weekly rather than shaking them out.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_heldout / h21

what temperature for bisque

> Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_heldout / h22

weighing out a glaze recipe

> Put the water in the bucket first, then the powders, so nothing cakes on the bottom. Leave it to slake for twenty minutes before stirring. Pass twice through an 80 mesh sieve. Adjust to 1.45 on the hydrometer for dipping. Write the date and the recipe code on the lid and on the side.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c01

glaze firing schedule for the gas kiln

> Light both burners on low and candle for an hour. Begin body reduction at 900 C by closing the damper to a finger's width until a soft flame shows at the spy hole. Return to neutral at 1000 C and climb to 1222 C over five hours. Finish with ten minutes of oxidation to clear the atmosphere.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c02

wedging before throwing on the wheel

> Ram's head for small amounts, spiral for anything over two kilos. Thirty turns is a minimum. Cut the lump with a wire and look at the face: it should be one even colour with no holes. Wedge on canvas or bare wood, not on plaster, which chips into the clay and blows out in the kiln.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c03

handles pulling away while drying

> Dry slowly and evenly. Turn pots onto their rims once they will hold their shape, so the base catches up with the lip. Wrap handles and joins loosely for the first day. A piece is ready when it no longer feels cool against the cheek. Thick sculpture needs two weeks, not two days.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported situation inference.

Classes: situation_to_relation. First limiting stage: interpretation. Expected defensible behavior / general repair: Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.

## probes_adjacent / c04

which clay is for sculpture

> White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. Red earthenware, RE, matures at cone 04 and must never go in a cone 6 firing, where it slumps and fuses to the shelf. Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.

Observed: **return**. Returned: Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.. Disposition: supported complete source claim.

Classes: supported. First limiting stage: none. Expected defensible behavior / general repair: No question-specific repair. Keep exact quote and qualifiers.

## probes_adjacent / c05

drying slurry on plaster

> Let scraps go bone dry, then slake them in a bucket of water overnight without stirring. Pour off the clear water. Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c06

wax on the foot ring before dipping

> Wax the foot ring and let it dry. Hold with tongs, dip for a count of three and lift out with a twist to shed the drip. The coat should be the thickness of a postcard: scratch through with a pin to check. Touch up tong marks with a brush once the surface has lost its shine. Sponge the foot clean before the piece goes on a board.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c07

vent fan and smell during a firing

> Switch the extractor on before the kiln and leave it running until the pyrometer reads under 200 C. Wax burn-off and sulphur from some clays come off between 200 C and 700 C; keep the kiln room door shut and work elsewhere during that stretch. Spy hole bungs stay in after 600 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.

## probes_adjacent / c08

bisque firing schedule in the electric kiln

> Load bone-dry ware only. Climb 100 C per hour to 600 C so chemically bound water can leave without blowing the walls out, then 150 C per hour to 1000 C, which is cone 06. Soak ten minutes. Leave the lid shut until the pyrometer reads under 100 C.

Observed: **not_in_corpus**. Returned: (no answer). Disposition: deliberately unsupported free-form procedure.

Classes: procedure. First limiting stage: interpretation. Expected defensible behavior / general repair: Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.
