# todoist_export

This program runs from your computer and communicates with the Todoist server to create a log of incomplete tasks organized by

```
[section name]
project name
    * task name
```

The complete code is [here](https://www.github.com/ShayHill/todoist_export) for review.

When you double click the executable file, a terminal window will open and ask you for the following:

* Enter your Todoist API token:

By default, the script will create an outline of *all* tasks as a Microsoft Word document named `todoist_[timestamp]`.

There is a "secret" command you can enter at the API-token prompt: "config". If you enter "config" at the API-token prompt, the program will create a template config file, `todoist_export.ini` with instructions. Right click and open this file with Notepad. You can use this file to whitelist or blacklist section and project names.

## Where is my API Token?

You can get your API token from the Todoist website by clicking

1. your profile icon in the top left
2. Settings
3. Integrations
4. Developer

Copy this and paste it into the terminal window. Do not share your API token with anyone.

## License: MIT

The MIT License (MIT)
Copyright © 2023 <Shay Hill>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## To Create an EXE

`pyinstaller src\todoist_export\main.py --upx-dir . --onefile`

This will require pyinstaller in your environment and a [upx executable](https://github.com/upx/upx/releases/tag/v4.0.2) in the root directory.
