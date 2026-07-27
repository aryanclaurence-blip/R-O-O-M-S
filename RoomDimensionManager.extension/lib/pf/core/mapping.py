# -*- coding: utf-8 -*-
"""Parameter Mapping Models for PARAMS FLOW."""
import uuid
import time

class MappingType(object):
    COPY = "Parameter Copy"
    STATIC = "Static Value"
    SEQUENCE = "Sequence Generator"
    FIND_REPLACE = "Find & Replace"
    PREFIX = "Prefix"
    SUFFIX = "Suffix"

class ParameterMapping(object):
    def __init__(self, mapping_type=MappingType.COPY, source_param="", target_param="", static_value="", seq_pattern="RM-{SEQ:001}", seq_start=1, seq_step=1, find_str="", replace_str="", prefix_str="", suffix_str="", source_scope="Current View", source_cat="Rooms", target_cat="Rooms", mapping_id=None, enabled=True, status="Not Validated"):
        self.id = mapping_id or str(uuid.uuid4())
        self.mapping_type = mapping_type
        self.source_scope = source_scope
        self.source_cat = source_cat
        self.source_param = source_param
        self.target_cat = target_cat
        self.target_param = target_param
        self.static_value = static_value
        self.seq_pattern = seq_pattern
        self.seq_start = int(seq_start) if str(seq_start).isdigit() else 1
        self.seq_step = int(seq_step) if str(seq_step).isdigit() else 1
        self.find_str = find_str
        self.replace_str = replace_str
        self.prefix_str = prefix_str
        self.suffix_str = suffix_str
        self.enabled = enabled
        self.status = status
        self.created_time = time.time()
        self.modified_time = time.time()

    def clone(self):
        c = ParameterMapping(
            mapping_type=self.mapping_type,
            source_param=self.source_param,
            target_param=self.target_param,
            static_value=self.static_value,
            seq_pattern=self.seq_pattern,
            seq_start=self.seq_start,
            seq_step=self.seq_step,
            find_str=self.find_str,
            replace_str=self.replace_str,
            prefix_str=self.prefix_str,
            suffix_str=self.suffix_str,
            source_scope=self.source_scope,
            source_cat=self.source_cat,
            target_cat=self.target_cat,
            enabled=self.enabled,
            status=self.status
        )
        return c

    def copy(self):
        return self.clone()

    def to_dict(self):
        return {
            "id": self.id,
            "mapping_type": self.mapping_type,
            "source_scope": self.source_scope,
            "source_cat": self.source_cat,
            "source_param": self.source_param,
            "target_cat": self.target_cat,
            "target_param": self.target_param,
            "static_value": self.static_value,
            "seq_pattern": self.seq_pattern,
            "seq_start": self.seq_start,
            "seq_step": self.seq_step,
            "find_str": self.find_str,
            "replace_str": self.replace_str,
            "prefix_str": self.prefix_str,
            "suffix_str": self.suffix_str,
            "enabled": self.enabled,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            mapping_id=d.get("id"),
            mapping_type=d.get("mapping_type", MappingType.COPY),
            source_scope=d.get("source_scope", "Current View"),
            source_cat=d.get("source_cat", "Rooms"),
            source_param=d.get("source_param", ""),
            target_cat=d.get("target_cat", "Rooms"),
            target_param=d.get("target_param", ""),
            static_value=d.get("static_value", ""),
            seq_pattern=d.get("seq_pattern", "RM-{SEQ:001}"),
            seq_start=d.get("seq_start", 1),
            seq_step=d.get("seq_step", 1),
            find_str=d.get("find_str", ""),
            replace_str=d.get("replace_str", ""),
            prefix_str=d.get("prefix_str", ""),
            suffix_str=d.get("suffix_str", ""),
            enabled=d.get("enabled", True),
            status=d.get("status", "Not Validated")
        )
