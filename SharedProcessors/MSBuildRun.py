#!/usr/local/autopkg/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-23.
#
# Run MSBuild to build project file.
# MSBuild.exe [Optionen] [Projektdatei]
# MSBuild MyApp.csproj -t:Clean -p:Configuration=Debug;TargetFrameworkVersion=v3.5
# 20210517 Nick Heim: Python v3 changes
# 20220504 Nick Heim: Insert MSBUILD_PATH variable

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["MSBuildRun"]

class MSBuildRun(Processor):
    description = "Run MSBuild to build a project."
    input_variables = {
        "build_file": {
            "required": True,
            "description": "Buildfile to run in MSBuild",
        },
        "build_folder": {
            "required": True,
            "description": "Path to the build dir, required",
        },
        "build_target": {
            "required": False,
            "description": "Target to call in Buildfile",
        },
        "build_property": {
            "required": False,
            "description": "Property to set in Buildfile",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):

        build_folder = self.env.get('build_folder')
        build_file = self.env.get('build_file')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)

        msbuild_cmd = self.env.get('MSBUILD_PATH', "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\MSBuild\\Current\\Bin\\amd64\\MSBuild.exe")
        #msbuild_cmd = 'msbuild.exe'
        # msbuild_cmd = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\MSBuild\\Current\\Bin\\amd64\\MSBuild.exe"

        self.output("Building in: %s" % build_folder)
        os.chdir(build_folder)
        #cmd = [msbuild_cmd, build_file.encode('utf-8')]
        cmd = [msbuild_cmd, build_file]

        if "build_target" in self.env:
            build_target = self.env.get('build_target')
            cmd.extend([('-t:%s' % build_target)])
        if "build_property" in self.env:
            build_property = self.env.get('build_property')
            # cmd.extend([('-p:%s' % build_property)])
            #cmd.extend([('-p:' + build_property.encode('utf-8'))])
            cmd.extend([('-p:' + build_property)])
        if verbosity > 1:
            cmd.extend(['-fl'])

        print("cmdline %s" % cmd, file=sys.stdout)
        # print >> sys.stdout, "run_folder %s" % os.getcwd()
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)

        except:
            if ignore_errors != 'True':
                raise
                print("MSBuild run %s" % Output, file=sys.stdout)

if __name__ == '__main__':
    processor = MSBuildRun()
    processor.execute_shell()
