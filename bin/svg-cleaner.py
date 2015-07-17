"""
A simple application that cleans up SVG files exported from
Affinity Designer[1] so they are easier to style with CSS and SVGInjector[2].

Basiclly it copies all the id to class and runs awesome-slugify on them.

[1]: https://affinity.serif.com/
[2]: https://github.com/iconic/SVGInjector

Requires: awesome-slugify==1.6.5

Copyright (c) 2015, Myles Braithwaite <me@mylesbraithwaite.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution.

* Neither the name of the Monkey in your Soul nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import xml.etree.ElementTree as ET

from slugify import slugify


def main(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    for child in root.iter():
        element_id = child.attrib.get('id', False)

        if element_id:
            element_class = slugify(element_id, to_lower=True)

            child.set('class', element_class)

    tree.write(svg_file)

if __name__ == "__main__":
    svg_file = sys.argv[1]

    if os.path.exists(svg_file):
        main(svg_file=svg_file)
