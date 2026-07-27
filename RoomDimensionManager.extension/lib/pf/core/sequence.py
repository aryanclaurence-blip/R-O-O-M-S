# -*- coding: utf-8 -*-
"""Sequence Generator for PARAMS FLOW."""
import re

class SequenceGenerator(object):
    def __init__(self, pattern="RM-{SEQ:001}", start=1, step=1):
        self.pattern = pattern
        self.start = int(start) if str(start).isdigit() else 1
        self.step = int(step) if str(step).isdigit() else 1

    def _number_to_letters(self, n):
        """Convert 1-based index into A, B, C... AA, AB... sequence."""
        res = ""
        while n > 0:
            n -= 1
            res = chr(65 + (n % 26)) + res
            n //= 26
        return res

    def generate(self, index):
        """Generate formatted sequence string for element at index (0-based)."""
        current_num = self.start + (index * self.step)

        if "{SEQ:ALPHA}" in self.pattern:
            alpha_str = self._number_to_letters(current_num)
            return self.pattern.replace("{SEQ:ALPHA}", alpha_str)

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
