# Snapshot investigation

The preserved Simple English pins were not one normalization.

- Cat, Dog, Moon, and Photosynthesis raw pins include trailing whitespace. They do not equal the stripped extract.
- Paris had no trailing whitespace, so its raw pin equals the stripped extract.
- The served page hashed the stripped, HTML-rendered intro. That is why a Paris pin can match stripped text while Cat and Dog pins do not.
- A revision id does not bind the extract. Fresh requests in this environment matched the old raw pins. A later request can return the same revid and a different extract. That is recorded as a payload mismatch. It is not by itself a wiki-side fault.

The old corpus was not replaced.
