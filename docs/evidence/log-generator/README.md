# Serialwrap Reboot Log Test Toolkit

This toolkit runs long reboot-log soak tests through serialwrap, one COM
selector per controller process. COM0 and COM1 use the same controller flow;
COM1 becomes the abnormal/fault-injection target only after installing the
boot-time fault injector.

## Install

This toolkit is run directly from a checkout. Clone the repository, then run
the local validation suite before using it on a target:

```bash
git clone https://github.com/hamanpaul/log-generator.git
cd log-generator
python3 -m pytest tests/ -q
```

## Usage

### Prerequisites

Runtime commands default to:

```bash
/home/paul_chen/.paul_tools/serialwrap
```

Override this path for testing or alternate deployments with:

```bash
export SERIALWRAP_CMD=/path/to/serialwrap
```

Before starting a controller, verify the deployed serialwrap supports event
rules and that the daemon is healthy:

```bash
/home/paul_chen/.paul_tools/serialwrap event --help
/home/paul_chen/.paul_tools/serialwrap daemon status
/home/paul_chen/.paul_tools/serialwrap event status --selector COM0
/home/paul_chen/.paul_tools/serialwrap event status --selector COM1
```

## Start minicom logging

Start minicom with extended timestamps before running a controller. The
controller identifies the active log by sending a marker through serialwrap and
searching `~/b-log/mini_COMx_*.log`.

```bash
minicom COM0 -O timestamp=extended
minicom COM1 -O timestamp=extended
```

Each controller run writes current-run state under
`/tmp/serialwrap-reboot-test.<selector>.<pid>/` so event handlers can map
events to the active minicom log and report.

## Install the COM1 fault injector

Provision the COM1 target once before abnormal soak tests:

```bash
bin/serialwrap-fault-install --selector COM1
```

The installer checks that `/etc/init.d` and `/etc/rc.d` exist on the target
before writing anything. It installs:

| Target path | Purpose |
| --- | --- |
| `/usr/sbin/serialwrap-fault-injector` | Boot-time fault injector |
| `/etc/init.d/serialwrap-fault-injector` | Init entrypoint |
| `/etc/rc.d/S50serialwrap-fault-injector` | S50 boot symlink |

The preferred transfer path uses serialwrap file transfer. If that fails, the
installer falls back to bounded base64 short writes through target commands;
the fallback avoids heredocs and large UART writes. The installer then sets
executable permissions, creates the S50 symlink, and verifies executable files
plus the symlink target.

The target injector runs silently once per boot. It has a 10% chance to inject
one of four equally selected faults:

1. Thermal notification written to `/dev/console`.
2. `ethctl eth0 phy-reset`.
3. `kill -SIGABRT` for a random `ps aux` PID greater than 4000, or exit 0 if
   no process qualifies.
4. `echo c > /proc/sysrq-trigger`.

## Run controllers

Run one controller per selector. By default, each controller runs indefinitely
until interrupted or signaled:

```bash
bin/serialwrap-reboot-controller --selector COM0
bin/serialwrap-reboot-controller --selector COM1
```

Use optional stop limits when needed:

```bash
bin/serialwrap-reboot-controller --selector COM0 --count 1
bin/serialwrap-reboot-controller --selector COM1 --hours 96
```

`--count N` stops after N completed normal reboot attempts. `--hours N` stops
after N elapsed hours. Both limits require positive integers. Without either
option, the controller keeps polling and rebooting until stopped.

The controller startup sequence checks serialwrap event support, checks daemon
health, sends a marker command through serialwrap, resolves the active minicom
log, writes `/tmp` run state, registers shared reboot-test event rules, and
enables only the selected COM matcher.

## Stop controllers and cleanup

Foreground controllers stop with `Ctrl-C`. For background controllers, find the
process ID and send SIGTERM:

```bash
ps -ef | grep 'serialwrap-reboot-controller --selector COM1'
kill -TERM <pid>
```

On normal exit, SIGINT, or SIGTERM, the controller:

1. Disables this selector's event matcher.
2. Resets this selector's event state.
3. Checks whether another COM matcher is still enabled.
4. Removes shared reboot-test event rules only when this selector was the last
   active user.
5. Removes `/tmp/serialwrap-reboot-test.<selector>.<pid>/`.

## Reports

Event reports are stored next to minicom logs:

```text
~/b-log/event-triggered_COMx_<timestamp>.md
```

There is one report per COM selector and minicom log. Reports include:

- A summary table for `brcm-therm`, `Link is Down`, `pstate`,
  `Kernel panic`, and `SMC bootloader`.
- Probabilities versus the `SMC bootloader` count. If the denominator is zero,
  probabilities are shown as `N/A`.
- An event table with minicom log name, physical log line number, trigger time,
  and event name.

The event handler maintains per-event scan cursors in `~/b-log` so repeated
payloads advance to the next matching physical log line instead of reusing an
earlier match.

## Local validation

Run the local suite before relying on a change:

```bash
python3 -m pytest tests/ -q
python3 -m py_compile bin/serialwrap-reboot-controller \
    bin/serialwrap-event-handler \
    bin/serialwrap-fault-install \
    serialwrap_reboot_test/*.py
openspec validate add-serialwrap-reboot-log-test-toolkit --strict
```

## Version

`VERSION` is the single source of truth for this repository version. Update it
together with `CHANGELOG.md` according to the `flat` policy profile before
release-oriented changes.
