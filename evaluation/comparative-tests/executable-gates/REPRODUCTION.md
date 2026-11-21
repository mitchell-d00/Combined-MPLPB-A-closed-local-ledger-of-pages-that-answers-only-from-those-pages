# Executable Gates comparison

Last reviewed: 2026-11-21.

Mitchell D. McPhetridge’s paper tests where rules are enforced in two local fixtures. The author’s ZIP, Markdown, PDF, scripts and raw results are preserved byte for byte. The [Markdown](Executable_Gates_and_Human-Maintained_Indexing.md), [PDF](Executable_Gates_and_Human-Maintained_Indexing.pdf) and [original ZIP](Executable_Gates_paper.zip) contain the original wording.

## Reproduced results

The submitted harness ran twice against MPLPB commit `6ba371ca07dd9269f28af762ed1971ad484fb6b5` using Python 3.12.14 and Git 2.56.1 on Linux. Both runs agreed byte for byte, and all probe fields matched the author’s Python 3.13.18 run. The Git comparison replayed with two disposable local repositories. [MPLPB replay](reproduction/mplpb-results.json) · [Git readbacks](reproduction/git-results.txt) · [Author’s raw results](probes/results.json)

| Fixture | Observed result |
| --- | --- |
| MPLPB supported and authorized controls | 7/7 dispatched once, wrote a marker and appended two events each. |
| MPLPB unsupported or unauthorized variants | 7/7 were denied before dispatch, with no marker, adapter call or new event. |
| Git with a README rule | The push succeeded, the server head changed and the edited file arrived. |
| Git with the same rule in a pre-receive hook | The push was rejected, and the server head and file stayed the same. |

## Assessment

The strongest part of the paper is its direct readback. It counts SQLite events and checks the file produced by the fixture adapter. It also reads the Git server’s head and file contents. The paired controls make the result easy to interpret.

In Section 5, P1 through P5 hold the seat’s **grant** fixed. The computed **permission** changes from `allowed` to `blocked` as support changes. P7 isolates a missing tool grant while the claim stays supported. The reported zero-event denials concern the observed pre-dispatch cases. The paper assumes complete mediation and uses one adapter, one source fixture and one local Git edit. Hosted branch policies, other tools, human review practices and native OOCC behavior remain outside these measurements.

The [dispatch enforcement follow-up](../dispatch-enforcement/README.md) expands the tested interfaces and records the outcome of a source change after reservation. It keeps the original pre-dispatch denial counts in their measured scope.

## Replay

The verifier requires a separate, clean MPLPB checkout at the recorded revision. The Git comparison uses disposable local repositories. Run from this package directory and give the verifier a fresh output path.

```sh
sha256sum -c SHA256SUMS
git clone https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages /tmp/mplpb-gates
git -C /tmp/mplpb-gates switch --detach 6ba371ca07dd9269f28af762ed1971ad484fb6b5
python3 -I -B verify.py /tmp/mplpb-gates /tmp/executable-gates-replay
```

[Verifier](verify.py) · [Original reproduction instructions](README.md)
