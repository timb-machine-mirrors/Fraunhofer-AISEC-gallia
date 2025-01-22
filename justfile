# SPDX-FileCopyrightText: AISEC Pentesting Team
#
# SPDX-License-Identifier: CC0-1.0

default:
    @just --list

[private]
lint-mypy:
    mypy --pretty src tests

[private]
lint-ruff-check:
    ruff check

[private]
lint-ruff-format:
    ruff format --check

[private]
lint-shellcheck:
    find tests/bats \( -iname "*.bash" -or -iname "*.bats" -or -iname "*.sh" \) | xargs shellcheck

[private]
lint-reuse:
    reuse lint

lint: lint-mypy lint-ruff-check lint-ruff-format lint-ruff-format lint-shellcheck lint-reuse

win32-lint-mypy:
    mypy --platform win32 --exclude "gallia\/log\.py" --exclude "hr" src tests

fmt:
    ruff check --fix-only
    ruff format
    find tests/bats \( -iname "*.bash" -or -iname "*.bats" -or -iname "*.sh" \) | xargs shfmt -w

run-tests: run-test-pytest run-test-bats

run-test-matrix:
    #!/usr/bin/env bash

    set -eu

    matrix=("3.11" "3.12" "3.13")
    for version in "${matrix[@]}"; do
        echo "running tests with python version: $version"
        uv sync --all-extras -p "$version"
        uv run -p "$version" just run-tests
    done

run-test-pytest:
    python -m pytest -v --cov={{ justfile_directory() }} --cov-report html tests/pytest

run-test-bats:
    ./tests/bats/run_bats.sh

gen-constants: && fmt
    #!/usr/bin/env python

    import socket

    TEMPLATE = f"""# This file has been autogenerated by `just gen-constants`.
    # !! DO NOT CHANGE MANUALLY !!

    # SPDX-FileCopyrightText: AISEC Pentesting Team
    #
    # SPDX-License-Identifier: Apache-2.0

    import struct


    CANFD_MTU = 72
    CAN_MTU = 16

    # https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/can.h
    CAN_HEADER_FMT = struct.Struct("=IBB2x")

    CANFD_BRS = 0x01
    CANFD_ESI = 0x02

    CAN_EFF_FLAG = {socket.CAN_EFF_FLAG}
    CAN_ERR_FLAG = {socket.CAN_ERR_FLAG}
    CAN_RTR_FLAG = {socket.CAN_RTR_FLAG}

    CAN_EFF_MASK = {socket.CAN_EFF_MASK}
    CAN_INV_FILTER = 0x20000000  # TODO: Add to CPython
    CAN_SFF_MASK = {socket.CAN_SFF_MASK}

    CAN_RAW = {socket.CAN_RAW}
    CAN_RAW_FD_FRAMES = {socket.CAN_RAW_FD_FRAMES}
    CAN_RAW_FILTER = {socket.CAN_RAW_FILTER}
    CAN_RAW_JOIN_FILTERS = {socket.CAN_RAW_JOIN_FILTERS}
    SOL_CAN_RAW = {socket.SOL_CAN_RAW}
    """

    with open("src/gallia/transports/_can_constants.py", "w") as f:
        f.write(TEMPLATE)

release increment:
    cz bump --increment {{ increment }}
    git push --follow-tags
    gh release create "v$(cz version -p)"

pre-release increment premode:
    cz bump --increment {{ increment }} --prerelease {{ premode }}
    git push --follow-tags
    gh release create --prerelease "v$(cz version -p)"

make-docs:
    make -C docs html

clean:
    make -C docs clean
