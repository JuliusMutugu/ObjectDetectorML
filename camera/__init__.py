"""Camera module initialization."""
from .camera_interface import CameraInterface
from .opencv_camera import OpenCVCamera

__all__ = ['CameraInterface', 'OpenCVCamera']
