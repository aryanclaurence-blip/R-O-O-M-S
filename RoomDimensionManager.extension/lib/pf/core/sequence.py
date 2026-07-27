# -*- coding: utf-8 -*-
"""Core Sequence Placeholder for PARAMS FLOW."""
import re

class SequenceGenerator(object):
    def __init__(self, pattern="RM-{SEQ:001}", start=1, step=1):
        self.pattern = pattern
        self.start = int(start)
        self.step = int(step)

    def generate(self, index):
        val = self.start + (index * self.step)
        return re.sub(r'\{SEQ(?::\d+)?\}', str(val).zfill(3), self.pattern)
