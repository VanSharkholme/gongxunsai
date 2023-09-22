from dynamixel_sdk import *
from typing import Optional
import time


# P = 2000 I = 6 D = 2650

class Error(Exception):
    def __init__(self, info):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.info


class Port:
    def __init__(self, device_name):
        self.baud = 1000000
        self.device = device_name
        self.portHandler = PortHandler(self.device)
        self.portHandler.setBaudRate(self.baud)
        self.is_open = False

    def open_port(self) -> bool:
        if self.portHandler.openPort():
            self.is_open = True
            return True
        return False

    def close_port(self) -> None:
        self.portHandler.closePort()
        self.is_open = False


class Parameter:
    def __init__(self,
                 addr: int, size: int, access: str,
                 init_value: Optional[int], data_range: Optional[list],
                 cur_value: int = None):
        self.addr = addr
        self.size = size
        self.access = access
        self.init_value = init_value
        self.range = data_range
        self.cur_value = cur_value

    def set_cur_val(self, val: int) -> None:
        self.cur_value = val


def check_data_range(data: int, d_range: list) -> bool:
    return data in d_range


def data_size_process(data: int, d_size: int) -> list:
    if d_size == 1:
        return [data]
    elif d_size == 2:
        return [DXL_LOBYTE(data), DXL_HIBYTE(data)]
    elif d_size == 4:
        return [DXL_LOBYTE(DXL_LOWORD(data)),
                DXL_HIBYTE(DXL_LOWORD(data)),
                DXL_LOBYTE(DXL_HIWORD(data)),
                DXL_HIBYTE(DXL_HIWORD(data))]


class Motor:
    def __init__(self, motor_id):
        self.type = ''
        self.PROTOCOL_VERSION = 1.0
        self.ID = Parameter(3, 1, 'RW', 1, list(range(0, 254)), motor_id)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

    def send_instruction(self,
                         parameter: Parameter, data: int,
                         port: Port, receive: bool = True) -> tuple[int, int] | int:
        p_handler = port.portHandler
        if check_data_range(data, parameter.range) \
                and port.is_open:
            data_cleaned = data_size_process(data, parameter.size)
            if receive:
                res, error = self.packetHandler.writeTxRx(p_handler, self.ID.cur_value,
                                                          parameter.addr, parameter.size,
                                                          data_cleaned)
                if res != COMM_SUCCESS:
                    raise Error(self.packetHandler.getTxRxResult(res))
                elif error != 0:
                    raise Error(self.packetHandler.getRxPacketError(error))
                return res, error
            else:
                res = self.packetHandler.writeTxOnly(p_handler, self.ID.cur_value,
                                                     parameter.addr, parameter.size,
                                                     data_cleaned)
                if res != COMM_SUCCESS:
                    raise Error(self.packetHandler.getTxRxResult(res))
                return res

        else:
            if not port.is_open:
                raise Error("The Port is not Open!! Action Cancelled!!")
            else:
                raise Error("Data out of Range! Action Cancelled!!")

    def reg_write(self,
                  parameter: Parameter, data: int,
                  port: Port, receive: bool = True) -> tuple[int, int] | int:
        p_handler = port.portHandler
        if check_data_range(data, parameter.range) \
                and port.is_open:
            data_cleaned = data_size_process(data, parameter.size)
            if receive:
                res, error = self.packetHandler.regWriteTxRx(p_handler, self.ID.cur_value,
                                                          parameter.addr, parameter.size,
                                                          data_cleaned)
                if res != COMM_SUCCESS:
                    raise Error(self.packetHandler.getTxRxResult(res))
                elif error != 0:
                    raise Error(self.packetHandler.getRxPacketError(error))
                return res, error
            else:
                res = self.packetHandler.regWriteTxOnly(p_handler, self.ID.cur_value,
                                                     parameter.addr, parameter.size,
                                                     data_cleaned)
                if res != COMM_SUCCESS:
                    raise Error(self.packetHandler.getTxRxResult(res))
                return res

        else:
            if not port.is_open:
                raise Error("The Port is not Open!! Action Cancelled!!")
            else:
                raise Error("Data out of Range! Action Cancelled!!")
    def read_info(self,
                  parameter: Parameter,
                  port: Port) -> tuple[int, int, int]:
        p_handler = port.portHandler
        data, res, error = self.packetHandler.readTxRx(p_handler,
                                                       self.ID.cur_value,
                                                       parameter.addr,
                                                       parameter.size)
        if res != COMM_SUCCESS:
            raise Error(self.packetHandler.getTxRxResult(res))
        elif error != 0:
            raise Error(self.packetHandler.getRxPacketError(error))

        if parameter.size == 2:
            data = DXL_MAKEWORD(data[0], data[1])
        elif parameter.size == 4:
            data = DXL_MAKEDWORD(DXL_MAKEWORD(data[0], data[1]),
                                 DXL_MAKEWORD(data[2], data[3]))

        return data, res, error


class MotorGroup:
    def __init__(self, *args: Motor):
        self.motors = []
        self.IDs = []
        self.p1_motors = []
        self.p2_motors = []
        self.is_same_type = True
        if len(args) == 0:
            raise Error('A Group needs to have at least one Motor!!!')
        for motor in args:
            self.motors.append(motor)
            if motor.ID.cur_value in self.IDs:
                raise Error("Duplicate IDs in the same group!!!")
            else:
                self.IDs.append(motor.ID.cur_value)
            if motor.PROTOCOL_VERSION == 1.0:
                self.p1_motors.append(motor)
            elif motor.PROTOCOL_VERSION == 2.0:
                self.p2_motors.append(motor)
            else:
                continue
        if len(self.p1_motors) * len(self.p2_motors) != 0:
            self.is_same_type = False
        try:
            self.packet_handler_p1 = self.p1_motors[0].packetHandler
        except IndexError:
            pass
        try:
            self.packet_handler_p2 = self.p2_motors[0].packetHandler
        except IndexError:
            pass
        self.default_packet_handler = self.motors[0].packetHandler
    def sync_write(self,
                   parameter: Parameter, data: int, port: Port) -> int:
        if not self.is_same_type:
            raise Error('This function can only be used when all Motors in the Group are the same type!!!')
        if check_data_range(data, parameter.range) \
                and port.is_open:
            port_handler = port.portHandler
            packet_handler = self.default_packet_handler
            addr = parameter.addr
            data_len = parameter.size
            groupSyncWrite = GroupSyncWrite(port_handler, packet_handler, addr, data_len)
            data_cleaned = data_size_process(data, data_len)
            for motor in self.motors:
                groupSyncWrite.addParam(motor.ID.cur_value, data_cleaned)
            comm_res = groupSyncWrite.txPacket()
            if comm_res != COMM_SUCCESS:
                raise Error(packet_handler.getTxRxResult(comm_res))
            groupSyncWrite.clearParam()
        else:
            if not port.is_open:
                raise Error("The Port is not Open!! Action Cancelled!!")
            else:
                raise Error("Data out of Range! Action Cancelled!!")

    def sync_reg_write(self, port: Port, motor_instructs: list, action: bool = True) -> tuple[int, int] | int:
        """
        This function receives an instruction list as parameter, in this list, every
        item should be another list consists of three items in this specific order:
        [ motor, parameter to write, data ].
        """
        for i in range(len(motor_instructs)):
            instruction = motor_instructs[i]
            motor = instruction[0]
            param = instruction[1]
            data = instruction[2]
            if motor not in self.motors:
                raise Error('Motor %d does NOT belong to this group!!!')
            res, error = motor.reg_write(param, data, port)
        if action:
            self.action(port)
        return (res, error)

    def action(self, port: Port):
        port_handler = port.portHandler
        try:
            self.packet_handler_p2.action(port_handler, 254)
        except AttributeError:
            try:
                self.packet_handler_p1.action(port_handler, 254)
            except AttributeError:
                self.default_packet_handler.action(port_handler, 254)




class AX12A(Motor):
    def __init__(self, motor_id):
        super().__init__(motor_id)
        self.PROTOCOL_VERSION = 1.0
        self.type = 'AX12A'
        self.Model_Num = Parameter(0, 2, 'R', 12, None)
        self.Firmware_Version = Parameter(2, 1, 'R', None, None)
        # self.ID = Parameter(3, 1, 'RW', 1, list(range(0, 254)))
        self.Baud = Parameter(4, 1, 'RW', 1, [1, 3, 4, 7, 9, 16, 34, 103, 207])
        self.Return_Delay_Time = Parameter(5, 1, 'RW', 250, list(range(0, 255)))
        self.CW_Angle_Limit = Parameter(6, 2, 'RW', 0, list(range(0, 1024)))
        self.CCW_Angle_Limit = Parameter(8, 2, 'RW', 1023, list(range(0, 1024)))
        self.Temp_Limit = Parameter(11, 1, 'RW', 70, list(range(0, 101)))
        self.Min_Voltage = Parameter(12, 1, 'RW', 60, list(range(50, 161)))
        self.Max_Voltage = Parameter(13, 1, 'RW', 140, list(range(50, 161)))
        self.Max_Torque = Parameter(14, 2, 'RW', 1023, list(range(0, 1024)))
        self.Status_Return_Level = Parameter(16, 1, 'RW', 2, [0, 1, 2])
        self.Alarm_LED = Parameter(17, 1, 'RW', 36, list(range(0, 128)))
        self.Shutdown = Parameter(18, 1, 'RW', 36, list(range(0, 128)))
        self.Torque_Ena = Parameter(24, 1, 'RW', 0, [0, 1])
        self.LED = Parameter(25, 1, 'RW', 0, [0, 1])
        self.CW_Compliance_Margin = Parameter(26, 1, 'RW', 1, list(range(0, 256)))
        self.CCW_Compliance_Margin = Parameter(27, 1, 'RW', 1, list(range(0, 256)))
        self.CW_Compliance_Slope = Parameter(28, 1, 'RW', 32, list(range(0, 255)))
        self.CCW_Compliance_Slope = Parameter(29, 1, 'RW', 32, list(range(0, 255)))
        self.Goal_Position = Parameter(30, 2, 'RW', None, list(range(0, 1024)))
        self.Moving_Speed = Parameter(32, 2, 'RW', None, list(range(0, 2048)))
        self.Torque_Limit = Parameter(34, 2, 'RW', 1023, list(range(0, 1024)))
        self.Present_Position = Parameter(36, 2, 'R', None, None)
        self.Present_Speed = Parameter(38, 2, 'R', None, None)
        self.Present_Load = Parameter(40, 2, 'R', None, None)
        self.Present_Voltage = Parameter(42, 1, 'R', None, None)
        self.Present_Temp = Parameter(43, 1, 'R', None, None)
        self.Instruction_Registered = Parameter(44, 1, 'R', 0, None)
        self.Moving = Parameter(46, 1, 'R', 0, None)
        self.Lock = Parameter(47, 1, 'RW', 0, [0, 1])
        self.Punch = Parameter(48, 2, 'RW', 32, list(range(32, 64)))
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)


class XL330(Motor):
    def __init__(self, motor_id):
        super().__init__(motor_id)
        self.PROTOCOL_VERSION = 2.0
        self.type = 'XL330'
        self.Model_Num = Parameter(0, 2, 'R', 1200, None)
        self.Model_Info = Parameter(2, 4, 'R', None, None)
        self.Firmware_Version = Parameter(6, 1, 'R', None, None)
        # self.ID = Parameter(7, 1, 'RW', 1, list(range(253)), 1)
        self.Baud = Parameter(8, 1, 'RW', 1, list(range(7)))
        self.Return_Delay_Time = Parameter(9, 1, 'RW', 250, list(range(255)))
        self.Drive_Mode = Parameter(10, 1, 'RW', 0, [0, 1, 2, 3, 4, 5])
        self.Operating_Mode = Parameter(11, 1, 'RW', 3, list(range(16)))
        self.Secondary_ID = Parameter(12, 1, 'RW', 255, list(range(253)))
        self.Protocol_Type = Parameter(13, 1, 'RW', 2, [2, 20, 21, 22])
        self.Homing_Offset = Parameter(20, 4, 'RW', 0, list(range(-1044479, 1044480)))
        self.Moving_Threshold = Parameter(24, 4, 'RW', 10, list(range(1024)))
        self.Temp_Limit = Parameter(31, 1, 'RW', 70, list(range(101)))
        self.Min_Voltage = Parameter(32, 2, 'RW', 70, list(range(31, 71)))
        self.Max_Voltage = Parameter(34, 2, 'RW', 35, list(range(31, 71)))
        self.PWM_Limit = Parameter(36, 2, 'RW', 885, list(range(886)))
        self.Current_Limit = Parameter(38, 2, 'Rw', 1750, list(range(1751)))
        self.Velocity_Limit = Parameter(44, 4, 'RW', 445, list(range(2048)))
        self.Max_Position_Limit = Parameter(48, 4, 'RW', 4095, list(range(4096)))
        self.Min_Position_Limit = Parameter(52, 4, 'RW', 0, list(range(4096)))
        self.Startup_Config = Parameter(60, 1, 'RW', 0, [0, 1, 2, 3])
        self.PWM_Slope = Parameter(62, 1, 'RW', 140, list(range(1, 256)))
        self.Shutdown = Parameter(63, 1, 'RW', 53, None)
        self.Torque_Ena = Parameter(64, 1, 'RW', 0, [0, 1])
        self.LED = Parameter(65, 1, 'RW', 0, [0, 1])
        self.Status_Return_Level = Parameter(68, 1, 'RW', 2, [0, 1, 2])
        self.Instruction_Registered = Parameter(69, 1, 'R', 0, [0, 1])
        self.Hardware_Error_Status = Parameter(70, 1, 'R', 0, None)
        self.Velocity_I_Gain = Parameter(76, 2, 'RW', 1600, list(range(16384)))
        self.Velocity_P_Gain = Parameter(78, 2, 'RW', 180, list(range(16384)))
        self.Position_D_Gain = Parameter(80, 2, 'RW', 0, list(range(16384)))
        self.Position_I_Gain = Parameter(82, 2, 'RW', 0, list(range(16384)))
        self.Position_P_Gain = Parameter(84, 2, 'RW', 400, list(range(16384)))
        self.Feedforward_2nd_Gain = Parameter(88, 2, 'RW', 0, list(range(16384)))
        self.Feedforward_1st_Gain = Parameter(90, 2, 'RW', 0, list(range(16384)))
        self.Bus_Watchdog = Parameter(98, 1, 'RW', 0, list(range(1, 128)))
        self.Goal_PWM = Parameter(100, 2, 'RW', None, list(range(-885, 886)))
        self.Goal_Current = Parameter(102, 2, 'RW', None, list(range(-1750, 1751)))
        self.Goal_Velocity = Parameter(104, 4, 'RW', None, list(range(-2047, 2048)))
        self.Profile_Accel = Parameter(108, 4, 'RW', 0, list(range(32767)))
        self.Profile_Velocity = Parameter(112, 4, 'RW', 0, list(range(32767)))
        self.Goal_Position = Parameter(116, 4, 'RW', None, list(range(4096)))
        self.Realtime_Tick = Parameter(120, 2, 'R', None, list(range(32768)))
        self.Moving = Parameter(122, 1, 'R', 0, [0, 1])
        self.Moving_Status = Parameter(123, 1, 'R', 0, list(range(60)))
        self.Present_PWM = Parameter(124, 2, 'R', None, list(range(-885, 886)))
        self.Present_Current = Parameter(126, 2, 'R', None, list(range(-1750, 1751)))
        self.Present_Velocity = Parameter(128, 4, 'R', None, list(range(-2047, 2048)))
        self.Present_Position = Parameter(132, 4, 'R', None, list(range(4096)))
        self.Velocity_Trajectory = Parameter(136, 4, 'R', None, list(range(2048)))
        self.Position_Trajectory = Parameter(140, 4, 'R', None, list(range(4096)))
        self.Present_Input_Voltage = Parameter(144, 2, 'R', None, list(range(31, 71)))
        self.Present_Temp = Parameter(146, 1, 'R', None, list(range(101)))
        self.Backup_Ready = Parameter(147, 1, 'R', None, [0, 1])
        self.Indirect_Address1 = Parameter(168, 2, 'RW', 208, list(range(64, 228)))
        self.Indirect_Address2 = Parameter(170, 2, 'RW', 209, list(range(64, 228)))
        self.Indirect_Address3 = Parameter(172, 2, 'RW', 210, list(range(64, 228)))
        self.Indirect_Address4 = Parameter(174, 2, 'RW', 211, list(range(64, 228)))
        self.Indirect_Address5 = Parameter(176, 2, 'RW', 212, list(range(64, 228)))
        self.Indirect_Address6 = Parameter(178, 2, 'RW', 213, list(range(64, 228)))
        self.Indirect_Address7 = Parameter(180, 2, 'RW', 214, list(range(64, 228)))
        self.Indirect_Address8 = Parameter(182, 2, 'RW', 215, list(range(64, 228)))
        self.Indirect_Address9 = Parameter(184, 2, 'RW', 216, list(range(64, 228)))
        self.Indirect_Address10 = Parameter(186, 2, 'RW', 217, list(range(64, 228)))
        self.Indirect_Address11 = Parameter(188, 2, 'RW', 218, list(range(64, 228)))
        self.Indirect_Address12 = Parameter(190, 2, 'RW', 219, list(range(64, 228)))
        self.Indirect_Address13 = Parameter(192, 2, 'RW', 220, list(range(64, 228)))
        self.Indirect_Address14 = Parameter(194, 2, 'RW', 221, list(range(64, 228)))
        self.Indirect_Address15 = Parameter(196, 2, 'RW', 222, list(range(64, 228)))
        self.Indirect_Address16 = Parameter(198, 2, 'RW', 223, list(range(64, 228)))
        self.Indirect_Address17 = Parameter(200, 2, 'RW', 224, list(range(64, 228)))
        self.Indirect_Address18 = Parameter(202, 2, 'RW', 225, list(range(64, 228)))
        self.Indirect_Address19 = Parameter(204, 2, 'RW', 226, list(range(64, 228)))
        self.Indirect_Address20 = Parameter(206, 2, 'RW', 227, list(range(64, 228)))
        self.Indirect_Data1 = Parameter(208, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data2 = Parameter(209, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data3 = Parameter(210, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data4 = Parameter(211, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data5 = Parameter(212, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data6 = Parameter(213, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data7 = Parameter(214, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data8 = Parameter(215, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data9 = Parameter(216, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data10 = Parameter(217, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data11 = Parameter(218, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data12 = Parameter(219, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data13 = Parameter(220, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data14 = Parameter(221, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data15 = Parameter(222, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data16 = Parameter(223, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data17 = Parameter(224, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data18 = Parameter(225, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data19 = Parameter(226, 1, 'RW', 0, list(range(256)))
        self.Indirect_Data20 = Parameter(227, 1, 'RW', 0, list(range(256)))
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)


if __name__ == '__main__':
    m1 = AX12A(1)
    m2 = AX12A(2)
    m3 = AX12A(3)
    m4 = AX12A(4)
    M1 = XL330(1)
    M2 = XL330(2)
    M3 = XL330(3)
    M4 = XL330(4)
    p = Port('COM3')
    r = p.open_port()
    # group1 = MotorGroup(m1, m2, m3, m4)
    group2 = MotorGroup(M1, M2, M3, M4)
    # group1.sync_write(m1.Torque_Ena, 1, p)
    group2.sync_write(M1.Velocity_Limit, 50, p)
    group2.sync_write(M1.Torque_Ena, 1, p)
    # group1.sync_write(m1.CW_Angle_Limit, 0, p)
    # group1.sync_write(m1.CCW_Angle_Limit, 0, p)
    group2.sync_write(M1.Operating_Mode, 3, p)
    group2.sync_write(M1.Goal_Position, 2048, p)
    input()
    group2.sync_write(M1.Torque_Ena, 0, p)

    # m1.send_instruction(m1.Torque_Ena, 1, p)
    # m2.send_instruction(m2.Torque_Ena, 1, p)
    # for i in range(1024):
    # m1.send_instruction(m1.Goal_Position, 100, p)
    # data, res, error = m1.read_info(m1.Present_Position, p)
    # instructions = [
    #     [m1, m1.Moving_Speed, 1000],
    #     [m2, m2.Moving_Speed, 2024],
    #     [m3, m3.Moving_Speed, 1000],
    #     [m4, m4.Moving_Speed, 2024]
    # ]
    # group1.sync_reg_write(p, instructions)
    # time.sleep(3)
    # group1.action(p)
    # instructions = [
    #     [m1, m1.Moving_Speed, 0],
    #     [m2, m2.Moving_Speed, 0],
    #     [m3, m3.Moving_Speed, 0],
    #     [m4, m4.Moving_Speed, 0],
    # ]
    # group1.sync_reg_write(p, instructions)
    # group1.action(p)
    p.close_port()
    exit()
