# -*- coding: utf-8 -*-
"""Smart Dimension Parsing Engine for RoomPro pyRevit extension (v1.1).

Parses arbitrary user-entered room dimension strings into structured ParseResult objects.
Converts values to Revit internal decimal feet while strictly preserving order of appearance.
Includes configurable separators and lightweight preview/validation generation.
"""
import re

try:
    from Autodesk.Revit.DB import UnitFormatUtils
    HAS_REVIT_API = True
except ImportError:
    HAS_REVIT_API = False


class ParseResult(object):
    """Structured result returned by SmartDimensionParser."""
    def __init__(self, success=False, dim_a="", dim_b="", internal_a=None, internal_b=None,
                 original_input="", parsed_units="", confidence="Low",
                 detected_separator="none", source_type="Project Units",
                 parse_warnings=None, error_message=None):
        self.Success = success
        self.DimensionA = dim_a
        self.DimensionB = dim_b
        self.InternalA = internal_a
        self.InternalB = internal_b
        self.OriginalInput = original_input
        self.ParsedUnits = parsed_units
        self.Confidence = confidence
        self.DetectedSeparator = detected_separator
        self.SourceType = source_type
        self.ParseWarnings = parse_warnings if parse_warnings is not None else []
        self.ErrorMessage = error_message

    def get_preview(self):
        """Generate a human-readable text preview of the parse result."""
        lines = []
        lines.append("Original Value")
        lines.append(self.OriginalInput)
        lines.append("----------------------------------")
        if self.Success:
            lines.append("Dimension A    : {}".format(self.DimensionA))
            lines.append("Dimension B    : {}".format(self.DimensionB))
            lines.append("Detected Units : {}".format(self.ParsedUnits))
            lines.append("Confidence     : {}".format(self.Confidence))
            lines.append("Status         : \u2713 Parsed Successfully")
        else:
            lines.append("Status         : \u2716 Invalid Format")
            lines.append("")
            lines.append("Reason :")
            lines.append("Unable to extract two valid numeric dimensions.")
            lines.append("")
            lines.append("Supported Examples:")
            lines.append("\u2022 2.25m x 5.00m")
            lines.append("\u2022 2.25m by 5.00m")
            lines.append("\u2022 2250 x 5000")
            lines.append("\u2022 2250mm x 5000mm")
            lines.append("\u2022 10'-6\" x 12'-0\"")
        lines.append("----------------------------------")
        return "\n".join(lines)

    def __repr__(self):
        if self.Success:
            return ("<ParseResult Success=True DimA='{}' DimB='{}' InternalA={:.4f}ft InternalB={:.4f}ft "
                    "Confidence={} Source='{}' Units='{}' Separator='{}'>").format(
                        self.DimensionA, self.DimensionB,
                        self.InternalA if self.InternalA is not None else 0.0,
                        self.InternalB if self.InternalB is not None else 0.0,
                        self.Confidence, self.SourceType, self.ParsedUnits, self.DetectedSeparator)
        return "<ParseResult Success=False Error='{}'>".format(self.ErrorMessage)


class SmartDimensionParser(object):
    INVALID_FORMAT = "Invalid Format"

    # Centralized configurable collection of supported dimension separators
    SUPPORTED_SEPARATORS = ['x', 'X', '×', 'by', '*', '/', ',', ';', ':', '-']

    # Conversion factors to decimal feet (Revit internal length unit)
    UNIT_TO_FEET = {
        'm': 1.0 / 0.3048,
        'meter': 1.0 / 0.3048,
        'meters': 1.0 / 0.3048,
        'metre': 1.0 / 0.3048,
        'metres': 1.0 / 0.3048,
        'mm': 1.0 / 304.8,
        'millimeter': 1.0 / 304.8,
        'millimeters': 1.0 / 304.8,
        'millimetre': 1.0 / 304.8,
        'millimetres': 1.0 / 304.8,
        'cm': 1.0 / 30.48,
        'centimeter': 1.0 / 30.48,
        'centimeters': 1.0 / 30.48,
        'centimetre': 1.0 / 30.48,
        'centimetres': 1.0 / 30.48,
        'dm': 1.0 / 3.048,
        'decimeter': 1.0 / 3.048,
        'decimeters': 1.0 / 3.048,
        'km': 1.0 / 0.0003048,
        'ft': 1.0,
        "'": 1.0,
        'foot': 1.0,
        'feet': 1.0,
        'in': 1.0 / 12.0,
        '"': 1.0 / 12.0,
        'inch': 1.0 / 12.0,
        'inches': 1.0 / 12.0,
    }

    @classmethod
    def format_preview(cls, result_or_input, unit_helper=None):
        """Lightweight validation helper that formats a ParseResult preview string."""
        if isinstance(result_or_input, ParseResult):
            return result_or_input.get_preview()
        res = cls.parse(result_or_input, unit_helper=unit_helper)
        return res.get_preview()

    @classmethod
    def _build_separator_regex(cls):
        """Dynamically construct regex pattern from SUPPORTED_SEPARATORS."""
        escaped = [re.escape(s) for s in cls.SUPPORTED_SEPARATORS]
        return r"(?:{})".format("|".join(escaped))

    @classmethod
    def parse_single(cls, val_str, unit_helper=None, default_unit=None):
        """Parse a single length value string into decimal feet float."""
        if not val_str:
            return None
        val_str = str(val_str).strip()

        # 1. Check Feet & Inches pattern (e.g. 10'-6", 10' 6", 10', 6")
        fi_match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:'|ft|feet)\s*(?:-?\s*(\d+(?:\.\d+)?)\s*(?:\"|in|inches)?)?\s*$", val_str, re.IGNORECASE)
        if fi_match:
            feet = float(fi_match.group(1))
            inches = float(fi_match.group(2)) if fi_match.group(2) else 0.0
            return feet + (inches / 12.0)

        in_match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:\"|in|inches)\s*$", val_str, re.IGNORECASE)
        if in_match:
            return float(in_match.group(1)) / 12.0

        # 2. Check Standard Number + Unit pattern
        num_unit_match = re.match(r"^\s*([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z\"']*)\s*$", val_str)
        if num_unit_match:
            num = float(num_unit_match.group(1))
            unit = num_unit_match.group(2).lower()

            if unit in cls.UNIT_TO_FEET:
                return num * cls.UNIT_TO_FEET[unit]
            elif not unit:
                if default_unit and default_unit.lower() in cls.UNIT_TO_FEET:
                    return num * cls.UNIT_TO_FEET[default_unit.lower()]

        # 3. Try Revit API unit_helper parsing
        if unit_helper and hasattr(unit_helper, 'parse_length'):
            try:
                res = unit_helper.parse_length(val_str)
                if res is not None:
                    return res
            except Exception:
                pass

        # Fallback numeric conversion
        try:
            num = float(re.sub(r"[^\d.-]", "", val_str))
            if default_unit and default_unit.lower() in cls.UNIT_TO_FEET:
                return num * cls.UNIT_TO_FEET[default_unit.lower()]
            return num
        except Exception:
            return None

    @classmethod
    def _extract_unit(cls, val_str):
        """Extract unit token from a dimension string if present."""
        if not val_str:
            return ""
        val_str = str(val_str).strip()
        if re.search(r"['\"]|ft|feet|in|inch", val_str, re.IGNORECASE):
            return "ft-in" if re.search(r"['\"]", val_str) else "ft"
        match = re.search(r"([a-zA-Z]+)\s*$", val_str)
        if match:
            u = match.group(1).lower()
            if u in cls.UNIT_TO_FEET:
                return u
        return ""

    @classmethod
    def parse(cls, input_str, unit_helper=None):
        """Intelligently parse arbitrary dimension string into a ParseResult object.

        Returns ParseResult with Success=False and ErrorMessage='Invalid Format' if
        2 valid dimensions cannot be extracted.
        Never swaps or reorders values.
        """
        if input_str is None:
            return ParseResult(success=False, original_input="", error_message=cls.INVALID_FORMAT)

        raw_input = str(input_str).strip()
        if not raw_input:
            return ParseResult(success=False, original_input=raw_input, error_message=cls.INVALID_FORMAT)

        warnings = []
        detected_sep = "none"
        source_type = "Explicit Units"
        is_normalized_sep = False

        sep_regex_pattern = cls._build_separator_regex()

        # 1. Check Labeled Input (e.g., L=2.25m W=5.00m or W=5.00m L=2.25m)
        strict_labeled = re.findall(
            r"(?:L|W|Length|Width|Len|Wid|H|Height|B)\s*[:=]\s*(\d+(?:\.\d+)?\s*[a-zA-Z\"']*)",
            raw_input, re.IGNORECASE
        )

        cand_a_raw = None
        cand_b_raw = None

        if len(strict_labeled) == 2:
            cand_a_raw = strict_labeled[0]
            cand_b_raw = strict_labeled[1]
            detected_sep = "label"
            source_type = "Labeled Input"

        # 2. Check Feet & Inches matching (e.g. 10'-6" x 12'-0", 10'6" by 12'0")
        if not cand_a_raw and re.search(r"['\"]", raw_input):
            fi_tokens = re.findall(
                r"\d+(?:\.\d+)?\s*(?:'|ft|feet)\s*(?:-?\s*\d+(?:\.\d+)?\s*(?:\"|in|inches)?)?|\d+(?:\.\d+)?\s*(?:\"|in|inches)",
                raw_input, re.IGNORECASE
            )
            if len(fi_tokens) == 2:
                cand_a_raw = fi_tokens[0]
                cand_b_raw = fi_tokens[1]
                source_type = "Feet & Inches"
                sep_match = re.search(r"\b(" + sep_regex_pattern + r")\b", raw_input, re.IGNORECASE)
                if sep_match:
                    detected_sep = sep_match.group(1)

        # 3. Configurable Separator Normalization & Splitting
        if not cand_a_raw:
            sep_search = re.search(r"(" + sep_regex_pattern + r")", raw_input, re.IGNORECASE)
            if sep_search:
                sep_char = sep_search.group(1)
                detected_sep = sep_char
                if sep_char in ["*", "/", ",", ";", ":", "-"] or re.search(r"\d[a-zA-Z]" + re.escape(sep_char) + r"\d", raw_input):
                    is_normalized_sep = True

            # Insert spaces around configured separators for zero-space inputs like 2.25mx5.00m, 2250MMX5000MM
            normalized_text = re.sub(
                r'(?<=\d|[a-zA-Z"\'\)])\s*(' + sep_regex_pattern + r')\s*(?=\d|[a-zA-Z"\'\(])',
                r' \1 ', raw_input, flags=re.IGNORECASE
            )

            split_parts = re.split(r"\s*(?:" + sep_regex_pattern + r")\s*", normalized_text, flags=re.IGNORECASE)
            split_parts = [p.strip() for p in split_parts if p.strip()]

            if len(split_parts) == 2:
                cand_a_raw = split_parts[0]
                cand_b_raw = split_parts[1]

        # 4. Fallback Token Extraction (e.g. 2.25 m 5.00 m or 2.25 5.00)
        if not cand_a_raw:
            num_tokens = re.findall(r"\d+(?:\.\d+)?\s*[a-zA-Z\"']*", raw_input)
            if len(num_tokens) == 2:
                cand_a_raw = num_tokens[0]
                cand_b_raw = num_tokens[1]
                detected_sep = "space" if " " in raw_input else "none"

        # If we could not extract two candidate dimension tokens, return Invalid Format
        if not cand_a_raw or not cand_b_raw:
            return ParseResult(success=False, original_input=raw_input, error_message=cls.INVALID_FORMAT)

        # Clean individual candidates of prefix labels if any remained
        cand_a_str = re.sub(r"^(?:L|W|Length|Width|Len|Wid|H|Height|B)\s*[:=]\s*", "", cand_a_raw, flags=re.IGNORECASE).strip()
        cand_b_str = re.sub(r"^(?:L|W|Length|Width|Len|Wid|H|Height|B)\s*[:=]\s*", "", cand_b_raw, flags=re.IGNORECASE).strip()

        unit_a = cls._extract_unit(cand_a_str)
        unit_b = cls._extract_unit(cand_b_str)

        default_unit_a = None
        default_unit_b = None

        if source_type not in ["Feet & Inches", "Labeled Input"]:
            if unit_a and unit_b:
                source_type = "Explicit Units"
            elif unit_a and not unit_b:
                source_type = "Inherited Units"
                default_unit_b = unit_a
                warnings.append("Missing unit on second dimension. Inherited '{}' from first value.".format(unit_a))
            elif unit_b and not unit_a:
                source_type = "Inherited Units"
                default_unit_a = unit_b
                warnings.append("Missing unit on first dimension. Inherited '{}' from second value.".format(unit_b))
            else:
                source_type = "Project Units"
                warnings.append("Using Project Units because no units were specified.")

        if is_normalized_sep:
            warnings.append("Non-standard separator normalized automatically.")

        # Parse numerical values into decimal feet
        internal_a = cls.parse_single(cand_a_str, unit_helper=unit_helper, default_unit=default_unit_a)
        internal_b = cls.parse_single(cand_b_str, unit_helper=unit_helper, default_unit=default_unit_b)

        if internal_a is None or internal_b is None or internal_a <= 0.0 or internal_b <= 0.0:
            return ParseResult(success=False, original_input=raw_input, error_message=cls.INVALID_FORMAT)

        parsed_units = unit_a or unit_b or (unit_helper.name if unit_helper else "Project Units")

        # Determine Confidence Level
        if source_type in ["Explicit Units", "Feet & Inches", "Labeled Input"] and detected_sep in ["x", "X", "×", "by", "label"]:
            confidence = "High"
        elif source_type == "Inherited Units" or (source_type != "Project Units" and detected_sep in cls.SUPPORTED_SEPARATORS):
            confidence = "Medium"
        else:
            confidence = "Low"

        # Format display strings with a space between number and unit for presentation
        def format_disp(val_str, unit):
            m = re.match(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z\"']*)$", val_str)
            if m:
                num_part = m.group(1)
                u_part = m.group(2) or unit or ""
                return "{} {}".format(num_part, u_part).strip()
            return val_str

        dim_a_disp = format_disp(cand_a_str, unit_a or default_unit_a)
        dim_b_disp = format_disp(cand_b_str, unit_b or default_unit_b)

        return ParseResult(
            success=True,
            dim_a=dim_a_disp,
            dim_b=dim_b_disp,
            internal_a=internal_a,
            internal_b=internal_b,
            original_input=raw_input,
            parsed_units=parsed_units,
            confidence=confidence,
            detected_separator=detected_sep,
            source_type=source_type,
            parse_warnings=warnings,
            error_message=None
        )
