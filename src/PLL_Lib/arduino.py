import serial
import serial.tools.list_ports
import PLL_Lib.arduinoerrorhelp as er
import time
from importlib.metadata import version
version = version('PLL_Lib')

MAX_INT = 2147483647  # 2^31 - 1
MIN_INT = -2147483647


class Arduino:

    def _check_with(f):
        def wrapper(self, *args, **kwargs):
            if not self._used_in_with:
                raise er.WrongContextException()
            return f(self, *args, **kwargs)

        return wrapper

    def __init__(self, port=None):
        '''
        Create a wrapper for the serial interface to an arduino.
        :param port: (Optional) The name of the serial port the arduino is connected to, eg 'COM5'.
        Otherwise the program will attempt to find this automatically.
        '''
        self.port = port
        self._used_in_with = False

    def __enter__(self):
        self._used_in_with = True
        if self.port is not None:
            try:
                self.arduino = serial.Serial(port=self.port, baudrate=9600)#, timeout=.1)
            except Exception as e:
                if "PermissionError" in e.args[0]:
                    raise er.PortInUseException(self.port)
                if "FileNotFound" in e.args[0]:
                    raise er.WrongPortException(self.port)
                else:
                    raise er.UnexpectedConnectionException(self.port)
        else:
            # Find port automatically
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if 'arduino' in p.description.lower() or 'serial' in p.description.lower():
                    self.port = p.device
                    try:
                        self.arduino = serial.Serial(port=self.port, baudrate=9600)#, timeout=.1)
                        break
                    except Exception as e:
                        if "PermissionError" in e.args[0]:
                            raise er.PortInUseException(self.port)
                        else:
                            raise er.UnexpectedConnectionException(self.port)
            else:
                raise er.CouldNotFindArduinoException()
        print(f'PLL_Lib version {version}: Connecting to Arduino on port {self.port}.')
        time.sleep(3)
        print('Connected to Arduino!')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.arduino.flush()
        self.arduino.close()

    @_check_with
    def send_code(self, code: int):
        '''
        Send a numeric code to the arduino.
        :param code: An integer between -2147483647 and 2147483647 inclusive.
        '''
        if type(code) is not int or not (MIN_INT <= code <= MAX_INT):
            raise er.InvalidCodeException(code, MIN_INT, MAX_INT)
        #print('sending', code)
        self.arduino.write(bytes(str(code)+'\n', 'utf-8'))
    
    # @_check_with
    # def wait_for_code(self, code: int = None, timeout = None) -> int | None:
    #     '''
    #     Wait for the arduino to send a numeric code
    #     :param code: the code to wait for.
    #     :param timeout: the timeout in seconds. If none specified, will wait forever
    #     If no code is specified, will wait for any code, and return the code received
    #     '''
    #     #parameter validation
    #     if code is not None:
    #         if type(code) is not int or not (MIN_INT <= code <= MAX_INT):
    #             raise er.InvalidCodeException(code, MIN_INT, MAX_INT)

    #     #wait loop
    #     if timeout is None:
    #         has_not_timed_out = lambda: True
    #     else:
    #         start_time = time.time()
    #         has_not_timed_out = lambda: time.time() < start_time + timeout
    #     while has_not_timed_out():
    #         #loop will hog the processor...
    #         #is there an easy way around this without compromising response time?
            

    #     if code is None:
    #         error_description = f"arduino did not send a code within {timeout} seconds"
    #     else:
    #         error_description = f"arduino did not send code {code} within {timeout} seconds"
    #     raise TimeoutError(error_description)
