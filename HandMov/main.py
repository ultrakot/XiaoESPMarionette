#connect using SPI
from machine import Pin, SPI
import struct
import time

# Pin definitions
#enable_pin = Pin(32, Pin.OUT)  # Enable pin
cs_pin = Pin(4, Pin.OUT)       # Chip select
cs_pin.value(1)                # Set CS high initially

# SPI setup
spi = SPI(-1, 
          baudrate=100000,
          polarity=1,
          phase=1,
          firstbit=SPI.MSB,
          sck=Pin(19, Pin.OUT),
          mosi=Pin(18, Pin.OUT),
          miso=Pin(20, Pin.IN))

# TMC2130 registers
WRITE_FLAG = 0x80
READ_FLAG = 0x00
REG_GCONF = 0x00
REG_IHOLD_IRUN = 0x10
REG_CHOPCONF = 0x6C
REG_COOLCONF = 0x6D
REG_DRVSTATUS = 0x6F

def pack_data(data, fmt='>L'):
    """Pack data into correct format for SPI communication"""
    return bytearray(struct.pack(fmt, data))

def tmc_write(reg, data):
    """Write data to a TMC2130 register"""
    cs_pin.value(0)  # Select chip
    spi.write(pack_data(reg, 'B'))  # Send register address
    result = spi.write(pack_data(data))  # Send data
    cs_pin.value(1)  # Deselect chip
    return result

def tmc_read(reg):
    """Read data from a TMC2130 register"""
    cs_pin.value(0)
    tmc_write(reg, 0x00)  # Send read request
    spi.write(pack_data(reg))  # Send register address
    data = struct.unpack('>L', spi.read(4, 0x00))[0]  # Read response
    cs_pin.value(1)
    return data

def setup_driver():
    """Initialize TMC2130 with basic settings"""
    # Initialize SPI
    spi.init(baudrate=100000)
    
    # Configure general settings
    # Enable voltage mode (AIN as reference)
    tmc_write(WRITE_FLAG + REG_GCONF, 0x00000001)
    
    # Set current (IHOLD=0x10, IRUN=0x10)
    tmc_write(WRITE_FLAG + REG_IHOLD_IRUN, 0x00001010)
    
    # Configure chopper (256 microsteps, basic settings)
    tmc_write(WRITE_FLAG + REG_CHOPCONF, 0x20008008)

def test_spi_connection():
    """Test SPI connection by reading and writing to registers"""
    print("Testing SPI connection...")
    
    # Test 1: Write and read back from COOLCONF register
    test_value = 0x12345678  # Test pattern
    print(f"Writing test pattern to COOLCONF: 0x{test_value:08X}")
    tmc_write(WRITE_FLAG + REG_COOLCONF, test_value)
    
    # Read back the value
    readback = tmc_read(REG_COOLCONF)
    print(f"Read back from COOLCONF: 0x{readback:08X}")
    
    if readback == test_value:
        print("COOLCONF register write/read test: PASSED")
    else:
        print("COOLCONF register write/read test: FAILED")
    
    # Test 2: Read DRVSTATUS register
    status = tmc_read(REG_DRVSTATUS)
    print(f"\nDRVSTATUS register value: 0x{status:08X}")
    
    # Parse some important status bits
    stallguard = (status >> 24) & 0xFF  # StallGuard2 value
    cs_actual = (status >> 16) & 0x1F   # Current scale actual value
    stealth = (status >> 14) & 1        # StealthChop indicator
    stst = status & 1                   # Standstill indicator
    
    print("\nStatus information:")
    print(f"- StallGuard2 value: {stallguard}")
    print(f"- Current scale: {cs_actual}")
    print(f"- StealthChop: {'active' if stealth else 'inactive'}")
    print(f"- Motor: {'standstill' if stst else 'running'}")
    
    return readback == test_value

def main():
    try:
        # Setup the driver
        setup_driver()
        
        # Test SPI connection
        if test_spi_connection():
            print("\nSPI communication test successful!")
            # Enable the motor
            enable_pin.value(0)
            print("Driver enabled and ready for operation")
        else:
            print("\nSPI communication test failed!")
            raise Exception("SPI communication failure")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()