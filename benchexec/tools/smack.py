"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import benchexec.result as result
import benchexec.util as util
import benchexec.tools.template

import subprocess
import sys
import string
import os
import re

class Tool(benchexec.tools.template.BaseTool):

    def executable(self):
        """
        Tells BenchExec to search for 'smack.sh' as the main executable to be
        called when running SMACK.
        """
        return util.find_executable('smack.sh')

    def version(self, executable):
        """
        Sets the version number for SMACK, which gets displayed in the "Tool" row
        in BenchExec table headers.
        """
        process = subprocess.Popen([executable, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        version = util.decode_to_string(stderr).split(' ')[2]
        return version

    def name(self):
        """
        Sets the name for SMACK, which gets displayed in the "Tool" row in
        BenchExec table headers.
        """
        return 'SMACK'

    def cmdline(self, executable, options, tasks, propertyfile=None, rlimits={}):
        """
        Allows us to define special actions to be taken or command line argument
        modifications to make just before calling SMACK.
        """
        assert len(tasks) == 1
        assert propertyfile is not None
        prop = ['--svcomp-property', propertyfile]
        return [executable] + options + prop + tasks

    def determine_result(self, returncode, returnsignal, output, isTimeout):
        """
        Returns a BenchExec result status based on the output of SMACK
        """
        splitout = "\n".join(output)
        if re.search(r'SMACK found no errors.', splitout):
            return result.RESULT_TRUE_PROP
        elif re.search(r'SMACK found an error.*', splitout):
            return result.RESULT_FALSE_REACH
        else:
            return result.RESULT_UNKNOWN
