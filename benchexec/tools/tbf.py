"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2018  Dirk Beyer
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
import logging

from benchexec.model import SOFTTIMELIMIT


class Tool(benchexec.tools.template.BaseTool):
    """
    Tool info for tbf (https://github.com/sosy-lab/tbf).
    """

    REQUIRED_PATHS = ["tbf", "lib", "bin"]

    def program_files(self, executable):
        return self._program_files_from_executable(
            executable, self.REQUIRED_PATHS, parent_dir=True
        )

    def executable(self):
        return util.find_executable("tbf", "bin/tbf")

    def version(self, executable):
        return self._version_from_tool(executable)

    def name(self):
        return "tbf"

    def determine_result(self, returncode, returnsignal, output, isTimeout):
        """
        Parse the output of the tool and extract the verification result.
        This method always needs to be overridden.
        If the tool gave a result, this method needs to return one of the
        benchexec.result.RESULT_* strings.
        Otherwise an arbitrary string can be returned that will be shown to the user
        and should give some indication of the failure reason
        (e.g., "CRASH", "OUT_OF_MEMORY", etc.).
        """
        for line in reversed(output):
            if line.startswith("ERROR:"):
                if "timeout" in line.lower():
                    return "TIMEOUT"
                else:
                    return "ERROR ({0})".format(returncode)
            elif line.startswith("TBF") and "FALSE" in line:
                return result.RESULT_FALSE_REACH
            elif line.startswith("TBF") and "TRUE" in line:
                return result.RESULT_TRUE_PROP
            elif line.startswith("TBF") and "DONE" in line:
                return result.RESULT_DONE
        return result.RESULT_UNKNOWN

    def get_value_from_output(self, lines, identifier):
        for line in reversed(lines):
            if identifier in line:
                start = line.find(":") + 1
                end = line.find("(", start)
                return line[start:end].strip()
        return None

    def cmdline(self, executable, options, tasks, propertyfile=None, rlimits={}):
        if SOFTTIMELIMIT in rlimits:
            if "--timelimit" in options:
                logging.warning(
                    "Time limit already specified in command-line options,"
                    " not adding time limit from benchmark definition"
                    " to the command line."
                )
            else:
                options = options + ["--timelimit", str(rlimits[SOFTTIMELIMIT])]
        if propertyfile:
            if "testcomp" in self.version(executable):
                options = options + ["--spec", propertyfile]

            else:
                logging.warning(
                    "Propertyfile given, but tbf ignores property files"
                    " and always checks for calls to __VERIFIER_error()"
                )

        return super().cmdline(executable, options, tasks, propertyfile, rlimits)
