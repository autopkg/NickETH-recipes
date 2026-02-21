#!/usr/bin/python
#
# Copyright 2025 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2026-02-21.
#
# Download App with dependencies from MS store to install offline.
# Based on: https://github.com/mjishnu/alt-app-installer-cli
# Output needs work. Goal would be to return the exitcode/errorlevel.

import os
import sys
import subprocess
import asyncio
import logging
import shutil
import re
from time import sleep

from tqdm import tqdm
from pypdl import Pypdl

from autopkglib import Processor, ProcessorError

sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(sharedproc_dir)
from MS_store_urlgen import url_generator

MATCH_MESSAGE = "Found matching text"
NO_MATCH_MESSAGE = "No match found in passed text"
   
__all__ = ["MSStoreAppGet"]


class MSStoreAppGet(Processor):
    description = "Download App and dependencies from MS store."
    input_variables = {
        "app_url": {
            "required": True,
            "description": "Url to the store app, required",
        },
        "dl_dir": {
            "required": True,
            "description": (
                "The directory where the packages will be downloaded to. Defaults "
                "to RECIPE_CACHE_DIR/downloads. If 'none' is set, only the path is returned."
            ),
        },
        "dl_file": {
            "required": False,
            "description": (
                "The file name for the downloaded main file. Defaults "
                "to its original name."
            ),
        },
        "dl_deps": {
            "required": False,
            "description": (
                "Dependency handling mode ('all', 'required', 'ignore_ver', 'none')"
                "Defaults to 'none'."
            ),
        },
        "dl_arch": {
            "default": False,
            "required": False,
            "description": (
                "Architecture to use for downloading (x64, arm, arm64, x86, auto). "
                "Defaults to 'auto'."
            ),
        },
        "re_pattern": {
            "description": "Regular expression (Python) to match against the main file to extract the version.",
            "required": False,
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {
        "file_list": {
            "description": "List of downloaded apps."
        }
    }
    __doc__ = description


    def default_logger(self, name: str) -> logging.Logger:
        """Creates a default debugging logger."""
        logger = logging.getLogger(name)
        handler = logging.FileHandler("log.txt", mode="a", delay=True)
        custom_format = (
            f"[{name} logs] \n[%(asctime)s]\n\n %(levelname)s: %(message)s\n{82 * '-'}\n"
        )
        handler.setFormatter(logging.Formatter(custom_format, datefmt="%d-%m-%Y %H:%M:%S"))
        logger.addHandler(handler)
        return logger


    def download(self, url, progress, dwnpath, dwnfile, arch, ignore_ver, all_dependencies, no_dependencies):

        if dwnfile != "none":
            dwnpath = os.path.join(dwnpath, dwnfile)

        if dwnfile == "none":
            dwnfile = None

        arch = arch if arch != "auto" else None
        main_dict, final_data, main_file, uwp = asyncio.run(
            url_generator(url, ignore_ver, all_dependencies, arch)
        )
        
        if dwnpath is not None:
            path_lst = []
            tasks = []

            def create_task(f_name):
                remote_url = main_dict[f_name]
                path = os.path.join(dwnpath, f_name)
                
                async def new_url_gen():
                    urls = await url_generator(url, ignore_ver, all_dependencies)
                    return urls[0][f_name]

                path_lst.append(dwnpath)
                tasks.append(
                    {
                        "url": remote_url,
                        "file_path": dwnpath,
                        "mirrors": new_url_gen,
                    }
                )

            d = None
            d = Pypdl(logger=self.default_logger("downloader"), max_concurrent=2)

            if no_dependencies:
                create_task(main_file)
                final_data = [main_file]
            else:
                for f_name in final_data:
                    create_task(f_name)
            
            display = True if progress == "full" else False
            block = False if progress == "simple" else True

            d.start(tasks=tasks, retries=3, overwrite=False, display=display, block=block)
            if progress == "simple":
                terminal_width = shutil.get_terminal_size().columns
                ncols = 105 if terminal_width >= 105 else None

                with tqdm(
                    total=100, ascii=True, bar_format="[{bar}] {percentage:3.0f}%", ncols=ncols
                ) as pbar:
                    while not d.completed:
                        sleep(0.5)
                        progress = d.progress if d.size else d.task_progress
                        pbar.n = progress or 0
                        pbar.refresh()
                    pbar.n = 100
                    pbar.refresh()

            self.output("Downloaded Package: %s" % final_data)
        mainoutfile = [main_dict[main_file], main_file]
        return mainoutfile

    def get_download_dir(self):
        """Create download dir and return its path."""
        download_dir = self.env.get("dl_dir") or os.path.join(
            self.env["RECIPE_CACHE_DIR"], "downloads"
        )
        if "download_dir" == "none":
            download_dir = ""
        else:
            if not os.path.exists(download_dir):
                try:
                    os.makedirs(download_dir)
                except OSError as err:
                    raise ProcessorError(f"Can't create {download_dir}: {err.strerror}")
        return download_dir

    def prepare_re_flags(self):
        """Create flag varible for re.compile"""
        flag_accumulator = 0
        for flag in self.env.get("re_flags", {}):
            if flag in re.__dict__:
                flag_accumulator += re.__dict__[flag]
        return flag_accumulator

    def re_search(self, content):
        """Search for re_pattern in content"""

        re_pattern = re.compile(self.env["re_pattern"], flags=self.prepare_re_flags())
        match = re_pattern.search(content)

        if not match:
            raise ProcessorError(f"{NO_MATCH_MESSAGE}: {content}")

        # return the last matched group with the dict of named groups
        return (match.group(match.lastindex or 0), match.groupdict())

    def main(self):

        app_url = self.env.get('app_url')
        download_dir = self.get_download_dir()

        if "dl_file" in self.env:
            dl_file = self.env.get('dl_file')
            if "dl_file" == "none":
                dl_file = None
        else:
            dl_file = None

        if "dl_arch" in self.env:
            dl_arch = self.env.get('dl_arch')
        else:
            dl_arch = "auto"

        if "dl_deps" in self.env:
            dl_deps = self.env.get('dl_deps')
        else:
            dl_deps = "none"

        dep_mapping = {
            "all": {
                "all_dependencies": True,
                "ignore_ver": False,
                "no_dependencies": False,
            },
            "required": {
                "all_dependencies": False,
                "ignore_ver": False,
                "no_dependencies": False,
            },
            "ignore_ver": {
                "all_dependencies": False,
                "ignore_ver": True,
                "no_dependencies": False,
            },
            "none": {
                "all_dependencies": False,
                "ignore_ver": False,
                "no_dependencies": True,
            },
        }
        dep_config = dep_mapping[dl_deps]

        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose')
        if verbosity > 1:
            dl_progress = "simple"
        elif verbosity > 3:
            dl_progress = "full"
        else:
            dl_progress = "none"

        data = self.download(app_url, dl_progress, download_dir, dl_file, dl_arch, **dep_config)

        if "re_pattern" in self.env:
            groupmatch, groupdict = self.re_search(data[1])
            if groupmatch:
                self.env['version'] = groupmatch
        
        self.env['file_list'] = data[0]
        self.env['main_file'] = data[1]

        self.output_variables = {}
        for key in groupdict.keys():
            self.env[key] = groupdict[key]
            self.output(f"{MATCH_MESSAGE} ({key}): {self.env[key]}")
            self.output_variables[key] = {
                "description": "Matched regular expression group"
            }
            
if __name__ == '__main__':
    processor = MSStoreAppGet()
    processor.execute_shell()
