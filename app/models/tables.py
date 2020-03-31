from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime


# 1 -- Leedarson
# 2 -- Innotech
# 3 -- Tonly
# 4 -- Changhong
from app.settings import FCODE

# 1. lasy init
db = SQLAlchemy(use_native_unicode='utf8')



# 2. model definition

class RunningState(db.Model):
    __bind_key__ = 'sqlite'
    __tablename__ = 'runningstates'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    key = db.Column(db.String(100))
    value1 = db.Column(db.Boolean)
    value2 = db.Column(db.Integer)
    value3 = db.Column(db.String(100))
    description = db.Column(db.String(100))
    def __init__(self, key, value1=False, value2=-100, value3='', description=''):
        self.key = key
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.description = description
    @staticmethod
    def seed():
        r_running = RunningState('r_running', description='Indicate running or not, default is False.')
        r_devicecode = RunningState('r_devicecode')
        r_totalcount = RunningState('r_totalcount', value2=0) 
        r_progress = RunningState('r_progress', value2=0) 
        r_phase = RunningState('r_phase') 
        r_errno = RunningState('r_errno', value2=0) 
        seeds = [r_running, r_devicecode, r_totalcount, r_progress, r_phase, r_errno]
        db.session.add_all(seeds)
        db.session.commit()

class Systeminfo(db.Model):
    __bind_key__ = 'sqlite'
    __tablename__ = 'systeminfo'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    key = db.Column(db.String(100))
    value1 = db.Column(db.Boolean)
    value2 = db.Column(db.Integer)
    description = db.Column(db.String(100))
    def __init__(self, key, value1=False, value2=-100, description=''):
        self.key = key
        self.value1 = value1
        self.value2 = value2
        self.description = description
    @staticmethod
    def seed():
        s_factorycode = Systeminfo('s_factorycode')
        seeds = [s_factorycode,]
        db.session.add_all(seeds)
        db.session.commit()


class Factory(db.Model):
    __bind_key__ = 'mysql'
    __tablename__ = 'factories'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    Testdata = db.relationship('Testdata', backref='Factory')
    Device = db.relationship('Device', backref='Factory')
    def __init__(self, code, name, description=''):
        self.code = code
        self.name = name
        self.description = description
    @staticmethod
    def seed():
        f1 = Factory(1, 'Leedarson', '立达信')
        f2 = Factory(2, 'Innotech', 'Smart LED Light Bulbs')
        f3 = Factory(3, 'Tonly', '通力')
        f4 = Factory(4, 'Changhong', '长虹')
        f5 = Factory(5, 'Test', 'Test')
        db.session.add_all([f1, f2, f3, f4, f5])
        db.session.commit()


class Device(db.Model):
    __bind_key__ = 'mysql'
    __tablename__ = 'devices'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    code_hex = db.Column(db.String(10), nullable=False, unique=True)
    factory = db.Column(db.Integer, db.ForeignKey('factories.code'), nullable=False) 
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    Testdata = db.relationship('Testdata', backref='Device')
    def __init__(self, code, code_hex, factory, name, description=''):
        self.code = code
        self.code_hex = code_hex
        self.factory = factory
        self.name = name
        self.description = description
    @staticmethod
    def seed():
        d_leedarson_13 = Device(13, '0x0D', 1, 'Gen2 TCO C-Life A19 ST')
        d_leedarson_27 = Device(27, '0x1B', 1, 'Gen2 TCO C-Life A19 MFG')
        d_leedarson_14 = Device(14, '0x0E', 1, 'Gen2 TCO C-Sleep A19 ST')
        d_leedarson_28 = Device(28, '0x1C', 1, 'Gen2 TCO C-Sleep A19 MFG')
        d_leedarson_15 = Device(15, '0x0F', 1, 'Gen2 TCO C-Sleep BR30 ST')
        d_leedarson_29 = Device(29, '0x1D', 1, 'Gen2 TCO C-Sleep BR30 MFG')
        d_leedarson_128 = Device(128, '0x80', 1, 'Dual mode Soft White A19')
        d_leedarson_129 = Device(129, '0x81', 1, 'Dual mode Tunable White A19')
        d_leedarson_130 = Device(130, '0x82', 1, 'Dual mode Tunable White BR30')
        d_leedarson_67 = Device(67, '0x43', 1, 'Out door Plug')

        d_innotech_30 = Device(30, '0x1E', 2, 'Gen2 TCO Full Color A19 ST')
        d_innotech_31 = Device(31, '0x1F', 2, 'Gen2 TCO Full Color A19 MFG')
        d_innotech_32 = Device(32, '0x20', 2, 'Gen2 TCO Full Color BR30 ST')
        d_innotech_33 = Device(33, '0x21', 2, 'Gen2 TCO Full Color BR30 MFG')
        d_innotech_34 = Device(34, '0x22', 2, 'Gen2 TCO Full Color Strip ST')
        d_innotech_35 = Device(35, '0x23', 2, 'Gen2 TCO Full Color Strip MFG')
        d_innotech_131 = Device(131, '0x83', 2, 'Dual mode Full Color A19')
        d_innotech_132 = Device(132, '0x84', 2, 'Dual mode Full Color BR30')
        d_innotech_133 = Device(133, '0x85', 2, 'Dual mode Full Color Strip')
        d_innotech_49 = Device(49, '0x31', 2, 'Motion dimmer switch')
        d_innotech_48 = Device(48, '0x30', 2, 'Dimmer switch')
        d_innotech_61 = Device(61, '0x3D', 2, 'Paddle switch TCO')
        d_innotech_62 = Device(62, '0x3E', 2, 'Toggle switch TCO')
        d_innotech_63 = Device(63, '0x3F', 2, 'Button switch TCO')
        d_innotech_65 = Device(65, '0x41', 2, 'GEN 1 Plug TCO')
    
        d_tonly_55 = Device(55, '0x37', 3, 'Dimmer Switch(0x37)')
        d_tonly_56 = Device(56, '0x38', 3, 'Dimmer Switch(Premium)(0x38)')
        d_tonly_57 = Device(57, '0x39', 3, 'Switch Toggle(0x3A)')
        d_tonly_58 = Device(58, '0x3A', 3, 'Switch Paddle(0x39)')
        d_tonly_59 = Device(59, '0x3B', 3, 'Switch Centre Button(0x3B)')
        d_tonly_81 = Device(81, '0x51', 3, 'Fan Speed Switch')

        d_changhong_66 = Device(66, '0x42', 4, 'Indoor Plug GEN2')

        # todo
        d_test_5 = Device(5, '0x05', 5, 'Test1')
        d_test_6 = Device(6, '0x06', 5, 'Test2')

        devices_all = [
            d_leedarson_13,
            d_leedarson_27,
            d_leedarson_14,
            d_leedarson_28,
            d_leedarson_15,
            d_leedarson_29,
            d_leedarson_128,
            d_leedarson_129,
            d_leedarson_130,
            d_leedarson_67,
            d_innotech_30,
            d_innotech_31,
            d_innotech_32,
            d_innotech_33,
            d_innotech_34,
            d_innotech_35,
            d_innotech_131,
            d_innotech_132,
            d_innotech_133,
            d_innotech_49,
            d_innotech_48,
            d_innotech_61,
            d_innotech_62,
            d_innotech_63,
            d_innotech_65,
            d_tonly_55,
            d_tonly_56,
            d_tonly_57,
            d_tonly_58,
            d_tonly_59,
            d_tonly_81,
            d_changhong_66
        ]

        devices_test = [d_test_5, d_test_6]

        db.session.add_all(devices_all)
        db.session.add_all(devices_test)
        db.session.commit()



class Testdata(db.Model):
    __bind_key__ = 'mysql'
    __tablename__ = 'testdatas'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    device_type = db.Column(db.Integer, db.ForeignKey('devices.code'), nullable=False)
    factory = db.Column(db.Integer, db.ForeignKey('factories.code'), nullable=True, server_default=str(FCODE)) 
    fw_version = db.Column(db.String(20))
    rssi_ble = db.Column(db.Integer)
    rssi_wifi = db.Column(db.Integer)
    mac_ble = db.Column(db.String(18))
    mac_wifi = db.Column(db.String(18))
    is_qualified = db.Column(db.Boolean)
    is_sync = db.Column(db.Boolean)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now())
    status_cmd_check = db.Column(db.Integer, nullable=True)
    def __init__(self, device_type, factory, fw_version, rssi_ble, rssi_wifi, mac_ble, mac_wifi, is_qualified, is_sync, datetime=None):
        self.device_type = device_type
        self.factory = factory
        self.fw_version = fw_version
        self.rssi_ble = rssi_ble
        self.rssi_wifi = rssi_wifi
        self.mac_ble = mac_ble
        self.mac_wifi = mac_wifi
        self.is_qualified = is_qualified
        self.is_sync = is_sync
        self.datetime = datetime
    @staticmethod
    def seed():
        a1 = Testdata(5, 2, '3.1', -65, -33, 'd74d38dabcf1', '88:50:F6:04:62:31', True, False, datetime.datetime.now())
        a2 = Testdata(1, 3, '3.2', -65, -33, 'd74d38dabcf5', '88:50:F6:04:62:35', True, False, datetime.datetime.now())
        a3 = Testdata(17, 1, '3.40', -65, -33, 'd74d38dabcf7', '88:50:F6:04:62:37', False, False, datetime.datetime.now())
        db.session.add_all([a1, a2, a3])
        db.session.commit()


