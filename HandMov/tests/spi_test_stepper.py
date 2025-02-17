from machine import Pin, SPI
import time

class TMC2130_StallTest:
    def __init__(self):
        # Initialize SPI on ESP32C6 pins
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
        
        # Motor pins
        self.step_pin = Pin(1, Pin.OUT)
        self.dir_pin = Pin(0, Pin.OUT)
        self.en_pin = Pin(2, Pin.OUT)
        self.en_pin.value(0)  # Enable driver (active low)
        
    def write_reg(self, addr, data):
        """Write to a TMC2130 register"""
        self.cs.value(0)
        buf = bytearray([addr | 0x80, (data >> 24) & 0xFF, (data >> 16) & 0xFF,
                        (data >> 8) & 0xFF, data & 0xFF])
        self.spi.write(buf)
        self.cs.value(1)
        
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

    
    def set_stall_threshold(self, threshold):
        """Set StallGuard threshold"""
        current_conf = self.read_reg(0x6D)  # Read current COOLCONF
        # Clear SGT bits and set new threshold
        new_conf = (current_conf & ~(0x7F << 16)) | ((threshold & 0x7F) << 16)
        self.write_reg(0x6D, new_conf)
        print(f"StallGuard threshold set to: {threshold}")
        
     
    def init_stallguard(self):
        """Initialize StallGuard settings"""
        # Set GCONF
        self.write_reg(0x00, 0x00000000)  # Normal operation
        
        # Set CHOPCONF
        # TOFF=5, HSTRT=4, HEND=1, TBL=2, CHM=0 (spreadCycle)
        self.write_reg(0x6C, 0x00010135)
        
        # Set COOLCONF for StallGuard
        # SEMIN=5, SEMAX=2, SEDN=1, SEUP=3, SGT=1 (more sensitive)
        self.write_reg(0x6D, 0x00091A01)
        
        # Set IHOLD_IRUN
        # IHOLD=8, IRUN=31 (max), IHOLDDELAY=6
        self.write_reg(0x10, 0x00061F08)
        
        # Set TPOWERDOWN
        self.write_reg(0x11, 0x0000000A)
        
        # Set TCOOLTHRS (threshold for enabling coolStep and StallGuard)
        self.write_reg(0x14, 0x00000000)  # Enable StallGuard at all speeds
        
        print("StallGuard initialized")
        
    def test_stallguard(self):
        """Test StallGuard functionality with different thresholds"""
        print("Starting StallGuard test...")
        self.init_stallguard()
        
        # Test different StallGuard thresholds
        thresholds = [16, 8, 4, 2, 1, 0, -1, -2, -4, -8]
        
        for threshold in thresholds:
            print(f"\nTesting with threshold: {threshold}")
            self.set_stall_threshold(threshold)
            time.sleep_ms(100)
            
            # Move motor and check stall
            for _ in range(20):
                self.step_pin.value(1)
                time.sleep_ms(1)
                self.step_pin.value(0)
                time.sleep_ms(1)
                
                # Read DRV_STATUS
                status = self.read_reg(0x6F)
                sg_value = (status >> 24) & 0x3FF
                stalled = (status >> 31) & 0x1
                cs_actual = status & 0x1F
                
                print(f"SG: {sg_value}, CS: {cs_actual}, {'STALLED' if stalled else 'OK'}")
                
                if stalled:
                    print(f"Stall detected at threshold {threshold}")
                    break
                
                time.sleep_ms(50)
            
            time.sleep_ms(500)  # Pause between threshold tests
        
        print("\nTest complete")

def main():
    try:
        tester = TMC2130_StallTest()
        tester.test_stallguard()
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == '__main__':
    main()