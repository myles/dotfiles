#!/usr/bin/env python
from random import sample
print ' '.join(sample(open('/usr/share/dict/words', 'r').read().split('\n'), 3)).title()
