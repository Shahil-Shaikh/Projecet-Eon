import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arducam_rclpy_tof_pointcloud import tof_pointcloud


def test_parse_cli_args_ignores_ros2_arguments():
    args = ["--cfg", "/tmp/cfg.yaml", "--ros-args", "--log-level", "info"]

    parsed = tof_pointcloud.parse_cli_args(args)

    assert parsed.cfg == "/tmp/cfg.yaml"
