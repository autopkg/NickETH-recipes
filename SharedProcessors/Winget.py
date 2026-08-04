#!/usr/bin/python
#
# Copyright 2026 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2026-08-01.
#
# 20260803 Nick Heim: Initial release.

# you need to install winget first!
# On Powershell, start:
# Install-Script -Name winget-install -Force
# winget-install -Force

import os
import sys
import subprocess
import json

from autopkglib import Processor, ProcessorError


__all__ = ["Winget"]


class Winget(Processor):
    description = "Dump or process 'winget' commands."
    input_variables = {
        "main_command": {
            "required": True,
            "description": "Winget main command, required",
        },
        "WG_id": {
            "required": True,
            "description": "Winget ID, required",
        },
        "sub_command": {
            "required": False,
            "description": "Winget main command.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
        "Winget_Dump": {
            "description": "Dump the actual values of Winget."
        },
        "url": {
            "description": "Dump the actual URL from the Winget show call."
        },
        "WG_JSON": {
            "description": "Dump the output as JSON from the Winget show call."
        }
    }

    __doc__ = description

    def main(self):

        # Determine the commands.
        # allow a subset of the commands supported by winget.
        valid_commands = [
            "show",
            "download",
        ]

        main_command = self.env.get("main_command", "show")
        if main_command not in valid_commands:
            raise ProcessorError(
                f"main_command '{main_command}' is invalid. Must be one of: "
                f"{', '.join(valid_commands)}."
            )

        main_command = self.env.get('main_command')
        cmd = ["winget", main_command]
        if "sub_command" in self.env:
            sub_command = self.env.get('sub_command')
            cmd.extend([sub_command])
        WG_id = self.env.get('WG_id')
        cmd.extend([WG_id])
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'

        Output = subprocess.check_output(cmd)
        self.output("cmd: %s" % cmd)
        #self.output("Output: %s" % Output)
        if main_command == "show":
            Output_decoded = Output.decode("utf-8", errors="ignore").replace("\r", "")
            if verbosity > 1:
                self.output( "Output: %s" % Output)
            Out_JSON = {
                k.strip(): v.strip()
                for k, v in (line.split(":", 1) for line in Output_decoded.split("\n") if ":" in line)
            }

        #self.output("JSON: %s" % Out_JSON.dumps(info, indent=4))
        #print(json.dumps(info, indent=4))
	
            self.env['Winget_Dump'] = json.dumps(Out_JSON, indent=4)
            self.env['url'] = Out_JSON["Installer-URL"]
            self.env['version'] = Out_JSON["Version"]
            self.env['WG_JSON'] = Out_JSON
            if verbosity > 1:
                self.output( "Winget_Dump: %s" % Out_JSON)

                            
if __name__ == '__main__':
    processor = Winget()
    processor.execute_shell()
