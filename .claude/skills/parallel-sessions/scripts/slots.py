"""
Share a fixed number of work slots between separate sessions.

Each session claims a slot before it starts its job, renews the claim while
it works and releases it when it finishes. A claim that is not renewed
lapses, so a session that dies never keeps its slot.

It owns the slot store and nothing else; starting sessions, running jobs and
committing their work belong to the parallel-sessions skill.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import click
from diskcache import Cache

DEFAULT_LIMIT = 3
DEFAULT_EXPIRY_SECONDS = 2 * 60 * 60
STORE_FOLDER = Path("work", "slots")
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
NO_SLOT = None


@dataclass
class Claim:
    """One slot held by one session until it lapses."""

    slot: int
    holder: str
    lapses_at: float


@dataclass
class SlotPool:
    """A fixed number of slots that separate processes share."""

    store: Cache
    limit: int
    expiry_seconds: float

    def claim(self, holder: str) -> int | None:
        held = self.slot_held_by(holder)
        return held if held is not None else self.take_free_slot(holder)

    def take_free_slot(self, holder: str) -> int | None:
        return next(
            (
                slot
                for slot in range(self.limit)
                if self.store.add(
                    slot_key(slot), holder, expire=self.expiry_seconds
                )
            ),
            NO_SLOT,
        )

    def renew(self, holder: str) -> bool:
        with self.store.transact():
            slot = self.slot_held_by(holder)
            return slot is not None and self.store.touch(
                slot_key(slot), self.expiry_seconds
            )

    def release(self, holder: str) -> bool:
        with self.store.transact():
            slot = self.slot_held_by(holder)
            return slot is not None and self.store.delete(slot_key(slot))

    def slot_held_by(self, holder: str) -> int | None:
        return next(
            (
                slot
                for slot in range(self.limit)
                if self.store.get(slot_key(slot)) == holder
            ),
            NO_SLOT,
        )

    def held_claims(self) -> list[Claim]:
        entries = [
            (slot, *self.store.get(slot_key(slot), expire_time=True))
            for slot in range(self.limit)
        ]
        return [
            Claim(slot, holder, lapses_at)
            for slot, holder, lapses_at in entries
            if holder is not None
        ]


def slot_key(slot: int) -> str:
    return f"slot-{slot}"


def shared_store_path(checkout: Path) -> Path:
    common = read_git_output(
        checkout, "rev-parse", "--path-format=absolute", "--git-common-dir"
    )
    return Path(common).resolve().parent / STORE_FOLDER


def read_git_output(directory: Path, *arguments: str) -> str:
    command = ["git", "-C", str(directory), *arguments]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout.strip()


@click.group()
@click.option(
    "--store",
    "store_folder",
    type=click.Path(path_type=Path),
    help="Slot store folder; defaults to work/slots under the main checkout",
)
@click.option("--limit", default=DEFAULT_LIMIT, show_default=True)
@click.option(
    "--expiry",
    "expiry_seconds",
    default=DEFAULT_EXPIRY_SECONDS,
    show_default=True,
    help="Seconds before an unrenewed claim lapses",
)
@click.pass_context
def main(
    context: click.Context,
    store_folder: Path | None,
    limit: int,
    expiry_seconds: int,
):
    folder = store_folder or shared_store_path(Path.cwd())
    context.obj = SlotPool(Cache(str(folder)), limit, expiry_seconds)


@main.command("claim")
@click.argument("holder")
@click.pass_obj
def claim_slot(pool: SlotPool, holder: str):
    slot = pool.claim(holder)
    if slot is None:
        exit_with(EXIT_FAILURE, f"No slot free for {holder}")
    exit_with(EXIT_SUCCESS, f"{holder} holds slot {slot}")


@main.command("renew")
@click.argument("holder")
@click.pass_obj
def renew_claim(pool: SlotPool, holder: str):
    if not pool.renew(holder):
        exit_with(
            EXIT_FAILURE, f"{holder} holds no slot; its claim may have lapsed"
        )
    exit_with(
        EXIT_SUCCESS, f"{holder} renewed for {pool.expiry_seconds} seconds"
    )


@main.command("release")
@click.argument("holder")
@click.pass_obj
def release_slot(pool: SlotPool, holder: str):
    if not pool.release(holder):
        exit_with(EXIT_FAILURE, f"{holder} holds no slot")
    exit_with(EXIT_SUCCESS, f"{holder} released its slot")


@main.command("status")
@click.pass_obj
def show_status(pool: SlotPool):
    claims = pool.held_claims()
    click.echo(f"{len(claims)} of {pool.limit} slots held")
    for claim in claims:
        click.echo(claim_line(claim))


def claim_line(claim: Claim) -> str:
    lapses = time.strftime("%H:%M:%S", time.localtime(claim.lapses_at))
    return f"slot {claim.slot}: {claim.holder}, lapses at {lapses}"


def exit_with(exit_code: int, message: str):
    click.echo(message)
    raise click.exceptions.Exit(exit_code)


if __name__ == "__main__":
    main()
