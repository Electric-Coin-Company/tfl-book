# This is a bash library (to be `source`'d) which runs a user's local git hook after running the repository-managed hook.
#
# Usage: at the end of a repository-managed hook, simply do "source ~/util/run-local-hook.sh" which will introspect to find the hook name, check if the user has a local hook with that name, and then will execute it.

set -x
hookname="$(basename "$0")"
local_hook=".git/hooks/$hookname"

if [ -f "$local_hook" ]
then
  echo "Executing $local_hook"
  exec "$local_hook"
fi
