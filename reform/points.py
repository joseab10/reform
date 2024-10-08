from __future__ import annotations

__all__ = [
    "Points",
]

import numpy as np

from reform.reference_frame import ReferenceFrame


class Points:
    
    FRAME_SEP = "_"

    def __init__(
        self,
        points: np.ndarray,
        *,
        name: str = "P",
        frame: ReferenceFrame | None = None,
    ):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        
        if points.ndim != 2:
            raise ValueError("Points must be a 2D array")
        
        if points.shape[-1] != 3:
            raise ValueError("Points must have 3 dimensions")
        
        if frame is None:
            frame = ReferenceFrame(None, None)
        
        self._points = points
        self._frame = frame
        self._name = name
    
    @property
    def points(
        self,
    ) -> np.ndarray:
        return self._points
    
    @property
    def frame(
        self,
    ) -> ReferenceFrame:
        return self._frame
    
    @property
    def name(
        self,
    ) -> str:
        return self._name
    
    @property
    def fullname(
        self,
    ) -> str:
        if self._frame.name:
            return f"{self._frame.name}{self.FRAME_SEP}{self.name}"
        
        return self.name

    def __str__(
        self,
    ) -> str:
        return f"{self.fullname}: {self.points}"

    def __repr__(self):
        return f"Points {self.fullname}: {self.points}"
