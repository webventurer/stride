"""
Test the launcher that starts each job's session only once it holds a slot.

These tests run the launcher with a stand-in for `claude` that records when
each session starts and ends, and check how many run at once, how soon a job
starts once a slot frees, and that every slot is freed when its session ends.

They own the launcher checks; the slot store belongs to the slots tests.
"""

import json
import stat
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from click.testing import CliRunner
from diskcache import Cache
from launch_jobs import DEFAULT_POLL_SECONDS, Job, Launcher, main
from slots import SlotPool

LIMIT = 2
JOB_COUNT = 4
POLL_SECONDS = 0.05
SESSION_SECONDS = 0.4
LONG_EXPIRY_SECONDS = 60
SHORT_EXPIRY_SECONDS = 0.5
START_ALLOWANCE_SECONDS = 1.0
MINUTE_SECONDS = 60
SINGLE_SLOT_LIMIT = 1


class LauncherTest(unittest.TestCase):
    """Tests for starting sessions as slots become free."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.events = self.root / "events.txt"
        self.events.touch()
        self.claude = write_stand_in(self.root, self.events)
        self.pool = SlotPool(
            Cache(str(self.root / "slots")), LIMIT, LONG_EXPIRY_SECONDS
        )

    def tearDown(self):
        self.pool.store.close()
        self.folder.cleanup()

    def test_no_more_sessions_run_at_once_than_there_are_slots(self):
        self.launch(self.jobs(JOB_COUNT))

        self.assertEqual(LIMIT, self.most_sessions_running_at_once())

    def test_every_job_gets_a_session(self):
        self.launch(self.jobs(JOB_COUNT))

        self.assertEqual(JOB_COUNT, len(self.times_of("start")))

    def test_jobs_start_in_the_order_given(self):
        one_slot = SlotPool(
            self.pool.store, SINGLE_SLOT_LIMIT, LONG_EXPIRY_SECONDS
        )
        Launcher(one_slot, str(self.claude), POLL_SECONDS).run(
            self.jobs(JOB_COUNT)
        )

        starts = self.times_of("start")

        self.assertEqual(sorted(starts), sorted(starts, key=starts.get))

    def test_a_job_starts_soon_after_a_running_session_exits(self):
        self.launch(self.jobs(JOB_COUNT))

        starts, ends = self.times_of("start"), self.times_of("end")

        waited = starts["job-2"] - min(ends.values())
        self.assertTrue(0 <= waited < START_ALLOWANCE_SECONDS)

    def test_a_job_starts_soon_after_another_holder_releases_its_slot(self):
        self.fill_every_slot()
        released_at = time.time() + SESSION_SECONDS
        threading.Timer(
            SESSION_SECONDS, self.pool.release, args=["outside-0"]
        ).start()

        self.launch(self.jobs(1))

        started_at = self.times_of("start")["job-0"]
        self.assertLess(started_at - released_at, START_ALLOWANCE_SECONDS)

    def test_a_job_starts_soon_after_another_holders_claim_lapses(self):
        pool = SlotPool(self.pool.store, LIMIT, SHORT_EXPIRY_SECONDS)
        for number in range(LIMIT):
            pool.claim(f"outside-{number}")
        lapses_at = time.time() + SHORT_EXPIRY_SECONDS

        self.launch(self.jobs(1))

        started_at = self.times_of("start")["job-0"]
        self.assertLess(started_at - lapses_at, START_ALLOWANCE_SECONDS)

    def test_a_job_waits_while_every_slot_is_held(self):
        self.fill_every_slot()
        launcher = threading.Thread(target=self.launch, args=[self.jobs(1)])
        launcher.start()
        time.sleep(SESSION_SECONDS)

        started_while_waiting = self.times_of("start")
        self.pool.release("outside-0")
        launcher.join()

        self.assertEqual({}, started_while_waiting)

    def test_the_default_wait_between_checks_is_well_inside_a_minute(self):
        self.assertLessEqual(DEFAULT_POLL_SECONDS, MINUTE_SECONDS / 2)

    def test_a_session_that_crashes_still_frees_its_slot(self):
        self.launch(self.jobs(LIMIT, outcome="crash"))

        self.assertEqual([], self.pool.held_claims())

    def test_a_session_that_exits_normally_frees_its_slot(self):
        self.launch(self.jobs(LIMIT))

        self.assertEqual([], self.pool.held_claims())

    def test_a_session_that_released_its_own_slot_leaves_the_slot_free(self):
        threading.Timer(
            SESSION_SECONDS / 2, self.pool.release, args=["job-0"]
        ).start()

        failures = self.launch(self.jobs(1))

        self.assertEqual((0, []), (failures, self.pool.held_claims()))

    def test_a_job_that_cannot_start_frees_its_slot_and_the_rest_still_run(
        self,
    ):
        missing = Job(
            "job-x",
            str(self.root / "nowhere"),
            *write_job_files(self.root, "x"),
        )

        failures = self.launch([missing, *self.jobs(1)])

        self.assertEqual(
            (1, [], 1),
            (failures, self.pool.held_claims(), len(self.times_of("start"))),
        )

    def test_a_session_runs_in_its_jobs_checkout_and_writes_its_log(self):
        checkout = self.root / "worktree"
        checkout.mkdir()
        job = self.jobs(1)[0]
        job.checkout = str(checkout)

        self.launch([job])

        self.assertEqual(
            str(checkout.resolve()), Path(job.log).read_text().strip()
        )

    def launch(self, jobs: list[Job]) -> int:
        return Launcher(self.pool, str(self.claude), POLL_SECONDS).run(jobs)

    def jobs(self, count: int, outcome: str = "ok") -> list[Job]:
        return [
            Job(
                f"job-{number}",
                str(self.root),
                *write_job_files(self.root, f"job-{number}", outcome),
            )
            for number in range(count)
        ]

    def fill_every_slot(self):
        for number in range(LIMIT):
            self.pool.claim(f"outside-{number}")

    def event_lines(self) -> list[list[str]]:
        return [line.split() for line in self.events.read_text().splitlines()]

    def times_of(self, kind: str) -> dict[str, float]:
        return {
            holder: float(at)
            for tag, holder, at in self.event_lines()
            if tag == kind
        }

    def most_sessions_running_at_once(self) -> int:
        changes = sorted(
            (float(at), 1 if tag == "start" else -1)
            for tag, _, at in self.event_lines()
        )
        running, most = 0, 0
        for _, change in changes:
            running += change
            most = max(most, running)
        return most


class LaunchCommandTest(unittest.TestCase):
    """Tests for the launcher's command line."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.events = self.root / "events.txt"
        self.events.touch()
        self.claude = write_stand_in(self.root, self.events)

    def tearDown(self):
        self.folder.cleanup()

    def test_it_runs_the_jobs_in_a_jobs_file_and_frees_every_slot(self):
        brief, model, effort, log, errors = write_job_files(self.root, "job-0")
        jobs_file = self.root / "jobs.json"
        jobs_file.write_text(
            json.dumps(
                [
                    {
                        "holder": "job-0",
                        "checkout": str(self.root),
                        "brief": brief,
                        "model": model,
                        "effort": effort,
                        "log": log,
                        "errors": errors,
                    }
                ]
            )
        )
        store = self.root / "slots"

        result = CliRunner().invoke(
            main,
            [
                "--store",
                str(store),
                "--limit",
                str(SINGLE_SLOT_LIMIT),
                "--poll",
                str(POLL_SECONDS),
                "--claude",
                str(self.claude),
                str(jobs_file),
            ],
        )

        pool = SlotPool(
            Cache(str(store)), SINGLE_SLOT_LIMIT, LONG_EXPIRY_SECONDS
        )
        self.assertEqual(
            (0, 2, []),
            (
                result.exit_code,
                len(self.events.read_text().splitlines()),
                pool.held_claims(),
            ),
        )


def write_stand_in(folder: Path, events: Path) -> Path:
    script = folder / "claude"
    script.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        "import time\n"
        "from pathlib import Path\n"
        "holder, seconds, outcome = sys.argv[2].split()\n"
        f"events = Path({str(events)!r})\n"
        "def record(kind):\n"
        "    with events.open('a') as file:\n"
        "        file.write(f'{kind} {holder} {time.time()}\\n')\n"
        "record('start')\n"
        "print(Path.cwd())\n"
        "time.sleep(float(seconds))\n"
        "record('end')\n"
        "sys.exit(3 if outcome == 'crash' else 0)\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def write_job_files(root: Path, name: str, outcome: str = "ok") -> list[str]:
    brief = root / f"{name}.md"
    brief.write_text(f"{name} {SESSION_SECONDS} {outcome}")
    return [
        str(brief),
        "sonnet",
        "high",
        str(root / f"{name}.jsonl"),
        str(root / f"{name}.err"),
    ]


if __name__ == "__main__":
    unittest.main()
