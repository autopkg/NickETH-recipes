#!/usr/local/autopkg/python
#
# Copyright 2026 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2026-11-03.
#
# Direct download from any filesys to local filesys.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from __future__ import absolute_import

import json
import os
import shutil
import errno

from autopkglib import Processor, ProcessorError, xattr


__all__ = ["FileSysDownloader"]


class FileSysDownloader(Processor):
    """Downloads a file directly to the specified download_dir using OS' copy function."""

    description = __doc__

    input_variables = {
        "source_path": {
            "required": True,
            "description": "Local mounted SMB file path.",
        },
        "download_dir": {
            "required": False,
            "description": (
                "The directory where the file will be downloaded to. Defaults "
                "to RECIPE_CACHE_DIR/downloads."
            ),
        },
        "filename": {
            "required": False,
            "description": "Override destination filename.",
        },
    }

    output_variables = {
        "pathname": {
            "description": "Downloaded file path."
        },
        "download_changed": {
            "description": "True if file was updated."
        }
    }

    XATTR_ETAG = "com.github.autopkg.etag"
    XATTR_LAST_MODIFIED = "com.github.autopkg.last-modified"

    def read_xattr(self, path, name):
        if name in xattr.listxattr(path):
            return xattr.getxattr(path, name).decode()
        return None


    def write_xattr(self, path, name, value):
        xattr.setxattr(
            path,
            name,
            str(value).encode("utf-8"),
        )
 
    def get_download_dir(self):
        """Create download dir and return its path."""
        download_dir = self.env.get("download_dir") or os.path.join(
            self.env["RECIPE_CACHE_DIR"], "downloads"
        )
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except OSError as err:
                raise ProcessorError(f"Can't create {download_dir}: {err.strerror}")
        return download_dir
        
    def main(self):
        XATTR_ETAG = "com.github.autopkg.etag"
        XATTR_LAST_MODIFIED = "com.github.autopkg.last-modified"
        source = self.env["source_path"]

        download_dir = self.get_download_dir()
        if not os.path.exists(source):
            raise ProcessorError(
                f"Source does not exist: {source}"
            )

        filename = self.env.get(
            "filename",
            os.path.basename(source)
        )

        dest = os.path.join(download_dir, filename)

        remote_stat = os.stat(source)

        remote_etag = (
            f"{remote_stat.st_size}-"
            f"{int(remote_stat.st_mtime)}"
        )

        remote_last_modified = str(
            int(remote_stat.st_mtime)
        )

        changed = True

        if os.path.exists(dest):

            cached_etag = self.read_xattr(
                dest,
                XATTR_ETAG
            )

            cached_last_modified = self.read_xattr(
                dest,
                XATTR_LAST_MODIFIED
            )

            if (
                cached_etag == remote_etag and
                cached_last_modified == remote_last_modified
            ):
                changed = False

        if changed:

            self.output(
                f"Copying updated file: {filename}"
            )

            shutil.copy2(source, dest)

            self.write_xattr(
                dest,
                XATTR_ETAG,
                remote_etag
            )

            self.write_xattr(
                dest,
                XATTR_LAST_MODIFIED,
                remote_last_modified
            )

        else:
            self.output(
                f"No change detected for {filename}"
            )

        self.env["pathname"] = dest
        self.env["download_changed"] = changed


if __name__ == "__main__":
    PROCESSOR = FileSysDownloader()
    PROCESSOR.execute_shell()