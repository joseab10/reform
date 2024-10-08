"""Reference Frame Module.

#======================================================================#
#                                                                      #
# Module containing the class for defining reference frames.           #
#                                                                      #
#                                                             JAB 2024 #
#======================================================================#
"""

from __future__ import annotations

__all__ = [
    "ReferenceFrame",
    "ReferenceFrameError",
]

from typing import Any


class ReferenceFrameError(RuntimeError):
    """Exception used for mismatched reference frames."""


class ReferenceFrame:
    """Class for defining reference frames."""
    
    FRAME_SEP = ", "

    def __init__(
        self,
        frame: str | None,
        time: Any | None = None
    ):
        """Constructor.

        Args:
            frame (str | None):
                Spatial name of the frame.
            time (Any | None): Defaults to None.
                Temporal stamp of the frame.
        """

        self._frame = frame
        self._time = time
    
    @property
    def frame(
        self,
    ) -> str:
        """Returns the spatial name of the frame."""

        return self._frame
    
    @property
    def time(
        self,
    ) -> Any | None:
        """Returns the temporal stamp of the frame."""

        return self._time
    
    def __eq__(
        self,
        other: 'ReferenceFrame',
    ) -> bool:
        return self._frame == other.frame and self._time == other.time
    
    @property
    def name(
        self,
    ) -> str:
        """Returns the name of the reference frame."""
        
        frame = self._frame if self._frame is not None else ""
        time = self._time if self._time is not None else ""
        printable = frame or time
        sep = self.FRAME_SEP if frame and time else ""
        rep = f"({frame}{sep}{time})" if printable else ""
        return rep

    def __str__(
        self,
    ) -> str:
        return self.name
    
    def __repr__(
        self,
    ) -> str:
        return f"ReferenceFrame({self.name})"
