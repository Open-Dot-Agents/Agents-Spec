# Command hook example

This example selects only the `hooks` profile. The `SessionStart` command
writes `.oda-hook-ran` in the native session's working directory. It requires
Python 3. It does not return a permission decision.

Copy this example to a separate directory. From that directory, use a freshly
built `agents` binary on `PATH`:

```sh
agents validate --root .
agents plan --vendor codex --root . --format json
agents apply --vendor codex --root .
agents plan --vendor codex --root . --check
```

Replace `codex` with `copilot` to test Copilot. Start a new native session from
this directory and check `.oda-hook-ran`. Configuration checks alone do not
prove that the native harness ran the hook. Workbench tests check this behavior
with exact harness versions and execution markers.

To remove the owned hook, set `profiles` to `[]` in `.agents/manifest.json`:

```sh
agents plan --vendor codex --root . --format json
agents apply --vendor codex --root .
agents plan --vendor codex --root . --check
```

Remove the old marker file before starting a new session to check removal.
Repeat the removal for each vendor to which you applied the example.
The canonical catalogue can remain in place for later use.

Copilot also accepts `disableAllHooks: true` in the canonical catalogue.
Codex and Claude refuse this setting because the adapter cannot preserve its
catalogue scope. A refused apply leaves earlier native hooks unchanged.
Profile removal is the common deactivation workflow. Claude preserves all
unrelated settings when it removes the owned `hooks` field.

Omitted or zero `timeoutSec` selects the native default; positive values set a
timeout in seconds. The example uses 5 seconds. Omit `matcher` to avoid native
matcher differences. Hook input, tool names, and output decisions remain
native; this example does not depend on them.
