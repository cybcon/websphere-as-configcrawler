# Summary
![logo](.readme/WAS-CC_Icon.png)

The WebSphere ApplicationServer ConfigCrawler is a small jython script (running in a wsadmin interpreter) and is able to output a lot of information about your IBM WebSphere ApplicationServer environment.
All configurable with a small config file where you can choose the scope and the items to crawl.
Output can be set to XML (for easy computer based postprocessing) or as simple Text fo easy administration overview.

# Features
- Easy to use
- Good overview about your WAS configuration
- Runs on Windows and Unix Platforms
- Output on standard out - Redirect to file if needed
- Plaintext and XML output
- Tested on more than 400 different cells every night

# Installation instructions
1. Modify `crawler.conf` section `[cybcon_was]` and set
   `libPath=<path where we can find the cybcon_was.py file>`

2. Modify `crawler.conf` for your needs

3. execute crawler<br>usage:<br/>`./wsadmin.sh -lang jython -f /path/to/config_crawler.py /path/to/crawler.conf`

# Project Samples

## XML output example
![XML output](.readme/xml_output.png)

## Plaintext output example
![Plaintext output](.readme/plaintext_output.png)

## Configuration file example
![configuration file](.readme/config_file.png)

# Donate
I would appreciate a small donation to support the further development of my open source projects.

<a href="https://www.paypal.com/donate/?hosted_button_id=BHGJGGUS6RH44" target="_blank"><img src="https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png" alt="Donate with PayPal" width="200px"></a>

# COPYRIGHT AND LICENSE

(C) Copyright 2009-2023, Michael Oberdorf IT-Consulting <info@oberdorf-itc.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
```
