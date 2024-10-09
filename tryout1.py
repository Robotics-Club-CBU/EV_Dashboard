import RPi.GPIO as GPIO
import time
import spidev  # For the MCP3008

# Pin assignments
BUTTON1_PIN = 8
BUTTON2_PIN = 9
BUTTON3_PIN = 10
BUTTON4_PIN = 11
BUZZER_PIN = 12
POT_PIN = 0  # MCP3008 channel for potentiometer

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON4_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize SPI for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

def read_adc(channel):
    """Read from MCP3008 ADC."""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]

try:
    while True:
        button1_state = GPIO.input(BUTTON1_PIN)
        button2_state = GPIO.input(BUTTON2_PIN)
        button3_state = GPIO.input(BUTTON3_PIN)
        button4_state = GPIO.input(BUTTON4_PIN)
        
        pot_value = read_adc(POT_PIN)
        
        # Print button states
        print(f"Button 1: {'Pressed' if button1_state else 'Not Pressed'}")
        print(f"Button 2: {'Pressed' if button2_state else 'Not Pressed'}")
        print(f"Button 3: {'Pressed' if button3_state else 'Not Pressed'}")
        print(f"Button 4: {'Pressed' if button4_state else 'Not Pressed'}")
        print(f"Potentiometer Value: {pot_value}")

        # Control the buzzer
        if button1_state or button2_state or button3_state or button4_state:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn buzzer on
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn buzzer off
        
        time.sleep(0.5)  # Adjust for readability

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
finally:
    GPIO.cleanup()  # Clean up GPIO on normal exit
