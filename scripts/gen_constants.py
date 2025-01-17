#!/usr/bin/env python

# SPDX-FileCopyrightText: AISEC Pentesting Team
#
# SPDX-License-Identifier: Apache-2.0

import socket

TEMPLATE = f"""# This file has been autogenerated by `make constants`.
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


def main() -> None:
    print(TEMPLATE)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
