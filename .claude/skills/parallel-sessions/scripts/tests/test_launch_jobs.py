"""
Test the launcher that starts each job's session only once it holds a slot.

These tests run the launcher with a stand-in for `claude` that records when
each session starts and ends, and check how many run at once, how soon a job
starts once a slot frees, and that every slot is freed when its session ends.

They own the launcher checks; the slot store belongs to the slots tests.
"""

import contextlib
import io
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
from launch_jobs import (
    DEFAULT_POLL_SECONDS,
    DEFAULT_RESUME_TRIES,
    DEFAULT_RESUME_WAIT_SECONDS,
    Job,
    Launcher,
    cut_by_connection,
    find_session_id,
    main,
)
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
RESUME_WAIT_SECONDS = 0.3
RESUME_TRIES = 2
WORKING_ROW = "| job-0 | sonnet | branch-0 | job-0.jsonl | working |"


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
        self.launch(self.jobs(LIMIT, ("crash",)))

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

        first_line = Path(job.log).read_text().splitlines()[0]
        self.assertEqual(str(checkout.resolve()), json.loads(first_line)["cwd"])

    def launch(self, jobs: list[Job]) -> int:
        return Launcher(self.pool, str(self.claude), POLL_SECONDS).run(jobs)

    def jobs(
        self, count: int, outcomes: tuple[str, ...] = ("ok",)
    ) -> list[Job]:
        return [
            Job(
                f"job-{number}",
                str(self.root),
                *write_job_files(self.root, f"job-{number}", outcomes),
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


class ResumeTest(unittest.TestCase):
    """Tests for resuming a session that a lost connection cut off."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.events = self.root / "events.txt"
        self.events.touch()
        self.claude = write_stand_in(self.root, self.events)
        self.progress = self.root / "progress.md"
        self.progress.write_text(
            f"| holder | model | branch | log | state |\n{WORKING_ROW}\n"
        )
        self.pool = SlotPool(
            Cache(str(self.root / "slots")), LIMIT, LONG_EXPIRY_SECONDS
        )

    def tearDown(self):
        self.pool.store.close()
        self.folder.cleanup()

    def test_a_connection_error_exit_is_resumed_by_its_session_id(self):
        failures = self.launch(("cut", "ok"))

        resume = self.resumes()[0]
        self.assertEqual(
            (0, 1, "session-job-0"),
            (failures, len(self.resumes()), resume["session"]),
        )

    def test_the_resume_message_tells_it_to_check_what_it_committed(self):
        self.launch(("cut", "ok"))

        self.assertIn("already committed", self.resumes()[0]["message"])

    def test_a_resume_waits_before_it_starts(self):
        self.launch(("cut", "ok"))

        starts, ends = self.times("start"), self.times("end")
        self.assertGreaterEqual(starts[1] - ends[0], RESUME_WAIT_SECONDS)

    def test_each_wait_is_three_times_the_one_before(self):
        self.launch(("cut", "cut", "ok"))

        starts, ends = self.times("start"), self.times("end")
        second_wait = starts[2] - ends[1]
        self.assertGreaterEqual(second_wait, 3 * RESUME_WAIT_SECONDS)

    def test_a_job_holds_no_slot_while_it_waits_to_resume(self):
        launcher = threading.Thread(target=self.launch, args=[("cut", "ok")])
        launcher.start()
        self.wait_for_first_exit()
        time.sleep(RESUME_WAIT_SECONDS / 3)

        held_while_waiting = self.pool.held_claims()
        launcher.join()

        self.assertEqual([], held_while_waiting)

    def test_a_resume_starts_only_once_its_slot_is_held(self):
        launcher = threading.Thread(target=self.launch, args=[("cut", "ok")])
        launcher.start()
        self.wait_for_first_exit()
        time.sleep(POLL_SECONDS * 2)
        for number in range(LIMIT):
            while self.pool.claim(f"outside-{number}") is None:
                time.sleep(POLL_SECONDS)
        time.sleep(RESUME_WAIT_SECONDS + SESSION_SECONDS)

        resumed_while_waiting = self.resumes()
        self.pool.release("outside-0")
        launcher.join()

        self.assertEqual(([], 1), (resumed_while_waiting, len(self.resumes())))

    def test_a_resumed_session_writes_its_own_log_and_the_first_is_kept(self):
        jobs = self.job(("cut", "ok"))
        self.launch_jobs(jobs)

        first = Path(jobs[0].log).read_text()
        resumed = (self.root / "job-0.resume-1.jsonl").read_text()
        self.assertEqual(
            (True, True), ("result" in first, "session_id" in resumed)
        )

    def test_a_connection_error_with_no_session_id_starts_from_its_brief(self):
        failures = self.launch(("cut-early", "ok"))

        self.assertEqual(
            (0, 2, []), (failures, len(self.times("start")), self.resumes())
        )

    def test_a_job_past_its_try_limit_is_marked_failed(self):
        failures = self.launch(("cut", "cut", "cut", "ok"))

        self.assertEqual(
            (1, RESUME_TRIES + 1, True),
            (failures, len(self.times("start")), self.is_marked_failed()),
        )

    def test_a_restart_from_the_brief_uses_up_a_try(self):
        failures = self.launch(("cut-early", "cut-early", "cut-early", "ok"))

        self.assertEqual(
            (1, RESUME_TRIES + 1, True),
            (failures, len(self.times("start")), self.is_marked_failed()),
        )

    def test_an_exit_for_another_reason_is_marked_failed_and_not_retried(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            failures = self.launch(("crash", "ok"))

        self.assertEqual(
            (1, 1, True, True),
            (
                failures,
                len(self.times("start")),
                self.is_marked_failed(),
                "job-0 failed" in output.getvalue(),
            ),
        )

    def test_a_row_already_merged_or_canceled_keeps_its_state(self):
        for state in ("merged", "canceled"):
            with self.subTest(state=state):
                self.progress.write_text(
                    f"| holder | state |\n| job-0 | {state} |\n"
                )

                self.launch(("crash",))

                self.assertEqual(
                    f"| job-0 | {state} |",
                    self.progress.read_text().splitlines()[1],
                )

    def test_a_log_that_is_not_valid_text_can_still_be_read(self):
        log = self.root / "bad.jsonl"
        errors = self.root / "bad.err"
        log.write_bytes(b'\xff{"session_id": "abc"}\n\xfe')
        errors.write_text("")

        self.assertEqual(
            (None, False),
            (find_session_id(log), cut_by_connection(log, errors)),
        )

    def test_a_clean_exit_is_neither_resumed_nor_marked_failed(self):
        failures = self.launch(("ok", "ok"))

        self.assertEqual(
            (0, 1, [], False),
            (
                failures,
                len(self.times("start")),
                self.resumes(),
                self.is_marked_failed(),
            ),
        )

    def test_the_defaults_leave_hours_for_a_connection_to_come_back(self):
        hours = sum(
            DEFAULT_RESUME_WAIT_SECONDS * 3**number
            for number in range(DEFAULT_RESUME_TRIES)
        ) / (60 * 60)

        self.assertGreater(hours, 8)

    def launch(self, outcomes: tuple[str, ...]) -> int:
        return self.launch_jobs(self.job(outcomes))

    def launch_jobs(self, jobs: list[Job]) -> int:
        return Launcher(
            self.pool,
            str(self.claude),
            POLL_SECONDS,
            RESUME_TRIES,
            RESUME_WAIT_SECONDS,
            self.progress,
        ).run(jobs)

    def job(self, outcomes: tuple[str, ...]) -> list[Job]:
        return [
            Job(
                "job-0",
                str(self.root),
                *write_job_files(self.root, "job-0", outcomes),
            )
        ]

    def wait_for_first_exit(self):
        while not self.times("end"):
            time.sleep(POLL_SECONDS / 5)

    def resumes(self) -> list[dict]:
        file = self.root / "resumes.jsonl"
        if not file.exists():
            return []
        return [json.loads(line) for line in file.read_text().splitlines()]

    def times(self, kind: str) -> list[float]:
        return [
            float(at)
            for tag, _, at in (
                line.split() for line in self.events.read_text().splitlines()
            )
            if tag == kind
        ]

    def is_marked_failed(self) -> bool:
        return self.progress.read_text().splitlines()[1].endswith("| failed |")


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

    def test_it_takes_the_resume_tries_wait_and_progress_file_as_options(self):
        brief, model, effort, log, errors = write_job_files(
            self.root, "job-0", ("cut", "cut")
        )
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
        progress = self.root / "progress.md"
        progress.write_text(WORKING_ROW + "\n")

        result = CliRunner().invoke(
            main,
            [
                "--store",
                str(self.root / "slots"),
                "--poll",
                str(POLL_SECONDS),
                "--claude",
                str(self.claude),
                "--resume-tries",
                "1",
                "--resume-wait",
                str(POLL_SECONDS),
                "--progress",
                str(progress),
                str(jobs_file),
            ],
        )

        self.assertEqual(
            (1, "| failed |", "0 of 1 jobs finished"),
            (
                result.exit_code,
                progress.read_text().strip()[-10:],
                result.output.strip().splitlines()[-1],
            ),
        )


def write_stand_in(folder: Path, events: Path) -> Path:
    script = folder / "claude"
    script.write_text(
        f"#!{sys.executable}\n"
        "import json\n"
        "import sys\n"
        "import time\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "resuming = '--resume' in args\n"
        "session = args[args.index('--resume') + 1] if resuming else None\n"
        "holder = session.removeprefix('session-') if resuming "
        "else args[1].split()[0]\n"
        f"events = Path({str(events)!r})\n"
        "seconds = float((events.parent / f'{holder}.md').read_text().split()[1])\n"
        "def record(kind):\n"
        "    with events.open('a') as file:\n"
        "        file.write(f'{kind} {holder} {time.time()}\\n')\n"
        "plan = (events.parent / f'{holder}.plan').read_text().split()\n"
        "attempt = sum(\n"
        "    1 for line in events.read_text().splitlines()\n"
        "    if line.split()[:2] == ['start', holder]\n"
        ")\n"
        "outcome = plan[min(attempt, len(plan) - 1)]\n"
        "record('start')\n"
        "if resuming:\n"
        "    with (events.parent / 'resumes.jsonl').open('a') as file:\n"
        "        file.write(json.dumps({'holder': holder, 'session': session, "
        "'message': args[1]}) + '\\n')\n"
        "if outcome != 'cut-early':\n"
        "    print(json.dumps({'type': 'system', 'session_id': "
        "f'session-{holder}', 'cwd': str(Path.cwd())}), flush=True)\n"
        "time.sleep(seconds)\n"
        "record('end')\n"
        "if outcome == 'cut':\n"
        "    print(json.dumps({'type': 'result', 'is_error': True, "
        "'result': \"Can't reach the API server\"}))\n"
        "    sys.exit(1)\n"
        "if outcome == 'cut-early':\n"
        '    print("Can\'t reach the API server", file=sys.stderr)\n'
        "    sys.exit(1)\n"
        "sys.exit(3 if outcome == 'crash' else 0)\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def write_job_files(
    root: Path, name: str, outcomes: tuple[str, ...] = ("ok",)
) -> list[str]:
    brief = root / f"{name}.md"
    brief.write_text(f"{name} {SESSION_SECONDS}")
    (root / f"{name}.plan").write_text(" ".join(outcomes))
    return [
        str(brief),
        "sonnet",
        "high",
        str(root / f"{name}.jsonl"),
        str(root / f"{name}.err"),
    ]


if __name__ == "__main__":
    unittest.main()
