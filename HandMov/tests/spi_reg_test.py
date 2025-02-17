from machine import Pin, SPI
import time

class TMC2130_Register_Check:
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

    def check_registers(self):
        """Check key registers and print human readable status"""
        print("\nTMC2130 Register Check:")
        print("-----------------------")
        
        # Check GSTAT (General Status)
        gstat = self.read_reg(0x01)
        print("\nGSTAT (0x01):")
        print("Reset:", "Yes" if gstat & 0x01 else "No")
        print("Driver Error:", "Yes" if gstat & 0x02 else "No")
        print("Under Voltage CP:", "Yes" if gstat & 0x04 else "No")
        
        # Check DRV_STATUS
        status = self.read_reg(0x6F)
        print("\nDRV_STATUS (0x6F):")
        print("StallGuard:", "Detected" if status & (1 << 24) else "Not Detected")
        print("Motor Stand Still:", "Yes" if status & (1 << 31) else "No")
        print("Open Load A:", "Yes" if status & (1 << 29) else "No")
        print("Open Load B:", "Yes" if status & (1 << 28) else "No")
        print("Temperature Warning:", "Yes" if status & (1 << 26) else "No")
        print("Temperature Shutdown:", "Yes" if status & (1 << 25) else "No")
        
        # Check CHOPCONF
        chopconf = self.read_reg(0x6C)
        toff = chopconf & 0x0F
        print("\nCHOPCONF (0x6C):")
        print("Driver Enabled:", "Yes" if toff > 0 else "No")
        print("Microsteps:", 256 >> ((chopconf >> 24) & 0x0F))
        print("StealthChop:", "Enabled" if chopconf & (1 << 2) else "Disabled")

def main():
    try:
        tester = TMC2130_Register_Check()
        tester.check_registers()
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == '__main__':
    main()