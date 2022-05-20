# type: ignore

import argparse
import sys
from argparse import ArgumentDefaultsHelpFormatter
from importlib.metadata import entry_points

import argcomplete

from gallia.command import GalliaBase
from gallia.commands.discover.uds.find_can_ids import FindCanIDsScanner
from gallia.commands.prims.uds.simple_dtc import SimpleDTC
from gallia.commands.prims.uds.simple_ecu_reset import SimpleECUReset
from gallia.commands.prims.uds.simple_get_vin import SimpleGetVin
from gallia.commands.prims.uds.simple_iocbi import SimpleIOCBI
from gallia.commands.prims.uds.simple_ping import SimplePing
from gallia.commands.prims.uds.simple_read_by_identifier import ReadByIdentifier
from gallia.commands.prims.uds.simple_read_error_log import SimpleReadErrorLog
from gallia.commands.prims.uds.simple_rmba import SimpleRMBA
from gallia.commands.prims.uds.simple_rtcl import SimpleRTCL
from gallia.commands.prims.uds.simple_send_pdu import SimpleSendPDU
from gallia.commands.prims.uds.simple_wmba import SimpleWMBA
from gallia.commands.prims.uds.simple_write_by_identifier import WriteByIdentifier
from gallia.commands.scan.uds.scan_identifiers import ScanIdentifiers
from gallia.commands.scan.uds.scan_memory_functions import MemoryFunctionsScanner
from gallia.commands.scan.uds.scan_reset import ResetScanner
from gallia.commands.scan.uds.scan_sa_dump_seeds import SaDumpSeeds
from gallia.commands.scan.uds.scan_services import ServicesScanner
from gallia.commands.scan.uds.scan_sessions import ScanSessions
from gallia.commands.serve.virtual_ecu import VirtualECU

# from gallia.commands.prims.uds.simple_test_xcp import SimpleTestXCP

registry: list[type[GalliaBase]] = [
    FindCanIDsScanner,
    ReadByIdentifier,
    SaDumpSeeds,
    ScanIdentifiers,
    MemoryFunctionsScanner,
    ResetScanner,
    ServicesScanner,
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
    # SimpleTestXCP,
    SimpleWMBA,
    WriteByIdentifier,
    VirtualECU,
]


def load_plugins() -> None:
    eps = entry_points()
    if "gallia_commands" in eps:
        for entry in eps["gallia_commands"]:
            registry.append(entry.load())


parser_structure = {
    "discover": {
        "help": "find hosts and endpoints",
        "subcategories": {
            "uds": {
                "help": "Universal Diagnostic Services",
            },
            "xcp": {
                "help": "Universal Measurement and Calibration Protocol",
            },
        },
    },
    "prims": {
        "help": "various primitives for network protocols",
        "subcategories": {
            "uds": {
                "help": "Universal Diagnostic Services",
            },
        },
    },
    "scan": {
        "help": "scan parameters of various network protocols",
        "subcategories": {
            "uds": {
                "help": "Universal Diagnostic Services",
            },
        },
    },
    "serve": {
        "help": "utilities to spawn services",
    },
}


def build_parsers() -> dict:
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(metavar="COMMAND")
    parsers = {"parser": parser, "subparsers": subparsers}

    for category in parser_structure:  # pylint: disable=consider-using-dict-items
        p = subparsers.add_parser(category, help=parser_structure[category]["help"])
        sp = p.add_subparsers(metavar="COMMAND")
        parsers[category] = {"parser": p, "subparsers": sp}

        if "subcategories" not in parser_structure[category]:
            continue

        for subcategory in parser_structure[category]["subcategories"].keys():
            pp = sp.add_parser(
                subcategory,
                help=parser_structure[category]["subcategories"][subcategory]["help"],
            )
            spp = pp.add_subparsers(metavar="COMMAND")
            parsers[category][subcategory] = {"parser": pp, "subparsers": spp}

    return parsers


def main() -> None:
    load_plugins()

    parsers = build_parsers()

    for cls in registry:
        if cls.CATEGORY is not None:
            if cls.SUBCATEGORY is not None:
                cat_subparsers = parsers[cls.CATEGORY][cls.SUBCATEGORY]["subparsers"]
            else:
                cat_subparsers = parsers[cls.CATEGORY]["subparsers"]
        else:
            cat_subparsers = parsers["subparsers"]

        subparser = cat_subparsers.add_parser(
            cls.COMMAND,
            description=cls.__doc__,
            help=cls.SHORT_HELP,
        )
        scanner = cls(subparser)
        subparser.set_defaults(func=scanner.run)

    parser = parsers["parser"]
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        if len(sys.argv) >= 2 and (cat := sys.argv[1]) in parser_structure:
            if len(sys.argv) >= 3 and (subcat := sys.argv[2]) in parser_structure[cat]:
                parsers[cat][subcat]["parser"].print_usage()
            else:
                parsers[cat]["parser"].print_usage()
        parser.exit(1)

    sys.exit(args.func(args))
