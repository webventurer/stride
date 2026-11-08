"""
Test the shared slot pool for parallel sessions.

These tests check that slots are handed out and returned correctly, also
when several processes ask at once, and that the command works.

They own the slots module checks; running the sessions belongs to the
skill.
"""

import multiprocessing
import subprocess
import tempfile
import time
import unittest
from collections.abc import Sequence
from multiprocessing.process import BaseProcess
from multiprocessing.queues import Queue
from multiprocessing.synchronize import Barrier
from pathlib import Path

from click.testing import CliRunner, Result
from diskcache import Cache
from slots import SlotPool, main, shared_store_path

AUTHOR_CONFIG = ("-c", "user.name=Test", "-c", "user.email=test@example.com")
LIMIT = 3
SHORT_EXPIRY_SECONDS = 0.5
LONG_EXPIRY_SECONDS = 60
CONTENDER_COUNT = 8
SINGLE_SLOT_LIMIT = 1
RENEWAL_COUNT = 3
CLI_EXPIRY_SECONDS = 1
CLI_LAPSE_WAIT_SECONDS = CLI_EXPIRY_SECONDS * 1.5


class SlotPoolTest(unittest.TestCase):
    """Tests for a pool of slots shared by separate processes."""

    def setUp(self):
        self.store = tempfile.TemporaryDirectory()
        self.pool = SlotPool(Cache(self.store.name), LIMIT, LONG_EXPIRY_SECONDS)

    def tearDown(self):
        self.pool.store.close()
        self.store.cleanup()

    def test_claim_gives_a_slot_to_exactly_limit_processes_at_once(self):
        claimed = self.claim_from_simultaneous_processes()

        held = [slot for slot in claimed if slot is not None]

        self.assertEqual(LIMIT, len(held))

    def claim_from_simultaneous_processes(self) -> list[int | None]:
        context = multiprocessing.get_context("spawn")
        starting_line, results = (
            context.Barrier(CONTENDER_COUNT),
            context.Queue(),
        )
        workers = [
            context.Process(
                target=claim_when_all_are_ready,
                args=(self.store.name, f"job-{number}", starting_line, results),
            )
            for number in range(CONTENDER_COUNT)
        ]
        run_to_completion(workers)
        return [results.get() for _ in workers]

    def test_claim_returns_none_when_every_slot_is_held(self):
        self.fill_every_slot()

        slot = self.pool.claim("job-late")

        self.assertIsNone(slot)

    def fill_every_slot(self):
        for number in range(LIMIT):
            self.pool.claim(f"job-{number}")

    def test_claim_returns_the_slot_a_holder_already_has(self):
        first = self.pool.claim("job-1")

        second = self.pool.claim("job-1")

        self.assertEqual(first, second)

    def test_release_frees_the_slot_for_another_holder(self):
        self.fill_every_slot()
        self.pool.release("job-0")

        slot = self.pool.claim("job-late")

        self.assertIsNotNone(slot)

    def test_release_reports_a_holder_with_no_slot(self):
        released = self.pool.release("job-unknown")

        self.assertFalse(released)

    def test_claim_lapses_when_it_is_not_renewed(self):
        pool = SlotPool(
            self.pool.store, SINGLE_SLOT_LIMIT, SHORT_EXPIRY_SECONDS
        )
        pool.claim("job-stuck")
        time.sleep(SHORT_EXPIRY_SECONDS * 2)

        slot = pool.claim("job-waiting")

        self.assertEqual(0, slot)

    def test_renew_keeps_a_claim_past_its_first_expiry(self):
        pool = SlotPool(
            self.pool.store, SINGLE_SLOT_LIMIT, SHORT_EXPIRY_SECONDS
        )
        pool.claim("job-alive")
        for _ in range(RENEWAL_COUNT):
            renew_after_a_pause(pool, "job-alive")

        slot = pool.claim("job-waiting")

        self.assertIsNone(slot)

    def test_renew_reports_a_holder_whose_claim_lapsed(self):
        pool = SlotPool(
            self.pool.store, SINGLE_SLOT_LIMIT, SHORT_EXPIRY_SECONDS
        )
        pool.claim("job-stuck")
        time.sleep(SHORT_EXPIRY_SECONDS * 2)

        renewed = pool.renew("job-stuck")

        self.assertFalse(renewed)

    def test_held_claims_lists_each_holder_with_when_it_lapses(self):
        self.pool.claim("job-1")
        before = time.time()

        claims = self.pool.held_claims()

        self.assertEqual(["job-1"], [claim.holder for claim in claims])
        self.assertGreater(claims[0].lapses_at, before)


class SlotCommandsTest(unittest.TestCase):
    """Tests for the slot store's command line."""

    def setUp(self):
        self.store = tempfile.TemporaryDirectory()
        self.options = ["--store", self.store.name, "--limit", "1"]

    def tearDown(self):
        self.store.cleanup()

    def test_claim_exits_with_failure_when_no_slot_is_free(self):
        self.run_command("claim", "job-1")

        result = self.run_command("claim", "job-2")

        self.assertEqual(1, result.exit_code)

    def test_status_names_each_holder_with_when_it_lapses(self):
        self.run_command("claim", "job-1")

        result = self.run_command("status")

        self.assertIn("slot 0: job-1, lapses at", result.output)

    def test_renew_exits_with_failure_for_a_holder_with_no_slot(self):
        result = self.run_command("renew", "job-unknown")

        self.assertEqual(1, result.exit_code)

    def test_release_frees_the_slot_for_the_next_claim(self):
        self.run_command("claim", "job-1")
        self.run_command("release", "job-1")

        result = self.run_command("claim", "job-2")

        self.assertEqual(0, result.exit_code)

    def test_expiry_sets_how_long_a_claim_lasts(self):
        self.options += ["--expiry", str(CLI_EXPIRY_SECONDS)]
        self.run_command("claim", "job-1")
        time.sleep(CLI_LAPSE_WAIT_SECONDS)

        result = self.run_command("claim", "job-2")

        self.assertEqual(0, result.exit_code)

    def run_command(self, *arguments: str) -> Result:
        return CliRunner().invoke(main, [*self.options, *arguments])


class SharedStorePathTest(unittest.TestCase):
    """Tests for finding one slot store from any checkout of a repo."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.main = Path(self.folder.name, "repo")
        self.worktree = Path(self.folder.name, "job-1")
        create_repo_with_worktree(self.main, self.worktree)

    def tearDown(self):
        self.folder.cleanup()

    def test_shared_store_path_is_the_same_from_a_worktree(self):
        from_main = shared_store_path(self.main)

        from_worktree = shared_store_path(self.worktree)

        self.assertEqual(from_main, from_worktree)

    def test_shared_store_path_sits_under_the_main_checkout(self):
        store = shared_store_path(self.worktree)

        self.assertEqual(self.main.resolve() / "work" / "slots", store)


def create_repo_with_worktree(main_checkout: Path, worktree: Path):
    main_checkout.mkdir()
    git(main_checkout, "init", "--quiet")
    git(
        main_checkout,
        *AUTHOR_CONFIG,
        "commit",
        "--allow-empty",
        "-m",
        "start",
        "--quiet",
    )
    git(main_checkout, "worktree", "add", "--quiet", str(worktree))


def git(directory: Path, *arguments: str):
    subprocess.run(["git", "-C", str(directory), *arguments], check=True)


def run_to_completion(workers: Sequence[BaseProcess]):
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()


def renew_after_a_pause(pool: SlotPool, holder: str):
    time.sleep(SHORT_EXPIRY_SECONDS / 2)
    pool.renew(holder)


def claim_when_all_are_ready(
    store_folder: str, holder: str, starting_line: Barrier, results: Queue
):
    pool = SlotPool(Cache(store_folder), LIMIT, LONG_EXPIRY_SECONDS)
    starting_line.wait()
    results.put(pool.claim(holder))


if __name__ == "__main__":
    unittest.main()
