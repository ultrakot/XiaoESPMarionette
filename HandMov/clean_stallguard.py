from machine import Pin, SPI
import time

class TMC2130_StallRecover:
    def __init__(self):
        # Initialize SPI
        self.cs = Pin(17, Pin.OUT)
        self.cs.value(1)  # CS starts high
        
        self.spi = SPI(1,
                      baudrate=4000000,
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=SPI.MSB,
                      sck=Pin(19),
                      mosi=Pin(18),
                      miso=Pin(20))
    
    def write_reg(self, addr, data):
        """Write to a TMC2130 register"""
        self.cs.value(0)
        buf = bytearray([addr | 0x80, (data >> 24) & 0xFF, (data >> 16) & 0xFF,
                        (data >> 8) & 0xFF, data & 0xFF])
        self.spi.write(buf)
        self.cs.value(1)
        time.sleep_ms(1)

    def read_reg(self, addr):
        """Read from a TMC2130 register"""
        self.cs.value(0)
        self.spi.write(bytearray([addr, 0, 0, 0, 0]))
        self.cs.value(1)
        
        time.sleep_ms(1)
        
        self.cs.value(0)
        data = self.spi.read(5)
        self.cs.value(1)
        
        return (data[1] << 24) | (data[2] << 16) | (data[3] << 8) | data[4]
        
    def recover_from_stall(self):
        """Recover stepper from stall condition"""
        print("Recovering from stall...")
        
        # 1. Read GSTAT to clear flags
        gstat = self.read_reg(0x01)
        print("GSTAT:", hex(gstat))
        
        # 2. Clear error flags by reading DRV_STATUS
        status = self.read_reg(0x6F)
        print("DRV_STATUS:", hex(status))
        
        # 3. Re-enable the driver if needed
        # Set CHOPCONF register - enable with basic settings
        self.write_reg(0x6C, 0x00010135)
        
        # 4. Re-initialize stallGuard
        self.setup_highspeed_stall()
        
        print("Recovery complete - motor should be ready to move")

    def setup_highspeed_stall(self):
        """Setup StallGuard for high speed stall detection"""
        self.write_reg(0x14, 0x00000064)  # TCOOLTHRS
        self.write_reg(0x6D, (-10 << 16))  # COOLCONF
        self.write_reg(0x15, 0x00000040)  # THIGH

def main():
    try:
        tester = TMC2130_StallRecover()
        tester.recover_from_stall()
        
        # First, check if motor is stalled
#         status = tester.read_reg(0x6F)
#         print(status)
#         if status & (1 << 24):  # Check StallGuard flag
#             print("Motor is stalled!")
#             tester.recover_from_stall()
#         else:
#             print("Motor is not stalled")
            
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == '__main__':
    main()