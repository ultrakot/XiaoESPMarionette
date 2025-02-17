from machine import Pin, SPI

class TMC2130_SPI:
    def __init__(self, spi_bus=1, cs_pin=5):
        # Initialize SPI
        self.cs_pin = Pin(cs_pin, Pin.OUT)
        self.spi = SPI(spi_bus,
                      baudrate=4000000,  # 4MHz
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=SPI.MSB,
                      sck=Pin(19),
                      mosi=Pin(18),
                      miso=Pin(20))
        
        self.cs_pin.value(1)  # CS inactive
        self.init_driver()
        
    def init_driver(self):
        """Initialize TMC2130 registers"""
        # Set GCONF register
        self.write_reg(0x00, 0x00000004)  # Enable stealthChop
        
        # Configure COOLCONF for stallGuard
        self.write_reg(0x6D, 0x00010404)  # stallGuard threshold
        
        # Set IHOLD_IRUN
        self.write_reg(0x10, 0x00001F08)  # Run current and hold current
        
    def write_reg(self, addr, data):
        """Write to a TMC2130 register"""
        self.cs_pin.value(0)  # CS active
        buf = bytearray([addr | 0x80, (data >> 24) & 0xFF, (data >> 16) & 0xFF,
                        (data >> 8) & 0xFF, data & 0xFF])
        self.spi.write(buf)
        self.cs_pin.value(1)  # CS inactive
        
    def read_reg(self, addr):
        """Read from a TMC2130 register"""
        self.cs_pin.value(0)  # CS active
        self.spi.write(bytearray([addr, 0, 0, 0, 0]))
        self.cs_pin.value(1)  # CS inactive
        
        self.cs_pin.value(0)
        data = self.spi.read(5)
        self.cs_pin.value(1)
        
        return (data[1] << 24) | (data[2] << 16) | (data[3] << 8) | data[4]
    
    def check_stall(self):
        """Check stallGuard status through SPI"""
        status = self.read_reg(0x41)  # Read DRV_STATUS
        return (status & 0x01000000) != 0  # Check stallGuard indicator bit