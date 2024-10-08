"""Points Module.

#======================================================================#
#                                                                      #
# Module containing the class for defining sets of 3D points.          #
#                                                                      #
#                                                             JAB 2024 #
#======================================================================#
"""

from __future__ import annotations

__all__ = [
    "Points",
]

import numpy as np

from reform.reference_frame import ReferenceFrame


class Points:
    """Class for defining sets of 3D points."""
    
    FRAME_SEP = "_"

    def __init__(
        self,
        points: np.ndarray,
        *,
        name: str = "P",
        frame: ReferenceFrame | None = None,
    ):
        """Constructor.

        Args:
            points (np.ndarray[..., 3]):
                Array of 3D points.
            name (str): Defaults to "P".
                Name of the set of points. Used for printing.
            frame (ReferenceFrame | None): Defaults to None.
                Reference frame of the points. Used for validating
                transformation operations.

        Raises:
            ValueError:
                If points is not a 2D array or if points does not have
                3 dimensions.
        """

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
        """Returns the array of points."""

        return self._points
    
    @property
    def frame(
        self,
    ) -> ReferenceFrame:
        """Returns the reference frame of the points."""

        return self._frame
    
    @property
    def name(
        self,
    ) -> str:
        """Returns the name of the set of points."""

        return self._name
    
    @property
    def fullname(
        self,
    ) -> str:
        """Returns the full name of the set of points.
        
        If the reference frame is defined, it is also included in the
        full name.
        """
        
        if self._frame.name:
            return f"{self._frame.name}{self.FRAME_SEP}{self.name}"
        
        return self.name

    def __str__(
        self,
    ) -> str:
        return f"{self.fullname}: {self.points}"

    def __repr__(self):
        return f"Points {self.fullname}: {self.points}"
