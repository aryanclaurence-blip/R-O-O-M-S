# -*- coding: utf-8 -*-
"""Sequence Generator for PARAMS FLOW."""
import re

class SequenceGenerator(object):
    def __init__(self, pattern="RM-{SEQ:001}", start=1, step=1):
        self.pattern = pattern
        self.start = int(start)
        self.step = int(step)

    def generate_value(self, index):
        """Generate formatted sequence string for element at index (0-based)."""
        current_num = self.start + (index * self.step)
        
        match = re.search(r'\{SEQ(?::(\d+))?\}', self.pattern)
        if not match:
            return "{}_{}".format(self.pattern, current_num)

        fmt_spec = match.group(1)
        if fmt_spec and fmt_spec.startswith('0'):
            width = len(fmt_spec)
            seq_str = str(current_num).zfill(width)
        elif fmt_spec:
            width = int(fmt_spec)
            seq_str = str(current_num).zfill(width)
        else:
            seq_str = str(current_num)

        return re.sub(r'\{SEQ(?::\d+)?\}', seq_str, self.pattern)
