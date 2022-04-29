import argparse
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter
from importlib.metadata import entry_points
from typing import Any

import argcomplete

from gallia.utils import camel_to_dash
from gallia.udscan.scanner.find_can_ids import FindCanIDsScanner
from gallia.udscan.scanner.find_endpoints import FindEndpoints
from gallia.udscan.scanner.find_iso_tp_addr import FindISOTPAddr
from gallia.udscan.scanner.scan_identifiers import ScanIdentifiers
from gallia.udscan.scanner.scan_memory_functions import ScanMemoryFunctions
from gallia.udscan.scanner.scan_reset import ScanReset
from gallia.udscan.scanner.scan_sa_dump_seeds import SaDumpSeeds
from gallia.udscan.scanner.scan_services import ScanServices
from gallia.udscan.scanner.scan_sessions import ScanSessions
from gallia.udscan.scanner.simple_dtc import SimpleDTC
from gallia.udscan.scanner.simple_ecu_reset import SimpleECUReset
from gallia.udscan.scanner.simple_get_vin import SimpleGetVin
from gallia.udscan.scanner.simple_iocbi import SimpleIOCBI
from gallia.udscan.scanner.simple_ping import SimplePing
from gallia.udscan.scanner.simple_read_by_identifier import ReadByIdentifier
from gallia.udscan.scanner.simple_read_error_log import SimpleReadErrorLog
from gallia.udscan.scanner.simple_rmba import SimpleRMBA
from gallia.udscan.scanner.simple_rtcl import SimpleRTCL
from gallia.udscan.scanner.simple_send_pdu import SimpleSendPDU
from gallia.udscan.scanner.simple_test_xcp import SimpleTestXCP
from gallia.udscan.scanner.simple_wmba import SimpleWMBA
from gallia.udscan.scanner.simple_write_by_identifier import WriteByIdentifier


# TODO: Rename classes: SimpleFoo…
# TODO: Create groups: simple, scanner, discover
# TODO: Entry points
registry = [
    FindCanIDsScanner,
    FindEndpoints,
    FindISOTPAddr,
    ReadByIdentifier,
    SaDumpSeeds,
    ScanIdentifiers,
    ScanMemoryFunctions,
    ScanReset,
    ScanServices,
    ScanSessions,
    SimpleDTC,
    SimpleECUReset,
    SimpleGetVin,
    SimpleIOCBI,
    SimplePing,
    SimpleRMBA,
    SimpleRTCL,
    SimpleReadErrorLog,
    SimpleSendPDU,
    SimpleTestXCP,
    SimpleWMBA,
    WriteByIdentifier,
]


class Formatter(ArgumentDefaultsHelpFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if (w := os.getenv("GALLIA_HELP_WIDTH")) is not None:
            kwargs["width"] = int(w)
        super().__init__(*args, **kwargs)


def get_id(cls: type) -> str:
    return cls.ID if hasattr(cls, "ID") else camel_to_dash(cls.__name__)  # type: ignore


def get_short_help(cls: type) -> str:
    return cls.SHORT_HELP if hasattr(cls, "SHORT_HELP") else cls.__doc__  # type: ignore


def get_help(cls: type) -> str:
    return cls.HELP if hasattr(cls, "HELP") else get_short_help(cls)  # type: ignore


def load_plugins() -> None:
    global registry

    all_entries = entry_points()
    for entry in all_entries["gallia_commands"]:
        registry.append(entry.load())


def main() -> None:
    load_plugins()

    parser = argparse.ArgumentParser(formatter_class=Formatter)
    subparsers = parser.add_subparsers(metavar="SCANNER")

    for cls in sorted(registry, key=lambda x: get_id(x)):
        subparser = subparsers.add_parser(
            get_id(cls),
            description=get_help(cls),
            help=get_short_help(cls),
        )
        scanner = cls(subparser)  # type: ignore
        subparser.set_defaults(func=scanner.run)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        parser.exit()

    sys.exit(args.func())
