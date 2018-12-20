
# Copyright 2018 Michael DeHaan LLC, <michael@michaeldehaan.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys

from colorama import init as colorama_init

from opsmop.callbacks.callbacks import Callbacks
from opsmop.callbacks.common import CommonCallbacks
from opsmop.callbacks.local import LocalCliCallbacks
from opsmop.core.api import Api
from opsmop.core.context import Context
from opsmop.core.errors import OpsMopError, OpsMopStop
from opsmop.core.common import load_data_file, shlex_kv


class Cli(object):

    def __init__(self, policy):
        """
        The CLI is constructed with the sys.argv command line, see bin/opsmop
        """
        self.policy = policy
        self.args = sys.argv
        self.go()

    def handle_extra_vars(self, extra_vars):
        data = None
        # TODO: make some functions in common that do this generically
        if extra_vars.startswith("@"):
            extra_vars = extra_vars.replace("@", "")
            data = load_data_file(extra_vars)
        else:
            data = shlex_kv(extra_vars)
        return data

    def go(self):

        colorama_init()

        common_args_parser = argparse.ArgumentParser(add_help=False)
        common_args_parser.add_argument('--extra-vars', help="add extra variables from the command line")
        common_args_parser.add_argument('--limit-groups', help="(with --push) limit groups executed to this comma-separated list of patterns")
        common_args_parser.add_argument('--limit-hosts', help="(with --push) limit hosts executed to this comma-separated list of patterns")
        common_args_parser.add_argument('--tags', help='optional comma seperated list of tags')
        common_args_parser.add_argument('--verbose', action='store_true', help='(with --push) increase verbosity')

        local_or_push_parser = common_args_parser.add_mutually_exclusive_group(required=True)
        local_or_push_parser.add_argument('--local', action='store_true', help='run in local mode')
        local_or_push_parser.add_argument('--push', action='store_true', help='run in push mode')

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='cmd', title='subcommands')
        subparsers.required = True
        subparsers.add_parser('apply', parents=[common_args_parser], help="apply policy")
        subparsers.add_parser('check', parents=[common_args_parser], help="check policy")
        subparsers.add_parser('validate', parents=[common_args_parser], help='validate policy')

        args = parser.parse_args(self.args[1:])

        extra_vars = dict()
        if args.extra_vars is not None:
            extra_vars = self.handle_extra_vars(args.extra_vars)

        Callbacks().set_callbacks([LocalCliCallbacks(), CommonCallbacks()])
        Context().set_verbose(args.verbose)

        abspath = os.path.abspath(sys.modules[self.policy.__module__].__file__)
        relative_root = os.path.dirname(abspath)
        os.chdir(os.path.dirname(abspath))

        tags = None
        if args.tags is not None:
            tags = args.tags.strip().split(",")

        api = Api(
            policies=[self.policy],
            tags=tags,
            push=args.push,
            extra_vars=extra_vars,
            limit_groups=args.limit_groups,
            limit_hosts=args.limit_hosts,
            relative_root=relative_root)

        try:
            handler = getattr(api, args.cmd)
            handler()
        except OpsMopStop:
            sys.exit(1)
        except OpsMopError as ome:
            print("")
            print(str(ome))
            print("")
            sys.exit(1)

        print("")
        sys.exit(0)
