python3 -m venv .venv
. .venv/bin/activate
python -c "import urllib.request; urllib.request.urlretrieve('https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/downloads/mplpb-native.zip', 'mplpb-native.zip')"
python -m zipfile -e mplpb-native.zip mplpb-native
python -m pip install --no-index mplpb-native/combined_mplpb-2.1.0rc1-py3-none-any.whl
mplpb-combined write demo-ledger --title "Museum hours" --scope "museum hours" --body "Opening time: 09:00."
mplpb-combined ask demo-ledger "When does the museum open?" --record-id DOC-0001 --field "Opening time"
mplpb-combined ask demo-ledger "When does the museum close?" --record-id DOC-0001 --field "Closing time"
