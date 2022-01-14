"""
    [summary]

[extended_summary]

:TODO:
- [ ] Write Module Docstring
- [ ] Remove unused imports
- [ ] Use Logger for logging execution
- [ ] Check Style for compatibility with PEP 8, 257 and 484 
"""

import argparse
import configparser
import logging
from pprint import pprint  # Pretty-printer for testing
from typing import Iterable, Sequence, Union

from findmyjob.jobsearcher import JobSearcher
from findmyjob.jobdatascraper import JobDataScraper

logger = logging.getLogger(__name__)


def parse_cli_inputs():

    argparser = argparse.ArgumentParser()
    argparser.add_argument(  # :TODO:
        "-d", "--default",
        help="Bypass other commands and run in default coniguration",
        default=None
    )

    subparser1 = argparser.add_subparsers(dest='mode', required=True)
    subp1_exec = subparser1.add_parser(
        "execute",
        help="Execute the tool",
    )
    subp1_gen = subparser1.add_parser(
        "generate",
        help="Generate a configuration file to be used with tool"
    )

    # Assign settings for 'execute' command
    subp1_exec_group = subp1_exec.add_mutually_exclusive_group(
        required=True
    )
    subp1_exec_group.add_argument(
        "-f", "--with-file",
        dest="file",
        help="Execute the tool with a config file",
    )
    subp1_exec_group.add_argument(  # :TODO:
        "-s", "--single",
        help="Execute the tool with singular arguments",
        default=None,
    )
    subp1_exec.add_argument(
        "--headless",
        help="Run WebDriver in headless mode",
        action="store_true",
        default=False,
    )
    subp1_exec.add_argument(
        "--incognito",
        help="Run WebDriver in incognito mode",
        action="store_true",
        default=False,
    )
    subp1_exec.add_argument(  # :TODO:
        "--log",
        help="Log the execution history in current working directory",
        action="store_true",
        default=None,
    )
    subp1_exec.set_defaults(func=execute_tool)

    # Assign settings for 'generate' command
    subp1_gen_group = subp1_gen.add_mutually_exclusive_group(
        required=True
    )
    subp1_gen_group.add_argument(
        "-t", "--template",
        dest="template",
        help="Generate a template config file"
    )
    subp1_gen_group.add_argument(
        "-e", "--example",
        dest="example",
        help="Generate an example config file"
    )
    subp1_gen.set_defaults(func=generate_config)

    cli_args = argparser.parse_args()

    return cli_args


def execute_tool(cli_args):

    # Use configparser to obtain information from given config file.
    config = configparser.ConfigParser()
    config.read(cli_args.file)

    job_searcher = JobSearcher(config)
    job_data_scraper = JobDataScraper(job_searcher, cli_args)

def generate_config(cli_args):
    # :FIXME:
    pass


def main():

    CLI_ARGS = parse_cli_inputs()

    print(CLI_ARGS.mode)
    # input("Wait for <Enter> keypress")

    mode_switcher = {
        "execute": execute_tool,
        "generate": generate_config,
        "help": ...  # :REVIEW:  is Ellipsis correct in this case?
    }

    mode_switcher[CLI_ARGS.mode](CLI_ARGS)
    # or CLI_ARGS.func(CLI_ARGS) thanks to .set_default(func=...)
    

if __name__ == "__main__":
    main()




# :XXX: DEPRECATED
def parse_cli_inputs_V1():

    argparser = argparse.ArgumentParser()
    ################
    # subparser_exec = argparser.add_subparsers()
    # subparser_exec_file = subparser_exec.add_parser(
    #     "config",
    #     # help="Execute the tool with a configuration file",
    # )
    # subparser_exec_file.add_argument(
    #     "-r", "--resolve",
    #     dest="file",
    #     help="Resolve an input config file and continue"
    # )
    # # subparser_exec_file_gen = \
    # #     subparser_exec_file.add_mutually_exclusive_group()
    # # subparser_exec_file_gen.add_argument(
    # #     "-gt", "--generate-template",
    # #     dest="template",
    # #     help="Generate a template config file"
    # # )
    # # subparser_exec_file_gen.add_argument(
    # #     "-ge", "--generate-example",
    # #     dest="example",
    # #     help="Generate an example config file"
    # # )
    # subparser_exec_fromsingle = subparser_exec.add_parser(  # :TODO:
    #     "--single", #"-s",
    #     help="Execute the tool with singular arguments",
    #     # default=None,
    # )
    #########

    parser_exec = argparser.add_mutually_exclusive_group(required=True)
    parser_exec.add_argument(
        "-f", "--file",
        dest="file",
        help="Execute the tool with a config file",
    )
    parser_exec.add_argument(  # :TODO:
        "-s", "--single",
        help="Execute the tool with singular arguments",
        default=None,
    )

    #######
    argparser.add_argument(
        "--headless",
        help="Run WebDriver in headless mode",
        action="store_true",
        default=False,
    )
    argparser.add_argument(
        "--incognito",
        help="Run WebDriver in incognito mode",
        action="store_true",
        default=False,
    )
    argparser.add_argument(  # :TODO:
        "--log",
        help="Log the execution history in current working directory",
        action="store_true",
        default=None,
    )

    CLI_ARGS = argparser.parse_args()

    return CLI_ARGS


# :XXX: DEPRECATED
def parse_cli_inputs_v2():

    argparser = argparse.ArgumentParser()
    subparser1 = argparser.add_subparsers()
    subp1_exec = subparser1.add_parser(
        "execute",
        help="Execute the tool",
    )
    subp1_gen = subparser1.add_parser(
        "generate",
        help="Generate a configuration file to be used with tool"
    )
    argparser.add_argument(  # :TODO:
        "--log",
        help="Log the execution history in current working directory",
        action="store_true",
        default=None,
    )

    # Assign settings for 'execute' command
    subp1_exec.add_argument(
        "-f", "--file",
        dest="file",
        help="Execute the tool with a config file",
    )
    subp1_exec.add_argument(  # :TODO:
        "-s", "--single",
        help="Execute the tool with singular arguments",
        default=None,
    )
    subp1_exec.add_argument(
        "--headless",
        help="Run WebDriver in headless mode",
        action="store_true",
        default=False,
    )
    subp1_exec.add_argument(
        "--incognito",
        help="Run WebDriver in incognito mode",
        action="store_true",
        default=False,
    )

    # Assign settings for 'generate' command
    subp1_gen.add_argument(
        "-gt", "--generate-template",
        dest="template",
        help="Generate a template config file"
    )
    subp1_gen.add_argument(
        "-ge", "--generate-example",
        dest="example",
        help="Generate an example config file"
    )

    CLI_ARGS = argparser.parse_args()

    return CLI_ARGS


# :XXX:

def interpret_configuration_file(filepath):

    # Use configparser to obtain information from given config file.
    config = configparser.ConfigParser()
    config.read(filepath)

    return config


def generate_bare_bones_config(filepath):
    #:FIXME:
    pass


def generate_example_config(filepath):
    # :FIXME:
    pass


class ConfigHandler:

    def __init__(self, filename: str, mode: str = "resolve") -> None:

        allowed_modes = {"generate", "resolve", "help"}
        mode_switcher = {
            "generate": generate_bare_bones_config,
            "resolve": interpret_configuration_file,
            "help": ...  # :REVIEW:  is Ellipsis correct in this case?
        }

        self.filename = filename

        if mode.casefold() not in allowed_modes:
            raise ValueError("mode='{}': It is not a permitted mode for {}"
                             .format(mode, self.__class__.__name__))
        else:
            self.mode = mode

        mode_switcher[self.mode](self.filename)
