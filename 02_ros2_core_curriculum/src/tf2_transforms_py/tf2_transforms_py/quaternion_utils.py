"""
Quaternion Mathematics Utility for Spatial Coordinate Transformations.

Provides pure Python Euler (Roll-Pitch-Yaw) to Quaternion conversion using the
ZYX intrinsic sequence standard (REP 103), with zero third-party dependencies.
"""

import math
import sys
from typing import Tuple


def euler_to_quaternion(
    roll: float,
    pitch: float,
    yaw: float
) -> Tuple[float, float, float, float]:
    """
    Convert Tait-Bryan Euler angles (ZYX intrinsic) to unit quaternion.

    :param roll: Rotation around X axis in radians (bank).
    :param pitch: Rotation around Y axis in radians (elevation).
    :param yaw: Rotation around Z axis in radians (heading).
    :return: (qx, qy, qz, qw) normalized quaternion tuple.
    :raises TypeError: If any angle parameter is non-numeric.
    :raises ValueError: If any angle parameter is NaN or Infinite.
    """
    for name, val in [('roll', roll), ('pitch', pitch), ('yaw', yaw)]:
        if not isinstance(val, (int, float)):
            raise TypeError(f'Expected numeric angle for {name}, got {type(val).__name__}')
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f'Angle for {name} cannot be NaN or Infinite, got {val}')

    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    qw = cr * cp * cy + sr * sp * sy

    return (qx, qy, qz, qw)


def run_quaternion_self_tests() -> bool:
    """
    Run self-test suite covering standard rotation cases and edge validations.

    :return: True if all assertion tests pass within 1e-6 tolerance.
    """
    tol = 1e-6
    print('=== Running Quaternion Self-Tests ===')

    # Test 1: Identity Rotation
    q1 = euler_to_quaternion(0.0, 0.0, 0.0)
    assert math.isclose(q1[0], 0.0, abs_tol=tol), f'Identity qx mismatch: {q1}'
    assert math.isclose(q1[1], 0.0, abs_tol=tol), f'Identity qy mismatch: {q1}'
    assert math.isclose(q1[2], 0.0, abs_tol=tol), f'Identity qz mismatch: {q1}'
    assert math.isclose(q1[3], 1.0, abs_tol=tol), f'Identity qw mismatch: {q1}'
    print('  [PASS] Test 1: Identity Rotation (0, 0, 0) -> (0, 0, 0, 1)')

    # Test 2: Planar +90 deg Yaw
    sqrt2_2 = math.sqrt(2.0) / 2.0
    q2 = euler_to_quaternion(0.0, 0.0, math.pi / 2.0)
    assert math.isclose(q2[0], 0.0, abs_tol=tol), f'+90deg Yaw qx mismatch: {q2}'
    assert math.isclose(q2[1], 0.0, abs_tol=tol), f'+90deg Yaw qy mismatch: {q2}'
    assert math.isclose(q2[2], sqrt2_2, abs_tol=tol), f'+90deg Yaw qz mismatch: {q2}'
    assert math.isclose(q2[3], sqrt2_2, abs_tol=tol), f'+90deg Yaw qw mismatch: {q2}'
    print('  [PASS] Test 2: Planar +90 deg Yaw (0, 0, pi/2) -> (0, 0, sqrt(2)/2, sqrt(2)/2)')

    # Test 3: Planar -90 deg Yaw
    q3 = euler_to_quaternion(0.0, 0.0, -math.pi / 2.0)
    assert math.isclose(q3[0], 0.0, abs_tol=tol), f'-90deg Yaw qx mismatch: {q3}'
    assert math.isclose(q3[1], 0.0, abs_tol=tol), f'-90deg Yaw qy mismatch: {q3}'
    assert math.isclose(q3[2], -sqrt2_2, abs_tol=tol), f'-90deg Yaw qz mismatch: {q3}'
    assert math.isclose(q3[3], sqrt2_2, abs_tol=tol), f'-90deg Yaw qw mismatch: {q3}'
    print('  [PASS] Test 3: Planar -90 deg Yaw (0, 0, -pi/2) -> (0, 0, -sqrt(2)/2, sqrt(2)/2)')

    # Test 4: Planar 180 deg Yaw
    q4 = euler_to_quaternion(0.0, 0.0, math.pi)
    assert math.isclose(q4[0], 0.0, abs_tol=tol), f'180deg Yaw qx mismatch: {q4}'
    assert math.isclose(q4[1], 0.0, abs_tol=tol), f'180deg Yaw qy mismatch: {q4}'
    assert math.isclose(q4[2], 1.0, abs_tol=tol), f'180deg Yaw qz mismatch: {q4}'
    assert math.isclose(q4[3], 0.0, abs_tol=tol), f'180deg Yaw qw mismatch: {q4}'
    print('  [PASS] Test 4: Planar 180 deg Yaw (0, 0, pi) -> (0, 0, 1, 0)')

    # Test 5: Arbitrary 3D Rotation Unit Length (Norm == 1.0)
    q5 = euler_to_quaternion(0.35, -0.22, 1.45)
    norm5 = math.sqrt(sum(k * k for k in q5))
    assert math.isclose(norm5, 1.0, abs_tol=tol), f'Unit norm failed: {norm5}'
    print(f'  [PASS] Test 5: Unit Norm Preservation: norm = {norm5:.7f}')

    # Test 6: Defensive Input Validation (TypeError and ValueError)
    type_err_caught = False
    try:
        euler_to_quaternion('invalid', 0.0, 0.0)  # type: ignore
    except TypeError:
        type_err_caught = True
    assert type_err_caught, 'Failed to raise TypeError for string angle'

    val_err_caught = False
    try:
        euler_to_quaternion(float('nan'), 0.0, 0.0)
    except ValueError:
        val_err_caught = True
    assert val_err_caught, 'Failed to raise ValueError for NaN angle'

    print('  [PASS] Test 6: Defensive validation on invalid/NaN types')
    print('=== All 6 Quaternion Self-Tests Succeeded! ===\n')
    return True


if __name__ == '__main__':
    success = run_quaternion_self_tests()
    sys.exit(0 if success else 1)
