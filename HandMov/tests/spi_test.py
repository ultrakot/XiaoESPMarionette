from machine import Pin, SPI
import time

def scan_spi():
    print("Scanning SPI on Xiao ESP32C6...")
    
    # Default SPI pins for Xiao ESP32C6
    try:
        # SPI2 pins on ESP32C6
        # SCK = GPIO8
        # MOSI = GPIO9
        # MISO = GPIO10
        spi = SPI(1,
                  baudrate=4000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=Pin(19),
                  mosi=Pin(18),
                  miso=Pin(20))

        return spi
        
    except Exception as e:
        print(f"SPI initialization failed: {e}")
        return None

if __name__ == '__main__':
    spi = scan_spi()
    if spi:
        print("\nSPI is ready to use")
    else:
        print("\nSPI initialization failed")