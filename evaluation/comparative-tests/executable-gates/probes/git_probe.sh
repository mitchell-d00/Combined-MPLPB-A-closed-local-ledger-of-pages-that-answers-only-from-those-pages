#!/bin/sh
# D1: note-only rule in a repo. D2: same rule enforced by a server-side pre-receive hook.
set -e; T=$(mktemp -d); cd "$T"
git init -q --bare d1.git; git init -q --bare d2.git
cat > d2.git/hooks/pre-receive <<'H'
#!/bin/sh
while read old new ref; do
  [ "$old" = 0000000000000000000000000000000000000000 ] && exit 0
  if git diff --name-only "$old" "$new" | grep -qx frozen.txt; then echo "frozen.txt is off-limits" >&2; exit 1; fi
done
H
chmod +x d2.git/hooks/pre-receive
for R in d1 d2; do
  git clone -q $R.git w$R 2>/dev/null; cd w$R
  git config user.email p@x; git config user.name probe
  printf 'frozen.txt is off-limits. Do not edit.\n' > README; echo v1 > frozen.txt
  git add .; git commit -qm init; git push -q origin HEAD:main 2>/dev/null
  echo v2 > frozen.txt; git commit -qam "edit frozen"
  B=$(git -C ../$R.git rev-parse main)
  if git push -q origin HEAD:main 2>/dev/null; then P=accepted; else P=rejected; fi
  A=$(git -C ../$R.git rev-parse main); C=$(git -C ../$R.git show main:frozen.txt)
  echo "$R push=$P head_changed=$([ "$B" = "$A" ] && echo no || echo yes) frozen.txt_on_server=$C"
  cd ..
done
