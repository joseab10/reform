"""Reference Frame Module.

#======================================================================#
#                                                                      #
# Module containing the class for defining reference frames.            #
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
        frame: str,
        time: Any | None = None,
        *,
        shortframe: str | None = None,
    ):
        """Constructor.

        Args:
            frame (str):
                Spatial name of the frame.
            time (Any | None): Defaults to None.
                Temporal stamp of the frame.
            shortframe (str | None): Defaults to None.
                Short name for the spatial name of the frame for representation.
                If None, then the first letter of the frame is used.
        """

        self._frame = frame
        self._shortframe = shortframe if shortframe is not None else (
            frame[0] if frame is not None else None)
        self._time = time
    
    @property
    def frame(
        self,
    ) -> str:
        """Returns the spatial name of the frame."""

        return self._frame

    @property
    def shortframe(
        self
    ) -> str:
        """Returns the short spatial name of the frame."""

        return self._shortframe
    
    @property
    def time(
        self,
    ) -> Any | None:
        """Returns the temporal stamp of the frame."""

        return self._time
    
    @property
    def name(
        self,
    ) -> str:
        """Returns the name of the reference frame."""
        
        frame = self._shortframe if self._shortframe is not None else ""
        time = self._time if self._time is not None else ""
        printable = frame or time
        sep = self.FRAME_SEP if frame and time else ""
        rep = f"({frame}{sep}{time})" if printable else ""
        return rep
    
    def __eq__(
        self,
        other: 'ReferenceFrame',
    ) -> bool:
        return self._frame == other.frame and self._time == other.time
    
    def __str__(
        self,
    ) -> str:
        return self.name
    
    def __repr__(
        self,
    ) -> str:
        return f"RF{self.name}"
    
    def __hash__(
        self,
    ) -> int:
        return hash((self._frame, self._time))
