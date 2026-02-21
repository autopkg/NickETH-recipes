# Taken from: https://github.com/mjishnu/alt-app-installer-cli
# Thank you for this excellent work!
import asyncio
import datetime
import html
import json
import os
import platform
import re
import warnings
from xml.dom import minidom

import aiohttp
import base64

warnings.filterwarnings("ignore")
script_dir = os.path.dirname(os.path.abspath(__file__))

GetCookie_xml = 'PEVudmVsb3BlICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMy8wNS9zb2FwLWVudmVsb3Bl\nIiB4bWxuczphPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1LzA4L2FkZHJlc3NpbmciIHhtbG5zOnU9\nImh0dHA6Ly9kb2NzLm9hc2lzLW9wZW4ub3JnL3dzcy8yMDA0LzAxL29hc2lzLTIwMDQwMS13c3Mt\nd3NzZWN1cml0eS11dGlsaXR5LTEuMC54c2QiPgogICAgPEhlYWRlcj4KICAgICAgICA8YTpBY3Rp\nb24gbXVzdFVuZGVyc3RhbmQ9IjEiID5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vU29mdHdhcmVE\naXN0cmlidXRpb24vU2VydmVyL0NsaWVudFdlYlNlcnZpY2UvR2V0Q29va2llPC9hOkFjdGlvbj4K\nICAgICAgICA8YTpUbyBtdXN0VW5kZXJzdGFuZD0iMSI+aHR0cHM6Ly9mZTNjci5kZWxpdmVyeS5t\ncC5taWNyb3NvZnQuY29tL0NsaWVudFdlYlNlcnZpY2UvY2xpZW50LmFzbXg8L2E6VG8+CiAgICAg\nICAgPFNlY3VyaXR5IG11c3RVbmRlcnN0YW5kPSIxIiB4bWxucz0iaHR0cDovL2RvY3Mub2FzaXMt\nb3Blbi5vcmcvd3NzLzIwMDQvMDEvb2FzaXMtMjAwNDAxLXdzcy13c3NlY3VyaXR5LXNlY2V4dC0x\nLjAueHNkIj4KICAgICAgICAgICAgPFdpbmRvd3NVcGRhdGVUaWNrZXRzVG9rZW4geG1sbnM9Imh0\ndHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vbXN1cy8yMDE0LzEwL1dpbmRvd3NVcGRhdGVBdXRo\nb3JpemF0aW9uIiB1OmlkPSJDbGllbnRNU0EiPgogICAgICAgICAgICAgICAgPCEtLSA8VGlja2V0\nVHlwZSBOYW1lPSJNU0EiIFZlcnNpb249IjEuMCIgUG9saWN5PSJNQklfU1NMIj48VXNlci8+PC9U\naWNrZXRUeXBlPiAtLT4KICAgICAgICAgICAgPC9XaW5kb3dzVXBkYXRlVGlja2V0c1Rva2VuPgog\nICAgICAgIDwvU2VjdXJpdHk+CiAgICA8L0hlYWRlcj4KICAgIDxCb2R5PjwvQm9keT4KPC9FbnZl\nbG9wZT4=\n'
WUIDRequest_xml = 'PHM6RW52ZWxvcGUKCXhtbG5zOmE9Imh0dHA6Ly93d3cudzMub3JnLzIwMDUvMDgvYWRkcmVzc2lu\nZyIKCXhtbG5zOnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDMvMDUvc29hcC1lbnZlbG9wZSI+Cgk8\nczpIZWFkZXI+CgkJPGE6QWN0aW9uIHM6bXVzdFVuZGVyc3RhbmQ9IjEiPgoJCQlodHRwOi8vd3d3\nLm1pY3Jvc29mdC5jb20vU29mdHdhcmVEaXN0cmlidXRpb24vU2VydmVyL0NsaWVudFdlYlNlcnZp\nY2UvU3luY1VwZGF0ZXM8L2E6QWN0aW9uPgoJCTxhOk1lc3NhZ2VJRD51cm46dXVpZDoxNzVkZjY4\nYy00YjkxLTQxZWUtYjcwYi1mMjIwOGM2NTQzOGU8L2E6TWVzc2FnZUlEPgoJCTxhOlRvIHM6bXVz\ndFVuZGVyc3RhbmQ9IjEiPgoJCQlodHRwczovL2ZlMy5kZWxpdmVyeS5tcC5taWNyb3NvZnQuY29t\nL0NsaWVudFdlYlNlcnZpY2UvY2xpZW50LmFzbXg8L2E6VG8+CgkJPG86U2VjdXJpdHkgczptdXN0\nVW5kZXJzdGFuZD0iMSIKCQkJeG1sbnM6bz0iaHR0cDovL2RvY3Mub2FzaXMtb3Blbi5vcmcvd3Nz\nLzIwMDQvMDEvb2FzaXMtMjAwNDAxLXdzcy13c3NlY3VyaXR5LXNlY2V4dC0xLjAueHNkIj4KCQkJ\nPFRpbWVzdGFtcAoJCQkJeG1sbnM9Imh0dHA6Ly9kb2NzLm9hc2lzLW9wZW4ub3JnL3dzcy8yMDA0\nLzAxL29hc2lzLTIwMDQwMS13c3Mtd3NzZWN1cml0eS11dGlsaXR5LTEuMC54c2QiPgoJCQkJPENy\nZWF0ZWQ+MjAxNy0wOC0wNVQwMjowMzowNS4wMzhaPC9DcmVhdGVkPgoJCQkJPEV4cGlyZXM+MjAx\nNy0wOC0wNVQwMjowODowNS4wMzhaPC9FeHBpcmVzPgoJCQk8L1RpbWVzdGFtcD4KCQkJPHd1d3M6\nV2luZG93c1VwZGF0ZVRpY2tldHNUb2tlbiB3c3U6aWQ9IkNsaWVudE1TQSIKCQkJCXhtbG5zOndz\ndT0iaHR0cDovL2RvY3Mub2FzaXMtb3Blbi5vcmcvd3NzLzIwMDQvMDEvb2FzaXMtMjAwNDAxLXdz\ncy13c3NlY3VyaXR5LXV0aWxpdHktMS4wLnhzZCIKCQkJCXhtbG5zOnd1d3M9Imh0dHA6Ly9zY2hl\nbWFzLm1pY3Jvc29mdC5jb20vbXN1cy8yMDE0LzEwL1dpbmRvd3NVcGRhdGVBdXRob3JpemF0aW9u\nIj4KCQkJCTxUaWNrZXRUeXBlIE5hbWU9Ik1TQSIgVmVyc2lvbj0iMS4wIiBQb2xpY3k9Ik1CSV9T\nU0wiPgoJCQkJCXsyfQoJCQkJPC9UaWNrZXRUeXBlPgoJCQk8L3d1d3M6V2luZG93c1VwZGF0ZVRp\nY2tldHNUb2tlbj4KCQk8L286U2VjdXJpdHk+Cgk8L3M6SGVhZGVyPgoJPHM6Qm9keT4KCQk8U3lu\nY1VwZGF0ZXMKCQkJeG1sbnM9Imh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9Tb2Z0d2FyZURpc3Ry\naWJ1dGlvbi9TZXJ2ZXIvQ2xpZW50V2ViU2VydmljZSI+CgkJCTxjb29raWU+CgkJCQk8RXhwaXJh\ndGlvbj4yMDQ1LTAzLTExVDAyOjAyOjQ4WjwvRXhwaXJhdGlvbj4KCQkJCTxFbmNyeXB0ZWREYXRh\nPnswfTwvRW5jcnlwdGVkRGF0YT4KCQkJPC9jb29raWU+CgkJCTxwYXJhbWV0ZXJzPgoJCQkJPEV4\ncHJlc3NRdWVyeT5mYWxzZTwvRXhwcmVzc1F1ZXJ5PgoJCQkJPEluc3RhbGxlZE5vbkxlYWZVcGRh\ndGVJRHM+CgkJCQkJPGludD4xPC9pbnQ+CgkJCQkJPGludD4yPC9pbnQ+CgkJCQkJPGludD4zPC9p\nbnQ+CgkJCQkJPGludD4xMTwvaW50PgoJCQkJCTxpbnQ+MTk8L2ludD4KCQkJCQk8aW50PjU0NDwv\naW50PgoJCQkJCTxpbnQ+NTQ5PC9pbnQ+CgkJCQkJPGludD4yMzU5OTc0PC9pbnQ+CgkJCQkJPGlu\ndD4yMzU5OTc3PC9pbnQ+CgkJCQkJPGludD41MTY5MDQ0PC9pbnQ+CgkJCQkJPGludD44Nzg4ODMw\nPC9pbnQ+CgkJCQkJPGludD4yMzExMDk5MzwvaW50PgoJCQkJCTxpbnQ+MjMxMTA5OTQ8L2ludD4K\nCQkJCQk8aW50PjU0MzQxOTAwPC9pbnQ+CgkJCQkJPGludD41NDM0MzY1NjwvaW50PgoJCQkJCTxp\nbnQ+NTk4MzAwMDY8L2ludD4KCQkJCQk8aW50PjU5ODMwMDA3PC9pbnQ+CgkJCQkJPGludD41OTgz\nMDAwODwvaW50PgoJCQkJCTxpbnQ+NjA0ODQwMTA8L2ludD4KCQkJCQk8aW50PjYyNDUwMDE4PC9p\nbnQ+CgkJCQkJPGludD42MjQ1MDAxOTwvaW50PgoJCQkJCTxpbnQ+NjI0NTAwMjA8L2ludD4KCQkJ\nCQk8aW50PjY2MDI3OTc5PC9pbnQ+CgkJCQkJPGludD42NjA1MzE1MDwvaW50PgoJCQkJCTxpbnQ+\nOTc2NTc4OTg8L2ludD4KCQkJCQk8aW50Pjk4ODIyODk2PC9pbnQ+CgkJCQkJPGludD45ODk1OTAy\nMjwvaW50PgoJCQkJCTxpbnQ+OTg5NTkwMjM8L2ludD4KCQkJCQk8aW50Pjk4OTU5MDI0PC9pbnQ+\nCgkJCQkJPGludD45ODk1OTAyNTwvaW50PgoJCQkJCTxpbnQ+OTg5NTkwMjY8L2ludD4KCQkJCQk8\naW50PjEwNDQzMzUzODwvaW50PgoJCQkJCTxpbnQ+MTA0OTAwMzY0PC9pbnQ+CgkJCQkJPGludD4x\nMDU0ODkwMTk8L2ludD4KCQkJCQk8aW50PjExNzc2NTMyMjwvaW50PgoJCQkJCTxpbnQ+MTI5OTA1\nMDI5PC9pbnQ+CgkJCQkJPGludD4xMzAwNDAwMzE8L2ludD4KCQkJCQk8aW50PjEzMjM4NzA5MDwv\naW50PgoJCQkJCTxpbnQ+MTMyMzkzMDQ5PC9pbnQ+CgkJCQkJPGludD4xMzMzOTkwMzQ8L2ludD4K\nCQkJCQk8aW50PjEzODUzNzA0ODwvaW50PgoJCQkJCTxpbnQ+MTQwMzc3MzEyPC9pbnQ+CgkJCQkJ\nPGludD4xNDM3NDc2NzE8L2ludD4KCQkJCQk8aW50PjE1ODk0MTA0MTwvaW50PgoJCQkJCTxpbnQ+\nMTU4OTQxMDQyPC9pbnQ+CgkJCQkJPGludD4xNTg5NDEwNDM8L2ludD4KCQkJCQk8aW50PjE1ODk0\nMTA0NDwvaW50PgoJCQkJCTxpbnQ+MTU5MTIzODU4PC9pbnQ+CgkJCQkJPGludD4xNTkxMzA5Mjg8\nL2ludD4KCQkJCQk8aW50PjE2NDgzNjg5NzwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ3Mzg2PC9pbnQ+\nCgkJCQkJPGludD4xNjQ4NDgzMjc8L2ludD4KCQkJCQk8aW50PjE2NDg1MjI0MTwvaW50PgoJCQkJ\nCTxpbnQ+MTY0ODUyMjQ2PC9pbnQ+CgkJCQkJPGludD4xNjQ4NTIyNTI8L2ludD4KCQkJCQk8aW50\nPjE2NDg1MjI1MzwvaW50PgoJCQkJPC9JbnN0YWxsZWROb25MZWFmVXBkYXRlSURzPgoJCQkJPE90\naGVyQ2FjaGVkVXBkYXRlSURzPgoJCQkJCTxpbnQ+MTA8L2ludD4KCQkJCQk8aW50PjE3PC9pbnQ+\nCgkJCQkJPGludD4yMzU5OTc3PC9pbnQ+CgkJCQkJPGludD41MTQzOTkwPC9pbnQ+CgkJCQkJPGlu\ndD41MTY5MDQzPC9pbnQ+CgkJCQkJPGludD41MTY5MDQ3PC9pbnQ+CgkJCQkJPGludD44ODA2NTI2\nPC9pbnQ+CgkJCQkJPGludD45MTI1MzUwPC9pbnQ+CgkJCQkJPGludD45MTU0NzY5PC9pbnQ+CgkJ\nCQkJPGludD4xMDgwOTg1NjwvaW50PgoJCQkJCTxpbnQ+MjMxMTA5OTU8L2ludD4KCQkJCQk8aW50\nPjIzMTEwOTk2PC9pbnQ+CgkJCQkJPGludD4yMzExMDk5OTwvaW50PgoJCQkJCTxpbnQ+MjMxMTEw\nMDA8L2ludD4KCQkJCQk8aW50PjIzMTExMDAxPC9pbnQ+CgkJCQkJPGludD4yMzExMTAwMjwvaW50\nPgoJCQkJCTxpbnQ+MjMxMTEwMDM8L2ludD4KCQkJCQk8aW50PjIzMTExMDA0PC9pbnQ+CgkJCQkJ\nPGludD4yNDUxMzg3MDwvaW50PgoJCQkJCTxpbnQ+Mjg4ODAyNjM8L2ludD4KCQkJCQk8aW50PjMw\nMDc3Njg4PC9pbnQ+CgkJCQkJPGludD4zMDQ4Njk0NDwvaW50PgoJCQkJCTxpbnQ+MzA1MjY5OTE8\nL2ludD4KCQkJCQk8aW50PjMwNTI4NDQyPC9pbnQ+CgkJCQkJPGludD4zMDUzMDQ5NjwvaW50PgoJ\nCQkJCTxpbnQ+MzA1MzA1MDE8L2ludD4KCQkJCQk8aW50PjMwNTMwNTA0PC9pbnQ+CgkJCQkJPGlu\ndD4zMDUzMDk2MjwvaW50PgoJCQkJCTxpbnQ+MzA1MzUzMjY8L2ludD4KCQkJCQk8aW50PjMwNTM2\nMjQyPC9pbnQ+CgkJCQkJPGludD4zMDUzOTkxMzwvaW50PgoJCQkJCTxpbnQ+MzA1NDUxNDI8L2lu\ndD4KCQkJCQk8aW50PjMwNTQ1MTQ1PC9pbnQ+CgkJCQkJPGludD4zMDU0NTQ4ODwvaW50PgoJCQkJ\nCTxpbnQ+MzA1NDYyMTI8L2ludD4KCQkJCQk8aW50PjMwNTQ3Nzc5PC9pbnQ+CgkJCQkJPGludD4z\nMDU0ODc5NzwvaW50PgoJCQkJCTxpbnQ+MzA1NDg4NjA8L2ludD4KCQkJCQk8aW50PjMwNTQ5MjYy\nPC9pbnQ+CgkJCQkJPGludD4zMDU1MTE2MDwvaW50PgoJCQkJCTxpbnQ+MzA1NTExNjE8L2ludD4K\nCQkJCQk8aW50PjMwNTUxMTY0PC9pbnQ+CgkJCQkJPGludD4zMDU1MzAxNjwvaW50PgoJCQkJCTxp\nbnQ+MzA1NTM3NDQ8L2ludD4KCQkJCQk8aW50PjMwNTU0MDE0PC9pbnQ+CgkJCQkJPGludD4zMDU1\nOTAwODwvaW50PgoJCQkJCTxpbnQ+MzA1NTkwMTE8L2ludD4KCQkJCQk8aW50PjMwNTYwMDA2PC9p\nbnQ+CgkJCQkJPGludD4zMDU2MDAxMTwvaW50PgoJCQkJCTxpbnQ+MzA1NjEwMDY8L2ludD4KCQkJ\nCQk8aW50PjMwNTYzMjYxPC9pbnQ+CgkJCQkJPGludD4zMDU2NTIxNTwvaW50PgoJCQkJCTxpbnQ+\nMzA1NzgwNTk8L2ludD4KCQkJCQk8aW50PjMwNjY0OTk4PC9pbnQ+CgkJCQkJPGludD4zMDY3Nzkw\nNDwvaW50PgoJCQkJCTxpbnQ+MzA2ODE2MTg8L2ludD4KCQkJCQk8aW50PjMwNjgyMTk1PC9pbnQ+\nCgkJCQkJPGludD4zMDY4NTA1NTwvaW50PgoJCQkJCTxpbnQ+MzA3MDI1Nzk8L2ludD4KCQkJCQk8\naW50PjMwNzA4NzcyPC9pbnQ+CgkJCQkJPGludD4zMDcwOTU5MTwvaW50PgoJCQkJCTxpbnQ+MzA3\nMTEzMDQ8L2ludD4KCQkJCQk8aW50PjMwNzE1NDE4PC9pbnQ+CgkJCQkJPGludD4zMDcyMDEwNjwv\naW50PgoJCQkJCTxpbnQ+MzA3MjAyNzM8L2ludD4KCQkJCQk8aW50PjMwNzMyMDc1PC9pbnQ+CgkJ\nCQkJPGludD4zMDg2Njk1MjwvaW50PgoJCQkJCTxpbnQ+MzA4NjY5NjQ8L2ludD4KCQkJCQk8aW50\nPjMwODcwNzQ5PC9pbnQ+CgkJCQkJPGludD4zMDg3Nzg1MjwvaW50PgoJCQkJCTxpbnQ+MzA4Nzg0\nMzc8L2ludD4KCQkJCQk8aW50PjMwODkwMTUxPC9pbnQ+CgkJCQkJPGludD4zMDg5MjE0OTwvaW50\nPgoJCQkJCTxpbnQ+MzA5OTA5MTc8L2ludD4KCQkJCQk8aW50PjMxMDQ5NDQ0PC9pbnQ+CgkJCQkJ\nPGludD4zMTE5MDkzNjwvaW50PgoJCQkJCTxpbnQ+MzExOTY5NjE8L2ludD4KCQkJCQk8aW50PjMx\nMTk3ODExPC9pbnQ+CgkJCQkJPGludD4zMTE5ODgzNjwvaW50PgoJCQkJCTxpbnQ+MzEyMDI3MTM8\nL2ludD4KCQkJCQk8aW50PjMxMjAzNTIyPC9pbnQ+CgkJCQkJPGludD4zMTIwNTQ0MjwvaW50PgoJ\nCQkJCTxpbnQ+MzEyMDU1NTc8L2ludD4KCQkJCQk8aW50PjMxMjA3NTg1PC9pbnQ+CgkJCQkJPGlu\ndD4zMTIwODQ0MDwvaW50PgoJCQkJCTxpbnQ+MzEyMDg0NTE8L2ludD4KCQkJCQk8aW50PjMxMjA5\nNTkxPC9pbnQ+CgkJCQkJPGludD4zMTIxMDUzNjwvaW50PgoJCQkJCTxpbnQ+MzEyMTE2MjU8L2lu\ndD4KCQkJCQk8aW50PjMxMjEyNzEzPC9pbnQ+CgkJCQkJPGludD4zMTIxMzU4ODwvaW50PgoJCQkJ\nCTxpbnQ+MzEyMTg1MTg8L2ludD4KCQkJCQk8aW50PjMxMjE5NDIwPC9pbnQ+CgkJCQkJPGludD4z\nMTIyMDI3OTwvaW50PgoJCQkJCTxpbnQ+MzEyMjAzMDI8L2ludD4KCQkJCQk8aW50PjMxMjIyMDg2\nPC9pbnQ+CgkJCQkJPGludD4zMTIyNzA4MDwvaW50PgoJCQkJCTxpbnQ+MzEyMjkwMzA8L2ludD4K\nCQkJCQk8aW50PjMxMjM4MjM2PC9pbnQ+CgkJCQkJPGludD4zMTI1NDE5ODwvaW50PgoJCQkJCTxp\nbnQ+MzEyNTgwMDg8L2ludD4KCQkJCQk8aW50PjM2NDM2Nzc5PC9pbnQ+CgkJCQkJPGludD4zNjQz\nNzg1MDwvaW50PgoJCQkJCTxpbnQ+MzY0NjQwMTI8L2ludD4KCQkJCQk8aW50PjQxOTE2NTY5PC9p\nbnQ+CgkJCQkJPGludD40NzI0OTk4MjwvaW50PgoJCQkJCTxpbnQ+NDcyODMxMzQ8L2ludD4KCQkJ\nCQk8aW50PjU4NTc3MDI3PC9pbnQ+CgkJCQkJPGludD41ODU3ODA0MDwvaW50PgoJCQkJCTxpbnQ+\nNTg1NzgwNDE8L2ludD4KCQkJCQk8aW50PjU4NjI4OTIwPC9pbnQ+CgkJCQkJPGludD41OTEwNzA0\nNTwvaW50PgoJCQkJCTxpbnQ+NTkxMjU2OTc8L2ludD4KCQkJCQk8aW50PjU5MTQyMjQ5PC9pbnQ+\nCgkJCQkJPGludD42MDQ2NjU4NjwvaW50PgoJCQkJCTxpbnQ+NjA0Nzg5MzY8L2ludD4KCQkJCQk8\naW50PjY2NDUwNDQxPC9pbnQ+CgkJCQkJPGludD42NjQ2NzAyMTwvaW50PgoJCQkJCTxpbnQ+NjY0\nNzkwNTE8L2ludD4KCQkJCQk8aW50Pjc1MjAyOTc4PC9pbnQ+CgkJCQkJPGludD43NzQzNjAyMTwv\naW50PgoJCQkJCTxpbnQ+Nzc0NDkxMjk8L2ludD4KCQkJCQk8aW50Pjg1MTU5NTY5PC9pbnQ+CgkJ\nCQkJPGludD45MDE5OTcwMjwvaW50PgoJCQkJCTxpbnQ+OTAyMTIwOTA8L2ludD4KCQkJCQk8aW50\nPjk2OTExMTQ3PC9pbnQ+CgkJCQkJPGludD45NzExMDMwODwvaW50PgoJCQkJCTxpbnQ+OTg1Mjg0\nMjg8L2ludD4KCQkJCQk8aW50Pjk4NjY1MjA2PC9pbnQ+CgkJCQkJPGludD45ODgzNzk5NTwvaW50\nPgoJCQkJCTxpbnQ+OTg4NDI5MjI8L2ludD4KCQkJCQk8aW50Pjk4ODQyOTc3PC9pbnQ+CgkJCQkJ\nPGludD45ODg0NjYzMjwvaW50PgoJCQkJCTxpbnQ+OTg4NjY0ODU8L2ludD4KCQkJCQk8aW50Pjk4\nODc0MjUwPC9pbnQ+CgkJCQkJPGludD45ODg3OTA3NTwvaW50PgoJCQkJCTxpbnQ+OTg5MDQ2NDk8\nL2ludD4KCQkJCQk8aW50Pjk4OTE4ODcyPC9pbnQ+CgkJCQkJPGludD45ODk0NTY5MTwvaW50PgoJ\nCQkJCTxpbnQ+OTg5NTk0NTg8L2ludD4KCQkJCQk8aW50Pjk4OTg0NzA3PC9pbnQ+CgkJCQkJPGlu\ndD4xMDAyMjAxMjU8L2ludD4KCQkJCQk8aW50PjEwMDIzODczMTwvaW50PgoJCQkJCTxpbnQ+MTAw\nNjYyMzI5PC9pbnQ+CgkJCQkJPGludD4xMDA3OTU4MzQ8L2ludD4KCQkJCQk8aW50PjEwMDg2MjQ1\nNzwvaW50PgoJCQkJCTxpbnQ+MTAzMTI0ODExPC9pbnQ+CgkJCQkJPGludD4xMDMzNDg2NzE8L2lu\ndD4KCQkJCQk8aW50PjEwNDM2OTk4MTwvaW50PgoJCQkJCTxpbnQ+MTA0MzcyNDcyPC9pbnQ+CgkJ\nCQkJPGludD4xMDQzODUzMjQ8L2ludD4KCQkJCQk8aW50PjEwNDQ2NTgzMTwvaW50PgoJCQkJCTxp\nbnQ+MTA0NDY1ODM0PC9pbnQ+CgkJCQkJPGludD4xMDQ0Njc2OTc8L2ludD4KCQkJCQk8aW50PjEw\nNDQ3MzM2ODwvaW50PgoJCQkJCTxpbnQ+MTA0NDgyMjY3PC9pbnQ+CgkJCQkJPGludD4xMDQ1MDUw\nMDU8L2ludD4KCQkJCQk8aW50PjEwNDUyMzg0MDwvaW50PgoJCQkJCTxpbnQ+MTA0NTUwMDg1PC9p\nbnQ+CgkJCQkJPGludD4xMDQ1NTgwODQ8L2ludD4KCQkJCQk8aW50PjEwNDY1OTQ0MTwvaW50PgoJ\nCQkJCTxpbnQ+MTA0NjU5Njc1PC9pbnQ+CgkJCQkJPGludD4xMDQ2NjQ2Nzg8L2ludD4KCQkJCQk8\naW50PjEwNDY2ODI3NDwvaW50PgoJCQkJCTxpbnQ+MTA0NjcxMDkyPC9pbnQ+CgkJCQkJPGludD4x\nMDQ2NzMyNDI8L2ludD4KCQkJCQk8aW50PjEwNDY3NDIzOTwvaW50PgoJCQkJCTxpbnQ+MTA0Njc5\nMjY4PC9pbnQ+CgkJCQkJPGludD4xMDQ2ODYwNDc8L2ludD4KCQkJCQk8aW50PjEwNDY5ODY0OTwv\naW50PgoJCQkJCTxpbnQ+MTA0NzUxNDY5PC9pbnQ+CgkJCQkJPGludD4xMDQ3NTI0Nzg8L2ludD4K\nCQkJCQk8aW50PjEwNDc1NTE0NTwvaW50PgoJCQkJCTxpbnQ+MTA0NzYxMTU4PC9pbnQ+CgkJCQkJ\nPGludD4xMDQ3NjIyNjY8L2ludD4KCQkJCQk8aW50PjEwNDc4NjQ4NDwvaW50PgoJCQkJCTxpbnQ+\nMTA0ODUzNzQ3PC9pbnQ+CgkJCQkJPGludD4xMDQ4NzMyNTg8L2ludD4KCQkJCQk8aW50PjEwNDk4\nMzA1MTwvaW50PgoJCQkJCTxpbnQ+MTA1MDYzMDU2PC9pbnQ+CgkJCQkJPGludD4xMDUxMTY1ODg8\nL2ludD4KCQkJCQk8aW50PjEwNTE3ODUyMzwvaW50PgoJCQkJCTxpbnQ+MTA1MzE4NjAyPC9pbnQ+\nCgkJCQkJPGludD4xMDUzNjI2MTM8L2ludD4KCQkJCQk8aW50PjEwNTM2NDU1MjwvaW50PgoJCQkJ\nCTxpbnQ+MTA1MzY4NTYzPC9pbnQ+CgkJCQkJPGludD4xMDUzNjk1OTE8L2ludD4KCQkJCQk8aW50\nPjEwNTM3MDc0NjwvaW50PgoJCQkJCTxpbnQ+MTA1MzczNTAzPC9pbnQ+CgkJCQkJPGludD4xMDUz\nNzM2MTU8L2ludD4KCQkJCQk8aW50PjEwNTM3NjYzNDwvaW50PgoJCQkJCTxpbnQ+MTA1Mzc3NTQ2\nPC9pbnQ+CgkJCQkJPGludD4xMDUzNzg3NTI8L2ludD4KCQkJCQk8aW50PjEwNTM3OTU3NDwvaW50\nPgoJCQkJCTxpbnQ+MTA1MzgxNjI2PC9pbnQ+CgkJCQkJPGludD4xMDUzODI1ODc8L2ludD4KCQkJ\nCQk8aW50PjEwNTQyNTMxMzwvaW50PgoJCQkJCTxpbnQ+MTA1NDk1MTQ2PC9pbnQ+CgkJCQkJPGlu\ndD4xMDU4NjI2MDc8L2ludD4KCQkJCQk8aW50PjEwNTkzOTAyOTwvaW50PgoJCQkJCTxpbnQ+MTA1\nOTk1NTg1PC9pbnQ+CgkJCQkJPGludD4xMDYwMTcxNzg8L2ludD4KCQkJCQk8aW50PjEwNjEyOTcy\nNjwvaW50PgoJCQkJCTxpbnQ+MTA2NzY4NDg1PC9pbnQ+CgkJCQkJPGludD4xMDc4MjUxOTQ8L2lu\ndD4KCQkJCQk8aW50PjExMTkwNjQyOTwvaW50PgoJCQkJCTxpbnQ+MTE1MTIxNDczPC9pbnQ+CgkJ\nCQkJPGludD4xMTU1Nzg2NTQ8L2ludD4KCQkJCQk8aW50PjExNjYzMDM2MzwvaW50PgoJCQkJCTxp\nbnQ+MTE3ODM1MTA1PC9pbnQ+CgkJCQkJPGludD4xMTc4NTA2NzE8L2ludD4KCQkJCQk8aW50PjEx\nODYzODUwMDwvaW50PgoJCQkJCTxpbnQ+MTE4NjYyMDI3PC9pbnQ+CgkJCQkJPGludD4xMTg4NzI2\nODE8L2ludD4KCQkJCQk8aW50PjExODg3MzgyOTwvaW50PgoJCQkJCTxpbnQ+MTE4ODc5Mjg5PC9p\nbnQ+CgkJCQkJPGludD4xMTg4ODkwOTI8L2ludD4KCQkJCQk8aW50PjExOTUwMTcyMDwvaW50PgoJ\nCQkJCTxpbnQ+MTE5NTUxNjQ4PC9pbnQ+CgkJCQkJPGludD4xMTk1Njk1Mzg8L2ludD4KCQkJCQk8\naW50PjExOTY0MDcwMjwvaW50PgoJCQkJCTxpbnQ+MTE5NjY3OTk4PC9pbnQ+CgkJCQkJPGludD4x\nMTk2NzQxMDM8L2ludD4KCQkJCQk8aW50PjExOTY5NzIwMTwvaW50PgoJCQkJCTxpbnQ+MTE5NzA2\nMjY2PC9pbnQ+CgkJCQkJPGludD4xMTk3NDQ2Mjc8L2ludD4KCQkJCQk8aW50PjExOTc3Mzc0Njwv\naW50PgoJCQkJCTxpbnQ+MTIwMDcyNjk3PC9pbnQ+CgkJCQkJPGludD4xMjAxNDQzMDk8L2ludD4K\nCQkJCQk8aW50PjEyMDIxNDE1NDwvaW50PgoJCQkJCTxpbnQ+MTIwMzU3MDI3PC9pbnQ+CgkJCQkJ\nPGludD4xMjAzOTI2MTI8L2ludD4KCQkJCQk8aW50PjEyMDM5OTEyMDwvaW50PgoJCQkJCTxpbnQ+\nMTIwNTUzOTQ1PC9pbnQ+CgkJCQkJPGludD4xMjA3ODM1NDU8L2ludD4KCQkJCQk8aW50PjEyMDc5\nNzA5MjwvaW50PgoJCQkJCTxpbnQ+MTIwODgxNjc2PC9pbnQ+CgkJCQkJPGludD4xMjA4ODk2ODk8\nL2ludD4KCQkJCQk8aW50PjEyMDk5OTU1NDwvaW50PgoJCQkJCTxpbnQ+MTIxMTY4NjA4PC9pbnQ+\nCgkJCQkJPGludD4xMjEyNjg4MzA8L2ludD4KCQkJCQk8aW50PjEyMTM0MTgzODwvaW50PgoJCQkJ\nCTxpbnQ+MTIxNzI5OTUxPC9pbnQ+CgkJCQkJPGludD4xMjE4MDM2Nzc8L2ludD4KCQkJCQk8aW50\nPjEyMjE2NTgxMDwvaW50PgoJCQkJCTxpbnQ+MTI1NDA4MDM0PC9pbnQ+CgkJCQkJPGludD4xMjcy\nOTMxMzA8L2ludD4KCQkJCQk8aW50PjEyNzU2NjY4MzwvaW50PgoJCQkJCTxpbnQ+MTI3NzYyMDY3\nPC9pbnQ+CgkJCQkJPGludD4xMjc4NjE4OTM8L2ludD4KCQkJCQk8aW50PjEyODU3MTcyMjwvaW50\nPgoJCQkJCTxpbnQ+MTI4NjQ3NTM1PC9pbnQ+CgkJCQkJPGludD4xMjg2OTg5MjI8L2ludD4KCQkJ\nCQk8aW50PjEyODcwMTc0ODwvaW50PgoJCQkJCTxpbnQ+MTI4NzcxNTA3PC9pbnQ+CgkJCQkJPGlu\ndD4xMjkwMzcyMTI8L2ludD4KCQkJCQk8aW50PjEyOTA3OTgwMDwvaW50PgoJCQkJCTxpbnQ+MTI5\nMTc1NDE1PC9pbnQ+CgkJCQkJPGludD4xMjkzMTcyNzI8L2ludD4KCQkJCQk8aW50PjEyOTMxOTY2\nNTwvaW50PgoJCQkJCTxpbnQ+MTI5MzY1NjY4PC9pbnQ+CgkJCQkJPGludD4xMjkzNzgwOTU8L2lu\ndD4KCQkJCQk8aW50PjEyOTQyNDgwMzwvaW50PgoJCQkJCTxpbnQ+MTI5NTkwNzMwPC9pbnQ+CgkJ\nCQkJPGludD4xMjk2MDM3MTQ8L2ludD4KCQkJCQk8aW50PjEyOTYyNTk1NDwvaW50PgoJCQkJCTxp\nbnQ+MTI5NjkyMzkxPC9pbnQ+CgkJCQkJPGludD4xMjk3MTQ5ODA8L2ludD4KCQkJCQk8aW50PjEy\nOTcyMTA5NzwvaW50PgoJCQkJCTxpbnQ+MTI5ODg2Mzk3PC9pbnQ+CgkJCQkJPGludD4xMjk5Njgz\nNzE8L2ludD4KCQkJCQk8aW50PjEyOTk3MjI0MzwvaW50PgoJCQkJCTxpbnQ+MTMwMDA5ODYyPC9p\nbnQ+CgkJCQkJPGludD4xMzAwMzM2NTE8L2ludD4KCQkJCQk8aW50PjEzMDA0MDAzMDwvaW50PgoJ\nCQkJCTxpbnQ+MTMwMDQwMDMyPC9pbnQ+CgkJCQkJPGludD4xMzAwNDAwMzM8L2ludD4KCQkJCQk8\naW50PjEzMDA5MTk1NDwvaW50PgoJCQkJCTxpbnQ+MTMwMTAwNjQwPC9pbnQ+CgkJCQkJPGludD4x\nMzAxMzEyNjc8L2ludD4KCQkJCQk8aW50PjEzMDEzMTkyMTwvaW50PgoJCQkJCTxpbnQ+MTMwMTQ0\nODM3PC9pbnQ+CgkJCQkJPGludD4xMzAxNzEwMzA8L2ludD4KCQkJCQk8aW50PjEzMDE3MjA3MTwv\naW50PgoJCQkJCTxpbnQ+MTMwMTk3MjE4PC9pbnQ+CgkJCQkJPGludD4xMzAyMTI0MzU8L2ludD4K\nCQkJCQk8aW50PjEzMDI5MTA3NjwvaW50PgoJCQkJCTxpbnQ+MTMwNDAyNDI3PC9pbnQ+CgkJCQkJ\nPGludD4xMzA0MDUxNjY8L2ludD4KCQkJCQk8aW50PjEzMDY3NjE2OTwvaW50PgoJCQkJCTxpbnQ+\nMTMwNjk4NDcxPC9pbnQ+CgkJCQkJPGludD4xMzA3MTMzOTA8L2ludD4KCQkJCQk8aW50PjEzMDc4\nNTIxNzwvaW50PgoJCQkJCTxpbnQ+MTMxMzk2OTA4PC9pbnQ+CgkJCQkJPGludD4xMzE0NTUxMTU8\nL2ludD4KCQkJCQk8aW50PjEzMTY4MjA5NTwvaW50PgoJCQkJCTxpbnQ+MTMxNjg5NDczPC9pbnQ+\nCgkJCQkJPGludD4xMzE3MDE5NTY8L2ludD4KCQkJCQk8aW50PjEzMjE0MjgwMDwvaW50PgoJCQkJ\nCTxpbnQ+MTMyNTI1NDQxPC9pbnQ+CgkJCQkJPGludD4xMzI3NjU0OTI8L2ludD4KCQkJCQk8aW50\nPjEzMjgwMTI3NTwvaW50PgoJCQkJCTxpbnQ+MTMzMzk5MDM0PC9pbnQ+CgkJCQkJPGludD4xMzQ1\nMjI5MjY8L2ludD4KCQkJCQk8aW50PjEzNDUyNDAyMjwvaW50PgoJCQkJCTxpbnQ+MTM0NTI4OTk0\nPC9pbnQ+CgkJCQkJPGludD4xMzQ1MzI5NDI8L2ludD4KCQkJCQk8aW50PjEzNDUzNjk5MzwvaW50\nPgoJCQkJCTxpbnQ+MTM0NTM4MDAxPC9pbnQ+CgkJCQkJPGludD4xMzQ1NDc1MzM8L2ludD4KCQkJ\nCQk8aW50PjEzNDU0OTIxNjwvaW50PgoJCQkJCTxpbnQ+MTM0NTQ5MzE3PC9pbnQ+CgkJCQkJPGlu\ndD4xMzQ1NTAxNTk8L2ludD4KCQkJCQk8aW50PjEzNDU1MDIxNDwvaW50PgoJCQkJCTxpbnQ+MTM0\nNTUwMjMyPC9pbnQ+CgkJCQkJPGludD4xMzQ1NTExNTQ8L2ludD4KCQkJCQk8aW50PjEzNDU1MTIw\nNzwvaW50PgoJCQkJCTxpbnQ+MTM0NTUxMzkwPC9pbnQ+CgkJCQkJPGludD4xMzQ1NTMxNzE8L2lu\ndD4KCQkJCQk8aW50PjEzNDU1MzIzNzwvaW50PgoJCQkJCTxpbnQ+MTM0NTU0MTk5PC9pbnQ+CgkJ\nCQkJPGludD4xMzQ1NTQyMjc8L2ludD4KCQkJCQk8aW50PjEzNDU1NTIyOTwvaW50PgoJCQkJCTxp\nbnQ+MTM0NTU1MjQwPC9pbnQ+CgkJCQkJPGludD4xMzQ1NTYxMTg8L2ludD4KCQkJCQk8aW50PjEz\nNDU1NzA3ODwvaW50PgoJCQkJCTxpbnQ+MTM0NTYwMDk5PC9pbnQ+CgkJCQkJPGludD4xMzQ1NjAy\nODc8L2ludD4KCQkJCQk8aW50PjEzNDU2MjA4NDwvaW50PgoJCQkJCTxpbnQ+MTM0NTYyMTgwPC9p\nbnQ+CgkJCQkJPGludD4xMzQ1NjMyODc8L2ludD4KCQkJCQk8aW50PjEzNDU2NTA4MzwvaW50PgoJ\nCQkJCTxpbnQ+MTM0NTY2MTMwPC9pbnQ+CgkJCQkJPGludD4xMzQ1NjgxMTE8L2ludD4KCQkJCQk8\naW50PjEzNDYyNDczNzwvaW50PgoJCQkJCTxpbnQ+MTM0NjY2NDYxPC9pbnQ+CgkJCQkJPGludD4x\nMzQ2NzI5OTg8L2ludD4KCQkJCQk8aW50PjEzNDY4NDAwODwvaW50PgoJCQkJCTxpbnQ+MTM0OTE2\nNTIzPC9pbnQ+CgkJCQkJPGludD4xMzUxMDA1Mjc8L2ludD4KCQkJCQk8aW50PjEzNTIxOTQxMDwv\naW50PgoJCQkJCTxpbnQ+MTM1MjIyMDgzPC9pbnQ+CgkJCQkJPGludD4xMzUzMDY5OTc8L2ludD4K\nCQkJCQk8aW50PjEzNTQ2MzA1NDwvaW50PgoJCQkJCTxpbnQ+MTM1Nzc5NDU2PC9pbnQ+CgkJCQkJ\nPGludD4xMzU4MTI5Njg8L2ludD4KCQkJCQk8aW50PjEzNjA5NzAzMDwvaW50PgoJCQkJCTxpbnQ+\nMTM2MTMxMzMzPC9pbnQ+CgkJCQkJPGludD4xMzYxNDY5MDc8L2ludD4KCQkJCQk8aW50PjEzNjE1\nNzU1NjwvaW50PgoJCQkJCTxpbnQ+MTM2MzIwOTYyPC9pbnQ+CgkJCQkJPGludD4xMzY0NTA2NDE8\nL2ludD4KCQkJCQk8aW50PjEzNjQ2NjAwMDwvaW50PgoJCQkJCTxpbnQ+MTM2NzQ1NzkyPC9pbnQ+\nCgkJCQkJPGludD4xMzY3NjE1NDY8L2ludD4KCQkJCQk8aW50PjEzNjg0MDI0NTwvaW50PgoJCQkJ\nCTxpbnQ+MTM4MTYwMDM0PC9pbnQ+CgkJCQkJPGludD4xMzgxODEyNDQ8L2ludD4KCQkJCQk8aW50\nPjEzODIxMDA3MTwvaW50PgoJCQkJCTxpbnQ+MTM4MjEwMTA3PC9pbnQ+CgkJCQkJPGludD4xMzgy\nMzIyMDA8L2ludD4KCQkJCQk8aW50PjEzODIzNzA4ODwvaW50PgoJCQkJCTxpbnQ+MTM4Mjc3NTQ3\nPC9pbnQ+CgkJCQkJPGludD4xMzgyODcxMzM8L2ludD4KCQkJCQk8aW50PjEzODMwNjk5MTwvaW50\nPgoJCQkJCTxpbnQ+MTM4MzI0NjI1PC9pbnQ+CgkJCQkJPGludD4xMzgzNDE5MTY8L2ludD4KCQkJ\nCQk8aW50PjEzODM3MjAzNTwvaW50PgoJCQkJCTxpbnQ+MTM4MzcyMDM2PC9pbnQ+CgkJCQkJPGlu\ndD4xMzgzNzUxMTg8L2ludD4KCQkJCQk8aW50PjEzODM3ODA3MTwvaW50PgoJCQkJCTxpbnQ+MTM4\nMzgwMTI4PC9pbnQ+CgkJCQkJPGludD4xMzgzODAxOTQ8L2ludD4KCQkJCQk8aW50PjEzODUzNDQx\nMTwvaW50PgoJCQkJCTxpbnQ+MTM4NjE4Mjk0PC9pbnQ+CgkJCQkJPGludD4xMzg5MzE3NjQ8L2lu\ndD4KCQkJCQk8aW50PjEzOTUzNjAzNzwvaW50PgoJCQkJCTxpbnQ+MTM5NTM2MDM4PC9pbnQ+CgkJ\nCQkJPGludD4xMzk1MzYwMzk8L2ludD4KCQkJCQk8aW50PjEzOTUzNjA0MDwvaW50PgoJCQkJCTxp\nbnQ+MTQwMzY3ODMyPC9pbnQ+CgkJCQkJPGludD4xNDA0MDYwNTA8L2ludD4KCQkJCQk8aW50PjE0\nMDQyMTY2ODwvaW50PgoJCQkJCTxpbnQ+MTQwNDIyOTczPC9pbnQ+CgkJCQkJPGludD4xNDA0MjM3\nMTM8L2ludD4KCQkJCQk8aW50PjE0MDQzNjM0ODwvaW50PgoJCQkJCTxpbnQ+MTQwNDgzNDcwPC9p\nbnQ+CgkJCQkJPGludD4xNDA2MTU3MTU8L2ludD4KCQkJCQk8aW50PjE0MDgwMjgwMzwvaW50PgoJ\nCQkJCTxpbnQ+MTQwODk2NDcwPC9pbnQ+CgkJCQkJPGludD4xNDExODk0Mzc8L2ludD4KCQkJCQk8\naW50PjE0MTE5Mjc0NDwvaW50PgoJCQkJCTxpbnQ+MTQxMzgyNTQ4PC9pbnQ+CgkJCQkJPGludD4x\nNDE0NjE2ODA8L2ludD4KCQkJCQk8aW50PjE0MTYyNDk5NjwvaW50PgoJCQkJCTxpbnQ+MTQxNjI3\nMTM1PC9pbnQ+CgkJCQkJPGludD4xNDE2NTkxMzk8L2ludD4KCQkJCQk8aW50PjE0MTg3MjAzODwv\naW50PgoJCQkJCTxpbnQ+MTQxOTkzNzIxPC9pbnQ+CgkJCQkJPGludD4xNDIwMDY0MTM8L2ludD4K\nCQkJCQk8aW50PjE0MjA0NTEzNjwvaW50PgoJCQkJCTxpbnQ+MTQyMDk1NjY3PC9pbnQ+CgkJCQkJ\nPGludD4xNDIyMjcyNzM8L2ludD4KCQkJCQk8aW50PjE0MjI1MDQ4MDwvaW50PgoJCQkJCTxpbnQ+\nMTQyNTE4Nzg4PC9pbnQ+CgkJCQkJPGludD4xNDI1NDQ5MzE8L2ludD4KCQkJCQk8aW50PjE0MjU0\nNjMxNDwvaW50PgoJCQkJCTxpbnQ+MTQyNTU1NDMzPC9pbnQ+CgkJCQkJPGludD4xNDI2NTMwNDQ8\nL2ludD4KCQkJCQk8aW50PjE0MzE5MTg1MjwvaW50PgoJCQkJCTxpbnQ+MTQzMjU4NDk2PC9pbnQ+\nCgkJCQkJPGludD4xNDMyOTk3MjI8L2ludD4KCQkJCQk8aW50PjE0MzMzMTI1MzwvaW50PgoJCQkJ\nCTxpbnQ+MTQzNDMyNDYyPC9pbnQ+CgkJCQkJPGludD4xNDM2MzI0MzE8L2ludD4KCQkJCQk8aW50\nPjE0MzY5NTMyNjwvaW50PgoJCQkJCTxpbnQ+MTQ0MjE5NTIyPC9pbnQ+CgkJCQkJPGludD4xNDQ1\nOTA5MTY8L2ludD4KCQkJCQk8aW50PjE0NTQxMDQzNjwvaW50PgoJCQkJCTxpbnQ+MTQ2NzIwNDA1\nPC9pbnQ+CgkJCQkJPGludD4xNTA4MTA0Mzg8L2ludD4KCQkJCQk8aW50PjE1MTI1ODc3MzwvaW50\nPgoJCQkJCTxpbnQ+MTUxMzE1NTU0PC9pbnQ+CgkJCQkJPGludD4xNTE0MDAwOTA8L2ludD4KCQkJ\nCQk8aW50PjE1MTQyOTQ0MTwvaW50PgoJCQkJCTxpbnQ+MTUxNDM5NjE3PC9pbnQ+CgkJCQkJPGlu\ndD4xNTE0NTM2MTc8L2ludD4KCQkJCQk8aW50PjE1MTQ2NjI5NjwvaW50PgoJCQkJCTxpbnQ+MTUx\nNTExMTMyPC9pbnQ+CgkJCQkJPGludD4xNTE2MzY1NjE8L2ludD4KCQkJCQk8aW50PjE1MTgyMzE5\nMjwvaW50PgoJCQkJCTxpbnQ+MTUxODI3MTE2PC9pbnQ+CgkJCQkJPGludD4xNTE4NTA2NDI8L2lu\ndD4KCQkJCQk8aW50PjE1MjAxNjU3MjwvaW50PgoJCQkJCTxpbnQ+MTUzMTExNjc1PC9pbnQ+CgkJ\nCQkJPGludD4xNTMxMTQ2NTI8L2ludD4KCQkJCQk8aW50PjE1MzEyMzE0NzwvaW50PgoJCQkJCTxp\nbnQ+MTUzMjY3MTA4PC9pbnQ+CgkJCQkJPGludD4xNTMzODk3OTk8L2ludD4KCQkJCQk8aW50PjE1\nMzM5NTM2NjwvaW50PgoJCQkJCTxpbnQ+MTUzNzE4NjA4PC9pbnQ+CgkJCQkJPGludD4xNTQxNzEw\nMjg8L2ludD4KCQkJCQk8aW50PjE1NDMxNTIyNzwvaW50PgoJCQkJCTxpbnQ+MTU0NTU5Njg4PC9p\nbnQ+CgkJCQkJPGludD4xNTQ5Nzg3NzE8L2ludD4KCQkJCQk8aW50PjE1NDk3OTc0MjwvaW50PgoJ\nCQkJCTxpbnQ+MTU0OTg1NzczPC9pbnQ+CgkJCQkJPGludD4xNTQ5ODkzNzA8L2ludD4KCQkJCQk8\naW50PjE1NTA0NDg1MjwvaW50PgoJCQkJCTxpbnQ+MTU1MDY1NDU4PC9pbnQ+CgkJCQkJPGludD4x\nNTU1Nzg1NzM8L2ludD4KCQkJCQk8aW50PjE1NjQwMzMwNDwvaW50PgoJCQkJCTxpbnQ+MTU5MDg1\nOTU5PC9pbnQ+CgkJCQkJPGludD4xNTk3NzYwNDc8L2ludD4KCQkJCQk8aW50PjE1OTgxNjYzMDwv\naW50PgoJCQkJCTxpbnQ+MTYwNzMzMDQ4PC9pbnQ+CgkJCQkJPGludD4xNjA3MzMwNDk8L2ludD4K\nCQkJCQk8aW50PjE2MDczMzA1MDwvaW50PgoJCQkJCTxpbnQ+MTYwNzMzMDUxPC9pbnQ+CgkJCQkJ\nPGludD4xNjA3MzMwNTY8L2ludD4KCQkJCQk8aW50PjE2NDgyNDkyMjwvaW50PgoJCQkJCTxpbnQ+\nMTY0ODI0OTI0PC9pbnQ+CgkJCQkJPGludD4xNjQ4MjQ5MjY8L2ludD4KCQkJCQk8aW50PjE2NDgy\nNDkzMDwvaW50PgoJCQkJCTxpbnQ+MTY0ODMxNjQ2PC9pbnQ+CgkJCQkJPGludD4xNjQ4MzE2NDc8\nL2ludD4KCQkJCQk8aW50PjE2NDgzMTY0ODwvaW50PgoJCQkJCTxpbnQ+MTY0ODMxNjUwPC9pbnQ+\nCgkJCQkJPGludD4xNjQ4MzUwNTA8L2ludD4KCQkJCQk8aW50PjE2NDgzNTA1MTwvaW50PgoJCQkJ\nCTxpbnQ+MTY0ODM1MDUyPC9pbnQ+CgkJCQkJPGludD4xNjQ4MzUwNTY8L2ludD4KCQkJCQk8aW50\nPjE2NDgzNTA1NzwvaW50PgoJCQkJCTxpbnQ+MTY0ODM1MDU5PC9pbnQ+CgkJCQkJPGludD4xNjQ4\nMzY4OTg8L2ludD4KCQkJCQk8aW50PjE2NDgzNjg5OTwvaW50PgoJCQkJCTxpbnQ+MTY0ODM2OTAw\nPC9pbnQ+CgkJCQkJPGludD4xNjQ4NDUzMzM8L2ludD4KCQkJCQk8aW50PjE2NDg0NTMzNDwvaW50\nPgoJCQkJCTxpbnQ+MTY0ODQ1MzM2PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDUzMzc8L2ludD4KCQkJ\nCQk8aW50PjE2NDg0NTM0MTwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ1MzQyPC9pbnQ+CgkJCQkJPGlu\ndD4xNjQ4NDUzNDU8L2ludD4KCQkJCQk8aW50PjE2NDg0NTM0NjwvaW50PgoJCQkJCTxpbnQ+MTY0\nODQ1MzQ5PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDUzNTA8L2ludD4KCQkJCQk8aW50PjE2NDg0NTM1\nMzwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ1MzU1PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDUzNTg8L2lu\ndD4KCQkJCQk8aW50PjE2NDg0NTM2MTwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ1MzY0PC9pbnQ+CgkJ\nCQkJPGludD4xNjQ4NDczODc8L2ludD4KCQkJCQk8aW50PjE2NDg0NzM4ODwvaW50PgoJCQkJCTxp\nbnQ+MTY0ODQ3Mzg5PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDczOTA8L2ludD4KCQkJCQk8aW50PjE2\nNDg0ODMyODwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ4MzI5PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDgz\nMzA8L2ludD4KCQkJCQk8aW50PjE2NDg0OTQ0ODwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ5NDQ5PC9p\nbnQ+CgkJCQkJPGludD4xNjQ4NDk0NTE8L2ludD4KCQkJCQk8aW50PjE2NDg0OTQ1MjwvaW50PgoJ\nCQkJCTxpbnQ+MTY0ODQ5NDU0PC9pbnQ+CgkJCQkJPGludD4xNjQ4NDk0NTU8L2ludD4KCQkJCQk8\naW50PjE2NDg0OTQ1NzwvaW50PgoJCQkJCTxpbnQ+MTY0ODQ5NDYxPC9pbnQ+CgkJCQkJPGludD4x\nNjQ4NTAyMTk8L2ludD4KCQkJCQk8aW50PjE2NDg1MDIyMDwvaW50PgoJCQkJCTxpbnQ+MTY0ODUw\nMjIyPC9pbnQ+CgkJCQkJPGludD4xNjQ4NTAyMjM8L2ludD4KCQkJCQk8aW50PjE2NDg1MDIyNDwv\naW50PgoJCQkJCTxpbnQ+MTY0ODUwMjI2PC9pbnQ+CgkJCQkJPGludD4xNjQ4NTAyMjc8L2ludD4K\nCQkJCQk8aW50PjE2NDg1MDIyODwvaW50PgoJCQkJCTxpbnQ+MTY0ODUwMjI5PC9pbnQ+CgkJCQkJ\nPGludD4xNjQ4NTAyMzE8L2ludD4KCQkJCQk8aW50PjE2NDg1MDIzNjwvaW50PgoJCQkJCTxpbnQ+\nMTY0ODUwMjM3PC9pbnQ+CgkJCQkJPGludD4xNjQ4NTAyNDA8L2ludD4KCQkJCQk8aW50PjE2NDg1\nMDI0MjwvaW50PgoJCQkJCTxpbnQ+MTY0ODUwMjQzPC9pbnQ+CgkJCQkJPGludD4xNjQ4NTIyNDI8\nL2ludD4KCQkJCQk8aW50PjE2NDg1MjI0MzwvaW50PgoJCQkJCTxpbnQ+MTY0ODUyMjQ0PC9pbnQ+\nCgkJCQkJPGludD4xNjQ4NTIyNDc8L2ludD4KCQkJCQk8aW50PjE2NDg1MjI0ODwvaW50PgoJCQkJ\nCTxpbnQ+MTY0ODUyMjQ5PC9pbnQ+CgkJCQkJPGludD4xNjQ4NTIyNTA8L2ludD4KCQkJCQk8aW50\nPjE2NDg1MjI1MTwvaW50PgoJCQkJCTxpbnQ+MTY0ODUyMjU0PC9pbnQ+CgkJCQkJPGludD4xNjQ4\nNTIyNTY8L2ludD4KCQkJCQk8aW50PjE2NDg1MjI1NzwvaW50PgoJCQkJCTxpbnQ+MTY0ODUyMjU4\nPC9pbnQ+CgkJCQkJPGludD4xNjQ4NTIyNTk8L2ludD4KCQkJCQk8aW50PjE2NDg1MjI2MDwvaW50\nPgoJCQkJCTxpbnQ+MTY0ODUyMjYxPC9pbnQ+CgkJCQkJPGludD4xNjQ4NTIyNjI8L2ludD4KCQkJ\nCQk8aW50PjE2NDg1MzA2MTwvaW50PgoJCQkJCTxpbnQ+MTY0ODUzMDYzPC9pbnQ+CgkJCQkJPGlu\ndD4xNjQ4NTMwNzE8L2ludD4KCQkJCQk8aW50PjE2NDg1MzA3MjwvaW50PgoJCQkJCTxpbnQ+MTY0\nODUzMDc1PC9pbnQ+CgkJCQkJPGludD4xNjgxMTg5ODA8L2ludD4KCQkJCQk8aW50PjE2ODExODk4\nMTwvaW50PgoJCQkJCTxpbnQ+MTY4MTE4OTgzPC9pbnQ+CgkJCQkJPGludD4xNjgxMTg5ODQ8L2lu\ndD4KCQkJCQk8aW50PjE2ODE4MDM3NTwvaW50PgoJCQkJCTxpbnQ+MTY4MTgwMzc2PC9pbnQ+CgkJ\nCQkJPGludD4xNjgxODAzNzg8L2ludD4KCQkJCQk8aW50PjE2ODE4MDM3OTwvaW50PgoJCQkJCTxp\nbnQ+MTY4MjcwODMwPC9pbnQ+CgkJCQkJPGludD4xNjgyNzA4MzE8L2ludD4KCQkJCQk8aW50PjE2\nODI3MDgzMzwvaW50PgoJCQkJCTxpbnQ+MTY4MjcwODM0PC9pbnQ+CgkJCQkJPGludD4xNjgyNzA4\nMzU8L2ludD4KCQkJCTwvT3RoZXJDYWNoZWRVcGRhdGVJRHM+CgkJCQk8U2tpcFNvZnR3YXJlU3lu\nYz5mYWxzZTwvU2tpcFNvZnR3YXJlU3luYz4KCQkJCTxOZWVkVHdvR3JvdXBPdXRPZlNjb3BlVXBk\nYXRlcz50cnVlPC9OZWVkVHdvR3JvdXBPdXRPZlNjb3BlVXBkYXRlcz4KCQkJCTxGaWx0ZXJBcHBD\nYXRlZ29yeUlkcz4KCQkJCQk8Q2F0ZWdvcnlJZGVudGlmaWVyPgoJCQkJCQk8SWQ+ezF9PC9JZD4K\nCQkJCQk8L0NhdGVnb3J5SWRlbnRpZmllcj4KCQkJCTwvRmlsdGVyQXBwQ2F0ZWdvcnlJZHM+CgkJ\nCQk8VHJlYXRBcHBDYXRlZ29yeUlkc0FzSW5zdGFsbGVkPnRydWU8L1RyZWF0QXBwQ2F0ZWdvcnlJ\nZHNBc0luc3RhbGxlZD4KCQkJCTxBbHNvUGVyZm9ybVJlZ3VsYXJTeW5jPmZhbHNlPC9BbHNvUGVy\nZm9ybVJlZ3VsYXJTeW5jPgoJCQkJPENvbXB1dGVyU3BlYyAvPgoJCQkJPEV4dGVuZGVkVXBkYXRl\nSW5mb1BhcmFtZXRlcnM+CgkJCQkJPFhtbFVwZGF0ZUZyYWdtZW50VHlwZXM+CgkJCQkJCTxYbWxV\ncGRhdGVGcmFnbWVudFR5cGU+RXh0ZW5kZWQ8L1htbFVwZGF0ZUZyYWdtZW50VHlwZT4KCQkJCQk8\nL1htbFVwZGF0ZUZyYWdtZW50VHlwZXM+CgkJCQkJPExvY2FsZXM+CgkJCQkJCTxzdHJpbmc+ZW4t\nVVM8L3N0cmluZz4KCQkJCQkJPHN0cmluZz5lbjwvc3RyaW5nPgoJCQkJCTwvTG9jYWxlcz4KCQkJ\nCTwvRXh0ZW5kZWRVcGRhdGVJbmZvUGFyYW1ldGVycz4KCQkJCTxDbGllbnRQcmVmZXJyZWRMYW5n\ndWFnZXM+CgkJCQkJPHN0cmluZz5lbi1VUzwvc3RyaW5nPgoJCQkJPC9DbGllbnRQcmVmZXJyZWRM\nYW5ndWFnZXM+CgkJCQk8UHJvZHVjdHNQYXJhbWV0ZXJzPgoJCQkJCTxTeW5jQ3VycmVudFZlcnNp\nb25Pbmx5PmZhbHNlPC9TeW5jQ3VycmVudFZlcnNpb25Pbmx5PgoJCQkJCTxEZXZpY2VBdHRyaWJ1\ndGVzPgoJCQkJCQlCcmFuY2hSZWFkaW5lc3NMZXZlbD1DQjtDdXJyZW50QnJhbmNoPXJzX3ByZXJl\nbGVhc2U7RmxpZ2h0UmluZz17Mn07RmxpZ2h0aW5nQnJhbmNoTmFtZT1leHRlcm5hbDtJc0ZsaWdo\ndGluZ0VuYWJsZWQ9MTtJbnN0YWxsTGFuZ3VhZ2U9ZW4tVVM7T1NVSUxvY2FsZT1lbi1VUztJbnN0\nYWxsYXRpb25UeXBlPUNsaWVudDtEZXZpY2VGYW1pbHk9V2luZG93cy5EZXNrdG9wOwoJCQkJCTwv\nRGV2aWNlQXR0cmlidXRlcz4KCQkJCQk8Q2FsbGVyQXR0cmlidXRlcz5JbnRlcmFjdGl2ZT0xO0lz\nU2Vla2VyPTA7PC9DYWxsZXJBdHRyaWJ1dGVzPgoJCQkJCTxQcm9kdWN0cyAvPgoJCQkJPC9Qcm9k\ndWN0c1BhcmFtZXRlcnM+CgkJCTwvcGFyYW1ldGVycz4KCQk8L1N5bmNVcGRhdGVzPgoJPC9zOkJv\nZHk+CjwvczpFbnZlbG9wZT4=\n'
FE3FileUrl_xml = 'PEVudmVsb3BlIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAzLzA1L3NvYXAtZW52ZWxvcGUi\nCiAgICB4bWxuczphPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1LzA4L2FkZHJlc3NpbmciCiAgICB4\nbWxuczp1PSJodHRwOi8vZG9jcy5vYXNpcy1vcGVuLm9yZy93c3MvMjAwNC8wMS9vYXNpcy0yMDA0\nMDEtd3NzLXdzc2VjdXJpdHktdXRpbGl0eS0xLjAueHNkIj4KICAgIDxIZWFkZXI+CiAgICAgICAg\nPGE6QWN0aW9uIG11c3RVbmRlcnN0YW5kPSIxIj4KICAgICAgICAgICAgaHR0cDovL3d3dy5taWNy\nb3NvZnQuY29tL1NvZnR3YXJlRGlzdHJpYnV0aW9uL1NlcnZlci9DbGllbnRXZWJTZXJ2aWNlL0dl\ndEV4dGVuZGVkVXBkYXRlSW5mbzI8L2E6QWN0aW9uPgogICAgICAgIDxhOlRvIG11c3RVbmRlcnN0\nYW5kPSIxIj4KICAgICAgICAgICAgaHR0cHM6Ly9mZTNjci5kZWxpdmVyeS5tcC5taWNyb3NvZnQu\nY29tL0NsaWVudFdlYlNlcnZpY2UvY2xpZW50LmFzbXgvc2VjdXJlZDwvYTpUbz4KICAgICAgICA8\nU2VjdXJpdHkgbXVzdFVuZGVyc3RhbmQ9IjEiCiAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vZG9j\ncy5vYXNpcy1vcGVuLm9yZy93c3MvMjAwNC8wMS9vYXNpcy0yMDA0MDEtd3NzLXdzc2VjdXJpdHkt\nc2VjZXh0LTEuMC54c2QiPgogICAgICAgICAgICA8V2luZG93c1VwZGF0ZVRpY2tldHNUb2tlbgog\nICAgICAgICAgICAgICAgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vbXN1cy8y\nMDE0LzEwL1dpbmRvd3NVcGRhdGVBdXRob3JpemF0aW9uIgogICAgICAgICAgICAgICAgdTppZD0i\nQ2xpZW50TVNBIj4KICAgICAgICAgICAgICAgIDwhLS0gPFRpY2tldFR5cGUgTmFtZT0iTVNBIiBW\nZXJzaW9uPSIxLjAiIFBvbGljeT0iTUJJX1NTTCI+PFVzZXIvPjwvVGlja2V0VHlwZT4gLS0+CiAg\nICAgICAgICAgIDwvV2luZG93c1VwZGF0ZVRpY2tldHNUb2tlbj4KICAgICAgICA8L1NlY3VyaXR5\nPgogICAgPC9IZWFkZXI+CiAgICA8Qm9keT4KICAgICAgICA8R2V0RXh0ZW5kZWRVcGRhdGVJbmZv\nMgogICAgICAgICAgICB4bWxucz0iaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL1NvZnR3YXJlRGlz\ndHJpYnV0aW9uL1NlcnZlci9DbGllbnRXZWJTZXJ2aWNlIj4KICAgICAgICAgICAgPHVwZGF0ZUlE\ncz4KICAgICAgICAgICAgICAgIDxVcGRhdGVJZGVudGl0eT4KICAgICAgICAgICAgICAgICAgICA8\nVXBkYXRlSUQ+ezB9PC9VcGRhdGVJRD4KICAgICAgICAgICAgICAgICAgICA8UmV2aXNpb25OdW1i\nZXI+ezF9PC9SZXZpc2lvbk51bWJlcj4KICAgICAgICAgICAgICAgIDwvVXBkYXRlSWRlbnRpdHk+\nCiAgICAgICAgICAgIDwvdXBkYXRlSURzPgogICAgICAgICAgICA8aW5mb1R5cGVzPgogICAgICAg\nICAgICAgICAgPFhtbFVwZGF0ZUZyYWdtZW50VHlwZT5GaWxlVXJsPC9YbWxVcGRhdGVGcmFnbWVu\ndFR5cGU+CiAgICAgICAgICAgICAgICA8WG1sVXBkYXRlRnJhZ21lbnRUeXBlPkZpbGVEZWNyeXB0\naW9uPC9YbWxVcGRhdGVGcmFnbWVudFR5cGU+CiAgICAgICAgICAgIDwvaW5mb1R5cGVzPgogICAg\nICAgICAgICA8ZGV2aWNlQXR0cmlidXRlcz5GbGlnaHRSaW5nPXsyfTs8L2RldmljZUF0dHJpYnV0\nZXM+CiAgICAgICAgPC9HZXRFeHRlbmRlZFVwZGF0ZUluZm8yPgogICAgPC9Cb2R5Pgo8L0VudmVs\nb3BlPg==\n'

def os_arc():
    machine = platform.machine().lower()

    if machine.endswith("arm64"):
        return "arm64"
    if machine.endswith("64"):
        return "x64"
    if machine.endswith("32") or machine.endswith("86"):
        return "x86"
    else:
        return "arm"


# cleans My.name.1.2 -> myname
def clean_name(badname):
    name = "".join(
        [(i if (64 < ord(i) < 91 or 96 < ord(i) < 123) else "") for i in badname]
    )
    return name.lower()


def select_best(items, curr_arch, ignore_ver=False, is_installer=False):
    """
    Select best item based on scoring system.
    For UWP: Prioritize arch -> file type -> date -> version
    For installers: Prioritize arch -> locale -> installer type
    """

    def score(item):
        if is_installer:
            arch, locale, inst_type, url = item
            # 2 = exact arch, 1 = neutral, 0 = other
            arch_score = 2 if arch == curr_arch else (1 if arch == "neutral" else 0)
            # 2 = en-us, 1 = en/us contained, 0 = other
            locale_score = (
                2
                if locale == "en-us"
                else 1
                if ("en" in locale or "us" in locale)
                else 0
            )
            return (arch_score, locale_score, inst_type)
        else:
            arch, ext, modified_str, version_str = item
            fav_type = {"appx", "msix", "msixbundle", "appxbundle"}
            arch_score = 2 if arch == curr_arch else (1 if arch == "neutral" else 0)
            type_score = 1 if ext in fav_type else 0

            if ignore_ver:
                dt = 0
                ver_tuple = (0, 0, 0, 0)
            else:
                clean_str = modified_str.rstrip("Z")
                clean_str = re.sub(r"(\.\d{6})\d+", r"\1", clean_str)
                dt = datetime.datetime.fromisoformat(clean_str)
                ver_tuple = tuple(map(int, version_str.split(".")))
            return (arch_score, type_score, dt, ver_tuple)

    # Filter arch to (curr_arch or "neutral"), else fallback
    candidates = [item for item in items if item[0] in (curr_arch, "neutral")]
    candidates = candidates or items

    return max(candidates, key=score)


def parse_dict(main_dict, file_name, ignore_ver, all_dependencies, arch):
    """Parse the dictionary and return the best file(s)"""
    # Prep the incoming 'file_name' for matching
    base_name = clean_name(file_name.split("-")[0])
    blockmap_pattern = re.compile(r".+\.BlockMap")

    # Build a dictionary of structured data for easy lookup
    full_data = {}
    for key, value in main_dict.items():
        if not blockmap_pattern.search(str(key)):
            parts = key.split("_")
            mapped_key = (
                clean_name(parts[0]),
                parts[2].lower(),
                parts[-1].split(".")[1].lower(),
                value,
                parts[1],
            )
            full_data[mapped_key] = key

    # Collect entries by their “cleaned-up name”
    names_dict = {}
    for mapped_key in full_data:
        name_base = mapped_key[0]
        names_dict.setdefault(name_base, []).append(mapped_key[1:])

    file_arch = None
    main_file_name_entry = None
    pat_main = re.compile(base_name)
    sys_arch = arch or os_arc()

    # Identify the main file
    matching_base = None
    for name_base in names_dict:
        if pat_main.search(name_base):
            matching_base = name_base
            break

    # Process matching entry if found
    if matching_base:
        content_list = names_dict[matching_base]
        arch, ext, modified, version = select_best(content_list, sys_arch)
        main_file_name_entry = full_data[(matching_base, arch, ext, modified, version)]
        file_arch = sys_arch if arch == "neutral" else arch
        del names_dict[matching_base]
    else:
        raise Exception("No file found")

    # Gather dependencies or single-file results
    final_list = []
    for name_base, content_list in names_dict.items():
        if all_dependencies:
            for data in content_list:
                final_list.append(full_data[(name_base, *data)])
        else:
            arch, ext, modified, version = select_best(
                content_list, file_arch, ignore_ver
            )
            final_list.append(full_data[(name_base, arch, ext, modified, version)])

    # If we found a main file, append it
    if main_file_name_entry:
        final_list.append(main_file_name_entry)
        file_name = main_file_name_entry
    else:
        # If no explicit main file found, pick the first from final_list
        if final_list:
            file_name = final_list[0]

    return final_list, file_name


async def uwp_gen(session, data_list, ignore_ver, all_dependencies, arch):
    """Get UWP app installer info from Microsoft Store"""
    cat_id = data_list["WuCategoryId"]
    main_file_name = data_list["PackageFamilyName"].split("_")[0]
    release_type = "retail"

    # 1. Get encrypted cookie
    # with open(f"{script_dir}/data/xml/GetCookie.xml", "r") as f:
        # cookie_template = f.read()
    cookie_template = base64.decodebytes(GetCookie_xml.encode('utf-8')).decode("utf-8")
    
    response_text = await (
        await session.post(
            "https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx",
            data=cookie_template,
            headers={"Content-Type": "application/soap+xml; charset=utf-8"},
        )
    ).text()

    cookie_doc = minidom.parseString(response_text)
    cookie = cookie_doc.getElementsByTagName("EncryptedData")[0].firstChild.nodeValue

    # 2. Request IDs and filenames
    # with open(f"{script_dir}/data/xml/WUIDRequest.xml", "r") as f:
        # wuid_template = f.read().format(cookie, cat_id, release_type)
    wuid_xml = base64.decodebytes(WUIDRequest_xml.encode('utf-8')).decode("utf-8").format(cookie, cat_id, release_type)
    wuid_template = wuid_xml.format(cookie, cat_id, release_type)

    response_text = await (
        await session.post(
            "https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx",
            data=wuid_template,
            headers={"Content-Type": "application/soap+xml; charset=utf-8"},
        )
    ).text()

    xml_doc = minidom.parseString(html.unescape(response_text))

    # Collect filenames {ID: (prefixed_filename, modifiedDate)}
    filenames_map = {}
    for files_node in xml_doc.getElementsByTagName("Files"):
        try:
            node_id = files_node.parentNode.parentNode.getElementsByTagName("ID")[
                0
            ].firstChild.nodeValue
            prefix = files_node.firstChild.attributes[
                "InstallerSpecificIdentifier"
            ].value
            fname = files_node.firstChild.attributes["FileName"].value
            modified = files_node.firstChild.attributes["Modified"].value
            filenames_map[node_id] = (f"{prefix}_{fname}", modified)
        except KeyError:
            continue

    if not filenames_map:
        raise Exception("server returned an empty list")

    # 3. Parse update IDs from SecuredFragment
    identities = {}
    name_modified = {}
    for fragment_node in xml_doc.getElementsByTagName("SecuredFragment"):
        try:
            fn_id = fragment_node.parentNode.parentNode.parentNode.getElementsByTagName(
                "ID"
            )[0].firstChild.nodeValue
            file_name, modified = filenames_map[fn_id]
            top_node = fragment_node.parentNode.parentNode.firstChild
            update_id = top_node.attributes["UpdateID"].value
            rev_num = top_node.attributes["RevisionNumber"].value

            name_modified[file_name] = modified
            identities[file_name] = (update_id, rev_num)
        except KeyError:
            continue

    # 4. Choose the best files via parse_dict
    parse_names, main_file_name = parse_dict(
        name_modified, main_file_name, ignore_ver, all_dependencies, arch
    )

    # Build a dict of {filename: (update_id, revision_number)}
    final_dict = {}
    for val in parse_names:
        final_dict[val] = identities[val]

    # 5. Download URLs for each selected file
    # with open(f"{script_dir}/data/xml/FE3FileUrl.xml", "r") as f:
        # file_template = f.read()
    file_template = base64.decodebytes(FE3FileUrl_xml.encode('utf-8')).decode("utf-8")

    file_dict = {}

    async def geturl(update_id, revision_num, file_name):
        resp_text = await (
            await session.post(
                "https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx/secured",
                data=file_template.format(update_id, revision_num, release_type),
                headers={"Content-Type": "application/soap+xml; charset=utf-8"},
            )
        ).text()
        doc = minidom.parseString(resp_text)
        for loc in doc.getElementsByTagName("FileLocation"):
            url = loc.getElementsByTagName("Url")[0].firstChild.nodeValue
            # blockmap vs actual file
            if len(url) != 99:
                file_dict[file_name] = url

    tasks = []
    for file_name, (upd_id, rev_num) in final_dict.items():
        tasks.append(asyncio.create_task(geturl(upd_id, rev_num, file_name)))

    await asyncio.gather(*tasks)

    # 6. Verify everything downloaded
    if len(file_dict) != len(final_dict):
        raise Exception("server returned an incomplete list")

    return (
        file_dict,  # {name: url}
        parse_names,  # file name list
        main_file_name,  # main file
        True,  # is_uwp flag
    )


async def non_uwp_gen(session, product_id, arch):
    """Get non-UWP app installer info from Microsoft Store"""

    # 1. Fetch package manifest
    api_url = (
        f"https://storeedgefd.dsx.mp.microsoft.com/v9.0/packageManifests/{product_id}"
    )
    api_params = "?market=US&locale=en-us&deviceFamily=Windows.Desktop"

    response = await session.get(api_url + api_params)
    data = json.loads(await response.text())

    if not data.get("Data"):
        raise Exception("Server returned empty package data")

    # 2. Get package name and installers
    package_name = data["Data"]["Versions"][0]["DefaultLocale"]["PackageName"]
    installers = data["Data"]["Versions"][0]["Installers"]

    # 3. Extract unique installer combinations
    installer_options = {
        (i["Architecture"], i["InstallerLocale"], i["InstallerType"], i["InstallerUrl"])
        for i in installers
    }

    # 5. Build result
    chosen = select_best(
        installer_options, curr_arch=arch or os_arc(), is_installer=True
    )
    main_file_name = f"{clean_name(package_name)}.{chosen[2]}"

    return (
        {main_file_name: chosen[3]},  # file_dict
        [main_file_name],  # file list
        main_file_name,  # main file
        False,  # is_uwp flag
    )


def extract_product_id(url):
    """Extract product ID from Microsoft Store URL"""
    pattern = re.compile(r".+\/([^\/\?]+)(?:\?|$)")
    if match := pattern.search(str(url)):
        return match.group(1)
    raise ValueError("Invalid URL format - Please provide a valid Microsoft Store URL")


async def fetch_product_details(session, product_id):
    """Fetch product details from Microsoft Store API"""
    api_url = f"https://storeedgefd.dsx.mp.microsoft.com/v9.0/products/{product_id}"
    params = "?market=US&locale=en-us&deviceFamily=Windows.Desktop"

    async with session.get(api_url + params) as response:
        data = await response.text()
        return json.loads(
            data,
            object_hook=lambda obj: {
                k: json.loads(v) if k == "FulfillmentData" else v
                for k, v in obj.items()
            },
        )


async def url_generator(url, ignore_ver, all_dependencies, arch):
    """Generate download URLs for Microsoft Store apps"""
    try:
        product_id = extract_product_id(url)

        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(
            timeout=timeout, raise_for_status=True
        ) as session:
            response = await fetch_product_details(session, product_id)

            if not response.get("Payload"):
                raise ValueError("Invalid product ID or URL")

            # Get fulfillment data from response
            data_list = response["Payload"]["Skus"][0].get("FulfillmentData")

            # Route to appropriate handler based on app type
            if data_list:
                return await uwp_gen(
                    session, data_list, ignore_ver, all_dependencies, arch
                )
            return await non_uwp_gen(session, product_id, arch)

    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        raise ConnectionError(f"Failed to fetch app details: {str(e)}")
