"""Transform Module.

#======================================================================#
#                                                                      #
# Module containing the class for defining 3D Spatial Transformations.  #
#                                                                      #
#                                                             JAB 2024 #
#======================================================================#
"""

from __future__ import annotations

__all__ = [
    "Transform",
]

import numpy as np
from scipy.spatial.transform import Rotation

from reform.points import Points
from reform.reference_frame import ReferenceFrame, ReferenceFrameError


class Transform:
    """Class for defining 3D Spatial Transformations."""

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
        """Constructor.

        Args:
            position (np.ndarray[3]):
                Position of the transformation.
            orientation (Rotation):
                Orientation of the transformation.
            name (str): Defaults to "T".
                Name of the transformation. Used for printing.
            frame_from (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation origin.
            frame_to (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation target.
        
        Raises:
            ValueError:
                If position does not have 3 dimensions.
            TypeError:
                If orientation is not a Rotation object.
        """

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
    def identity(
        cls,
        *,
        name: str = "T",
        frame_from: ReferenceFrame | None = None,
        frame_to: ReferenceFrame | None = None,
    ) -> Transform:
        """Creates an identity transformation.

        Args:
            name (str): Defaults to "T".
                Name of the transformation. Used for printing.
            frame_from (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation origin.
            frame_to (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation target.

        Returns:
            Transform:
                Identity transformation.
        """

        return cls(
            position=np.zeros(3),
            orientation=Rotation.identity(),
            name=name,
            frame_from=frame_from,
            frame_to=frame_to,
        )

    @classmethod
    def from_matrix(
        cls,
        matrix: np.ndarray,
        *,
        name: str = "T",
        frame_from: ReferenceFrame | None = None,
        frame_to: ReferenceFrame | None = None,
    ) -> Transform:
        """Creates a Transform object from a 3x3, 3x4 or 4x4 matrix.

        Args:
            matrix (np.ndarray):
                Transformation matrix.
            name (str): Defaults to "T".
                Name of the transformation. Used for printing.
            frame_from (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation origin.
            frame_to (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation target.

        Returns:
            Transform:
                Transform object created from the matrix.
        """

        orientation = Rotation.from_matrix(matrix[:3, :3])
        return cls(
            position=matrix[:3, 3],
            orientation=orientation,
            name=name,
            frame_from=frame_from,
            frame_to=frame_to,
        )
    
    @classmethod
    def from_pose(
        cls,
        position: np.ndarray,
        orientation: Rotation,
        *,
        name: str = "T",
        frame_from: ReferenceFrame | None = None,
        frame_to: ReferenceFrame | None = None,
    ):
        """Creates a Transform object from a 3x3, 3x4 or 4x4 matrix.

        Args:
            position (np.ndarray[3]):
                Position of the transformation.
            orientation (Rotation):
                Orientation of the transformation.
            name (str): Defaults to "T".
                Name of the transformation. Used for printing.
            frame_from (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation origin.
            frame_to (ReferenceFrame | None): Defaults to None.
                Reference frame of the transformation target.

        Returns:
            Transform:
                Transform object created from the position and orientation.
        """

        return cls(
            position=position,
            orientation=orientation,
            name=name,
            frame_from=frame_from,
            frame_to=frame_to,
        )
    
    @classmethod
    def from_se3(
            cls,
            qwxyz_txyz: np.ndarray,
            *,
            name: str = "T",
            frame_from: ReferenceFrame | None = None,
            frame_to: ReferenceFrame | None = None,
    ):
        """Creates a Transform object from a 7-element array.

        Args:
            txyz_qwxyz (np.ndarray[7]):
                Array containing the position and orientation of the transform.
            degrees (bool): Defaults to False.
                If True, the orientation is in degrees.

        Returns:
            Transform:
                Transform object created from the position and orientation.
        """

        position = qwxyz_txyz[..., 4:]
        quat = qwxyz_txyz[..., :4]
        quat = quat[..., [1, 2, 3, 0]]
        orientation = Rotation.from_quat(quat)
        
        return cls(
            position=position,
            orientation=orientation,
            name=name,
            frame_from=frame_from,
            frame_to=frame_to,
        )
    
    def as_se3(
        self,
    ) -> np.ndarray:
        """Returns the transformation as a 7-element array.

        Returns:
            np.ndarray[7]:
                Array containing the position and orientation of the transform.
        """
        rot_quat = self.orientation.as_quat()
        rot_quat = rot_quat[..., [1, 2, 3, 0]]
        tra = self.position

        return np.concatenate([rot_quat, tra])
        

    @property
    def position(
        self,
    ) -> np.ndarray:
        """Returns the position of the transformation."""

        return self._position
    
    @property
    def orientation(
        self,
    ) -> Rotation:
        """Returns the orientation of the transformation."""

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
        """Returns the origin reference frame of the transformation."""

        return self._frame_from
    
    @frame_from.setter
    def frame_from(
        self,
        frame: ReferenceFrame,
    ):
        """Sets the origin reference frame of the transformation."""

        if not isinstance(frame, ReferenceFrame):
            raise TypeError("frame_from must be a ReferenceFrame object")
        
        self._frame_from = frame
    
    @property
    def frame_to(
        self,
    ) -> ReferenceFrame:
        """Returns the target reference frame of the transformation."""

        return self._frame_to
    
    @frame_to.setter
    def frame_to(
        self,
        frame: ReferenceFrame,
    ):
        """Sets the target reference frame of the transformation."""

        if not isinstance(frame, ReferenceFrame):
            raise TypeError("frame_to must be a ReferenceFrame object")
        
        self._frame_to = frame
    
    def _build_orientation_matrix(
        self,
    ):
        self._orientation_matrix = self._orientation.as_matrix()
    
    @property
    def matrix(
        self,
    ) -> np.ndarray:
        """Returns the transformation matrix."""

        if self._matrix is None:
            self._build_matrix()
        
        return self._matrix
    
    @property
    def basis(
        self,
    ) -> np.ndarray:
        """Returns the orientation of the transformation as a matrix."""
        if self._orientation_matrix is None:
            self._build_orientation_matrix()
        
        return self._orientation_matrix
    
    @property
    def inv(
        self,
    ) -> 'Transform':
        """Returns the inverse of the transformation."""

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
        """Returns the name of the transformation."""

        return self._name
    
    @property
    def fullname(
        self,
    ) -> str:
        """Returns the full name of the transformation.

        If the reference frames are defined, they are also included in the
        full name.
        """
        
        rep = self._name
        if self._frame_from:
            rep = f"{rep}{self.FRAME_FROM_SEP}{self._frame_from.shortframe}"
        
        if self._frame_to.name:
            rep = f"{self._frame_to.shortframe}{self.FRAME_TO_SEP}{rep}"

        return rep

    def __repr__(
        self,
    ) -> str:
        orientation = self._orientation.as_rotvec()
        return f"TF({self.fullname}: {self.position}, {orientation})"
    
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
