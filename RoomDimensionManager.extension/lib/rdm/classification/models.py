# -*- coding: utf-8 -*-
"""
Models for the Room Shape Classification Engine.
IronPython 2.7 compatible.
"""
from rdm.models.enums import ShapeType, ReviewReason

class ShapeConfidence(object):
    """Immutable representation of classification confidence."""
    def __init__(self, score, method, is_ambiguous, alternative_candidates=None):
        self.score = score
        self.method = method
        self.is_ambiguous = is_ambiguous
        self.alternative_candidates = alternative_candidates or []

class ClassificationResult(object):
    """The final result of the Room Shape Classification Engine."""
    def __init__(self, shape_type, confidence, requires_review, review_reasons=None, validation_messages=None):
        self.shape_type = shape_type
        self.confidence = confidence
        self.requires_review = requires_review
        self.review_reasons = review_reasons or []
        self.validation_messages = validation_messages or []
    
    @property
    def is_successful(self):
        return self.shape_type not in (ShapeType.UNKNOWN_GEOMETRY, ShapeType.MIXED_GEOMETRY)
