from __future__ import annotations

__all__ = [
    "Transform",
]

import numpy as np
from scipy.spatial.transform import Rotation

from reform.points import Points
from reform.reference_frame import ReferenceFrame, ReferenceFrameError


class Transform:
    FRAME_FROM_SEP = "_"
    FRAME_TO_SEP = "_"

    def __init__(
        self,
        *,
        position: np.ndarray,
        orientation: Rotation,
        name: str = "T",
        frame_from: ReferenceFrame | None = None,
        frame_to: ReferenceFrame | None = None,
    ):

        if not isinstance(position, np.ndarray):
            position = np.array(position)
        
        if position.shape[-1] != 3:
            raise ValueError("Position must have 3 dimensions")
        
        if not isinstance(orientation, Rotation):
            raise TypeError("Orientation must be a Rotation object")

        if frame_from is None:
            frame_from = ReferenceFrame(None, None)
        
        if frame_to is None:
            frame_to = ReferenceFrame(None, None)
        
        self._position = position
        self._orientation = orientation
        self._orientation_matrix = None
        self._matrix = None
        self._name = name
        self._frame_from = frame_from
        self._frame_to = frame_to

    @classmethod
    def from_matrix(
        cls,
        matrix: np.ndarray,
    ):
        orientation = Rotation.from_matrix(matrix[:3, :3])
        return cls(position=matrix[:3, 3], orientation=orientation)
    
    @classmethod
    def from_pose(
        cls,
        position: np.ndarray,
        orientation: Rotation,
    ):
        return cls(position=position, orientation=orientation)

    @property
    def position(
        self,
    ) -> np.ndarray:
        return self._position
    
    @property
    def orientation(
        self,
    ) -> Rotation:
        return self._orientation

    def _build_matrix(
        self,
    ):
        self._matrix = np.eye(4)
        self._matrix[:3, :3] = self.basis
        self._matrix[:3, 3] = self._position
    
    @property
    def frame_from(
        self,
    ) -> ReferenceFrame:
        return self._frame_from
    
    @property
    def frame_to(
        self,
    ) -> ReferenceFrame:
        return self._frame_to
    
    def _build_orientation_matrix(
        self,
    ):
        self._orientation_matrix = self._orientation.as_matrix()
    
    @property
    def matrix(
        self,
    ) -> np.ndarray:
        if self._matrix is None:
            self._build_matrix()
        
        return self._matrix
    
    @property
    def basis(
        self,
    ) -> np.ndarray:
        if self._orientation_matrix is None:
            self._build_orientation_matrix()
        
        return self._orientation_matrix
    
    @property
    def inv(
        self,
    ) -> 'Transform':
        inv_orientation = self._orientation.inv()
        inv_position = - inv_orientation.apply(self._position)
        return Transform(
            position=inv_position,
            orientation=inv_orientation,
            frame_from=self._frame_to,
            frame_to=self._frame_from,
        )
    
    @property
    def name(
        self,
    ) -> str:
        return self._name
    
    @property
    def fullname(
        self,
    ) -> str:
        rep = self._name
        if self._frame_from:
            rep = f"{rep}{self.FRAME_FROM_SEP}{self._frame_from}"
        
        if self._frame_to.name:
            rep = f"{self._frame_to}{self.FRAME_TO_SEP}{rep}"

        return rep

    def __repr__(
        self,
    ) -> str:
        orientation = self._orientation.as_rotvec()
        return f"Transform {self.fullname}: {self.position}, {orientation}"
    
    def __str__(
            self,
    ) -> str:
        orientation = self._orientation.as_rotvec()
        return f"{self.fullname}: {self.position}, {orientation}"
    
    def _check_point_frame(
        self,
        other: Points,
    ):
        if other.frame == self._frame_from:
            return

        if other.frame == self._frame_to:
            raise ReferenceFrameError(
                f"Reference frames do not match: "
                f"{self.fullname} * {other.fullname}. "
                f"Perhaps you meant to use the inverse transform "
                f"({self.fullname})^-1 * {other.fullname}?"
            )
        
        raise ReferenceFrameError(
            f"Reference frames do not match: "
            f"{self.fullname} * {other.fullname}."
        )
    
    def _check_transform_frames(
        self,
        other: 'Transform',
    ):
        if other.frame_to == self.frame_from:
            return
        
        if other.frame_from == self.frame_from:
            raise ReferenceFrameError(
                f"Reference frames do not match: "
                f"{self.fullname} * {other.fullname}. "
                f"Perhaps you meant to use the inverse transform "
                f"{self.fullname} * ({other.fullname})^-1?"
            )
        
        if other.frame_to == self.frame_to:
            raise ReferenceFrameError(
                f"Reference frames do not match: "
                f"{self.fullname} * {other.fullname}. "
                f"Perhaps you meant to use the inverse transform "
                f"({self.fullname})^-1 * {other.fullname}?"
            )
        
        raise ReferenceFrameError(
            f"Reference frames do not match: "
            f"{self.fullname} * {other.fullname}."
        )
    
    def _check_frames(
        self,
        other: 'Transform' | Points,
    ):
        if isinstance(other, Transform):
            return self._check_transform_frames(other)
        
        if isinstance(other, Points):
            return self._check_point_frame(other)
        
        raise TypeError(f"Unsupported operand type {type(other)}")
    
    def __matmul__(
        self,
        other: 'Transform' | Points,
    ) -> 'Transform':

        self._check_frames(other)

        if isinstance(other, Transform):
            return Transform(
                position=self._orientation.apply(other.position)
                         + self._position,
                orientation=self._orientation * other.orientation,
                name=self.name,
                frame_from=other.frame_from,
                frame_to=self._frame_to,
            )
        
        if isinstance(other, Points):
            return Points(
                points=self._position + self._orientation.apply(other._points),
                name=other.name,
                frame=self._frame_to,
            )
