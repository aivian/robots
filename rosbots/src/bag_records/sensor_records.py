import pdb

import numpy

import bag_records.records
import bag_records.geometry_records
import bag_records.std_records

import copy

class BatteryState(bag_records.records.RecordBase):
    """Record for sensor_msgs/BatteryState types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(BatteryState, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'voltage': [],
            'current': [],
            'charge': [],
            'capacity': [],
            'design_capacity': [],
            'percentage': [],
            'power_supply_status': [],
            'power_supply_health': [],
            'power_supply_technology': [],
            'present': [],
            'cell_voltage': [],
            'location': [],
            'serial_number': [],
            }

class FluidPressure(bag_records.records.RecordBase):
    """Record for sensor_msgs/FluidPressure types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(FluidPressure, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'fluid_pressure': [],
            'variance': [],
            }

class Imu(bag_records.records.RecordBase):
    """Record for sensor_msgs/Imu types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(Imu, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'orientation':
                bag_records.geometry_records.Quaternion(has_msg_time=True),
            'orientation_covariance': [],
            'angular_velocity':
                bag_records.geometry_records.Vector3(has_msg_time=True),
            'angular_velocity_covariance': [],
            'linear_acceleration':
                bag_records.geometry_records.Vector3(has_msg_time=True),
            'linear_acceleration_covariance': [],
            }

class Joy(bag_records.records.RecordBase):
    """Record for sensor_msgs/Joy types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(Joy, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'axes': [],
            'buttons': [],
            }

class MagneticField(bag_records.records.RecordBase):
    """Record for sensor_msgs/MagneticField types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(MagneticField, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'magnetic_field':
                bag_records.geometry_records.Vector3(has_msg_time=True),
            'magnetic_field_covariance': [],
            }

class NavSatFix(bag_records.records.RecordBase):
    """Record for sensor_msgs/NavSatFix types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(NavSatFix, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'status': NavSatStatus(),
            'latitude': [],
            'longitude': [],
            'altitude': [],
            'position_covariance': [],
            'position_covariance_type': []
            }

class NavSatStatus(bag_records.records.RecordBase):
    """Record for sensor_msgs/NavSatStatus types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(NavSatStatus, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'status': [],
            'service': [],
            }

class RelativeHumidity(bag_records.records.RecordBase):
    """Record for sensor_msgs/RelativeHumidity types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(RelativeHumidity, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'relative_humidity': [],
            'variance': [],
            }

class Temperature(bag_records.records.RecordBase):
    """Record for sensor_msgs/Temperature types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(Temperature, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'temperature': [],
            'variance': [],
            }

class TimeReference(bag_records.records.RecordBase):
    """Record for sensor_msgs/TimeReference types
    """
    def __init__(self, has_msg_time=True):
        """Constructor

        Arguments:
            has_msg_time: defaults true, indicates if message has time

        Returns:
            class instance
        """
        super(TimeReference, self).__init__(has_msg_time)
        self._fields = {
            'bag_time': [],
            'msg_time': [],
            'time_ref': [],
            'source': [],
            }

