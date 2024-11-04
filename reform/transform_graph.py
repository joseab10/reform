"""Transform Graph Module.

#======================================================================#
#                                                                      #
# Module containing the class for defining graphs of 3D Spatial         #
# Transformations.                                                     #
#                                                                      #
#                                                             JAB 2024 #
#======================================================================#
"""

from __future__ import annotations

from collections import defaultdict, deque

from .transform import Transform
from .reference_frame import ReferenceFrame

__all__ = [
    "TransformGraph",
]


class TransformGraph:
    """Class for defining 3D Spatial Transformations."""

    def __init__(
            self,
            transforms: list[Transform] | None,
    ):
        """Constructor.
        
        Args:
            transforms (list[Transform] | None): Defaults to None.
                List of transforms to build the graph.
        """

        self._frames = defaultdict(dict)
        if transforms is not None:
            self.add_links(transforms)
    
    def add_link(
            self,
            transform: Transform
        ):
        """Add an edge / link to the transform graph.

        In addition to adding the reference frames as nodes to the
        graph, it adds the transform between the two frames as an edge,
        and the inverse transform between the reversed frames.
        
        Args:
            transform (Transform):
                Link to be added to the graph.
        """

        self._frames[transform.frame_from][transform.frame_to] = transform
        self._frames[transform.frame_to][transform.frame_from] = transform.inv
    
    def add_links(
            self,
            transforms: list[Transform]
        ):
        """Add multiple edges / links to the transform graph.

        In addition to adding the reference frames as nodes to the
        graph, it adds the transform between the two frames as an edge,
        and the inverse transform between the reversed frames.
        
        Args:
            transforms (list[Transform]):
                Links to be added to the graph.
        """

        for transform in transforms:
            self.add_link(transform)

    
    def _find_path_bfs(
            self,
            frame_from: ReferenceFrame,
            frame_to: ReferenceFrame,
    ) -> list[ReferenceFrame] | None:
        """Finds a path between two frames with Breadth First Search.
        
        Args:
            frame_from (ReferenceFrame):
                Starting frame to begin the search from.
            frame_to (ReferenceFrame):
                Target frame to find a path to.
        
        Returns:
            path (list[ReferenceFrame] | None):
                List of frames, including the frame_from and frame_to
                if a path exists
        """

        visited = {frame_from: None}
        queue = deque()
        queue.append(frame_from)
        
        while(queue):
            tmp_frame = queue.popleft()
            
            if tmp_frame == frame_to:
                path = []
                while tmp_frame:
                    path.append(tmp_frame)
                    tmp_frame = visited[tmp_frame]
                return path[::-1]
            
            for child_frame in self._frames[tmp_frame]:
                if child_frame not in visited:
                    visited[child_frame] = tmp_frame
                    queue.append(child_frame)

    def _find_path_dfs(
        self,
        frame_from: ReferenceFrame,
        frame_to: ReferenceFrame,
        path: list[ReferenceFrame] | None = None,
    ) -> list[ReferenceFrame] | None:
        """Finds a path between two frames with Depth First Search.
        
        Args:
            frame_from (ReferenceFrame):
                Starting frame to begin the search from.
            frame_to (ReferenceFrame):
                Target frame to find a path to.
        
        Returns:
            path (list[ReferenceFrame] | None):
                List of frames, including the frame_from and frame_to
                if a path exists.
        """

        if path is None:
            path = []
        
        path.append(frame_from)

        if frame_from == frame_to:
            return path
        
        if frame_from not in self._frames:
            return
        
        for frame in self._frames[frame_from]:
            if frame not in path:
                new_path = self.find_path(frame, frame_to, path)
                if new_path:
                    return new_path
    
    def find_path(
            self,
            frame_from: ReferenceFrame,
            frame_to: ReferenceFrame,
            method: str = "bfs"
    ) -> list[ReferenceFrame] | None:
        """Finds a path between two frames.
        
        Args:
            frame_from (ReferenceFrame):
                Starting frame to begin the search from.
            frame_to (ReferenceFrame):
                Target frame to find a path to.
            method (str): Defaults to "bfs".
                Method to use for the graph search.
                Supported: "bfs" and "dfs" for breadth and depth
                first searches respectively
        
        Returns:
            path (list[ReferenceFrame] | None):
                List of frames, including the frame_from and frame_to
                if a path exists.
        """

        if method == "bfs":
            return self._find_path_bfs(frame_from, frame_to)
        
        if method == "dfs":
            return self._find_path_dfs(frame_from, frame_to)
        
        raise ValueError(f"Invalid method {method}.")
    
    def find_transform(
            self,
            frame_from: ReferenceFrame,
            frame_to: ReferenceFrame,
    ) -> Transform | None:
        """Finds the relative transform between two frames.
        
        Args:
            frame_from (ReferenceFrame):
                Starting frame to begin the search from.
            frame_to (ReferenceFrame):
                Target frame to find a transform to.
        
        Returns:
            path (Transform | None):
                Relative transformation between frame_from and frame_to
                if a path exists.
        """
        path = self.find_path(frame_from, frame_to)
        if path is None:
            return
        
        transform = Transform.identity(
            frame_from=frame_from,
            frame_to=frame_from
        )
        for i in range(len(path) - 1):
            transform = transform @ self._frames[path[i + 1]][path[i]]
        
        return transform
