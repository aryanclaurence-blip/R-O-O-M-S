# -*- coding: utf-8 -*-
"""Parameter Mapping Models for PARAMS FLOW."""

class MappingType(object):
    COPY = "Parameter Copy"
    STATIC = "Static Value"
    SEQUENCE = "Sequence Generator"
    FIND_REPLACE = "Find & Replace"

class ParameterMapping(object):
    def __init__(self, mapping_type, source_param, target_param, static_value="", seq_pattern="RM-{SEQ:001}", seq_start=1, seq_step=1, find_str="", replace_str=""):
        self.mapping_type = mapping_type
        self.source_param = source_param
        self.target_param = target_param
        self.static_value = static_value
        self.seq_pattern = seq_pattern
        self.seq_start = int(seq_start) if str(seq_start).isdigit() else 1
        self.seq_step = int(seq_step) if str(seq_step).isdigit() else 1
        self.find_str = find_str
        self.replace_str = replace_str
        self.status = "PENDING"
        self.status_color = "#000000"

    def to_dict(self):
        return {
            "mapping_type": self.mapping_type,
            "source_param": self.source_param,
            "target_param": self.target_param,
            "static_value": self.static_value,
            "seq_pattern": self.seq_pattern,
            "seq_start": self.seq_start,
            "seq_step": self.seq_step,
            "find_str": self.find_str,
            "replace_str": self.replace_str
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            mapping_type=d.get("mapping_type", MappingType.COPY),
            source_param=d.get("source_param", ""),
            target_param=d.get("target_param", ""),
            static_value=d.get("static_value", ""),
            seq_pattern=d.get("seq_pattern", "RM-{SEQ:001}"),
            seq_start=d.get("seq_start", 1),
            seq_step=d.get("seq_step", 1),
            find_str=d.get("find_str", ""),
            replace_str=d.get("replace_str", "")
        )
