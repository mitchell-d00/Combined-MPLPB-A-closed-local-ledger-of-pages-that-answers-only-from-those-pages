# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d0a790b0e331515f55cad8ea70d4c0a8e5e499c7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0b123d775f346c08c187b6443b8e57b30d43b0ceab73c88672fe388bd8c7de85`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty — prioritize broader ordinary-language understanding. Work locally first. Create the next Cryptid series, “Bunyip,” if that name is unused. Before changing the reader, freeze development sources, questions, expected claims, qualifications, controls and baseline outputs. Preserve question arguments, negation, modality, attribution and requested relations through interpretation. Do not use entity-specific patches or infer missing facts. Audit every recovered answer against its source. Keep original failures and frozen scores. Mitchell has authorized incremental releases with verified gains and no regressions. Existing coverage misses alone do not require perfect scores before release. Once the gains are audited and required checks pass, publish the evidence, update the PR, merge through the normal protected workflow and verify deployment. Do not bypass required checks or request the same authorization again. Keep human onboarding execution NOT_RUN until Mitchell returns actual participant results. Add a documentation/navigation pass with MPLPB, Experimental Lab and Testing and Training Apparatus entry areas; preserve implementation paths and evidence. Keep root README under180lines; specify input format. Verify the exact quick-start command in a clean setup and show its expected output.

Make broader language generalization the primary development goal. Preserve existing memory, provenance and admission behavior as regression requirements. Measure newly answerable wording on fresh cases, alongside lost support and unsupported claims. Report those gains separately from improvements to tags, layout or test infrastructure.

### Implemented scope

- Primary development goal: broader ordinary-language generalization. Fresh wording gains must be separated from source/proof-operation reach, tag/layout changes and test infrastructure; memory/provenance/admission remain regression gates. Canonical-source diagnostic attribution is post-run, source-matched and not fresh/independent evidence.
- C5 compatibility repair makes optional title metadata safe for existing body-only imports; no answer-coverage gain from this fix. Broader ordinary-language gains remain primary16→56/60 versusPR105 (20unique recoveredquestions).
- C5local development154/158andall849priorcontracts exactly preserved. Bothconsumedpacketsretain original36/42and20/24scores. New16sealedbeforeC5codepatch; openonlyaftercommittedZIPfreeze.
- RootREADME131lines, exact verifiedplain-text --body quickstart+expectedoutput/citationpath. Threeentryareas/sevendepartments mapped; legacyanchors restored; input/source paths andhumanfrozenarms unchanged.

### Validation recorded

- Both102case baselines completed in real fail-closed Bubblewrap before any native change. Main12/60positive completions; PR10516/60;42/42withhold controls on each. Originalscores50/102 and58/102 retained.
- Four main strict-key flags reflect an absent additive literal-polarity field. Separate source-scoped representation review retained; no old key/score changed.
- C1realhost102completed:98/102strict,56completions,0flags onprimarypacket. PostC1developmentWrap24:20/24,4unsupportedcompletecases caused by standaloneOnlyifscope. OriginalPRWrap16/24 has6unsupportedclaims and2positive misses. AlloriginalrawscoresandfailedC1retained.
- DefaultnamespaceC1launch102executionfailures,0readerexecutions; separatehostretrycompleted102. No unsandboxed fallback.
- C2core98/102,56/60completions,42withholds0falseflags;scope24/24. Governordevelopment14score4/14,10falseflags; retainandrejectC2.
- 849currentPRcontracts exactlyunchanged inC2; releasedmainreplaycomplete and4apparentsupportlosseschecked againstexactclaims: inventedauthorsfusedwithheaders. No lostvalidsupport identified.
- 57focused nativechecksPASS. Legacy65case sourceassessmentPASS afterretainedhost-audit correction; historical/independentsemantic NOT_RUN.
- C3primary98/102, scope24/24, governor14/14, quoted-governor2/2.11focused testsPASS. Twenty unique questionstrings recovered versus PR105 (40layout executions).
- Exact root quickstart in freshvenv frompublicwheelPASS; all90Pythonfilesmatchreleasedmainc01021c. Citation/partial/owner/ambiguity checksPASS afterretainedhostcheckcorrections.
- Main145claim-bearingcases audited:137sameclaimcontracts;8invalidheaderfusedactors corrected/withheld. C2vsPR849exactcontracts preserved.
- C3fullnative1882:one failedtest(two public preservation outcomes); rejected. C4afocused16PASS/public52restored buttitle12/16; rejected incompletefix sourceZIP+hashesretained. C4btitle16/16andidentical142development+42consumedrunscomplete withzerofalseflags.
- C3posttest76654originalarchivepayloadsbyteidentical. FullWASM/Chromium/JSHTTP/packageMCP/docs/indexPASS; initialwheelbuildbackendfailure retained,retryPASS.
- Legacyfirstattempt1000tried390complete610diskexecutionfailures; retained separately. RAMretry1000/1000complete/1000exactcontracts; originalstrictFAILunchanged, separatelyfrozen sourcecheckedv2PASS. Hostmoduleinvocationfailure retained and corrected inCI.
- C4full1884hadonebody-onlyAPIerror. Allother36gatesandpublic52PASS; all849contracts exact; legacy1000/1000completeandexact v2PASS, originalstrictFAILretained. C4sourceposttest76753payloads unchanged.
- C5frozen2APIcontrolsoriginal2errors; affected22testsPASS. C5development158andconsumed66executionscomplete, originalkeys unchanged; zerofalseflags, remainingmissespreserved. C5prior849exactcontractmatches.
- AllC4rawoutputs losslesslyretained:Zstandardreferenceencoding reconstructsexactoriginalTARSHA777ca5eebabc4a01dcabfbc31dd4c8d9c5c6deec58fd1a15452de36127a9eaec. Originalcontainerandreceiptretained.
- Primaryfresh-languageattribution(firsttwoonce-onlypackets):11uniquequestionstrings/22pairedexecutions newlysource-supportedversusreleasedmain onbaselinecanonical-supported sources;PR10514strings/28executions. Eightothersource/proof-operationreach successesversusmainreportedseparately.78canonicaldiagnosticexecutionspost-runnotadditionalgains. Originaldiagnosticv1missing-tagrequirementretained;sourcecheckedv2separate,originalreaderscoresunchanged.

### Limitations and blocked checks

- Final C5full1885native andrequiredexact-headremotechecksarepending; do not calltheearlierfailedC4fullrun alocalC5pass. PublishreviewedsourcefornormalCIthenmergeonlyafterallrequiredgatespass.
- Fourdevelopmentmisses; first42sixmisses;second24fourmisses. Originalautomatedstagesandscoresunchanged, separatemechanism/policyassessmentsretained. Fresh16notopenedbeforeZIPfreeze.
- Human/independenthistorical-semantic/preparation-blinding/outside-custodian/nativeOOCC remainNOT_RUN.

### Next steps

- Freeze final C5 committed ZIP, execute sealed16once, measure actual fresh wording/source-language gains and remaining misses without changing old inputs/keys.
- Use matched canonical-source probes to separate newly answered wording from newly admitted proof/source operations; these diagnostic repetitions are not extra recovered questions.
- Preserve memory, provenance, admission, qualifications/citations and all prior valid claims. Publish verified incremental gains and evidence toexistingPR105, run fullrequiredexactheadCI including1885native, mergeonlynormalprotectedworkflowaftergatespass, verifydeployedfingerprints.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
