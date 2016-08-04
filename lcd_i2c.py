#!/usr/bin/python
import smbus
import time

# Define some device parameters
EE_ADDR = 0x50
LCD_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(LCD_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(LCD_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(LCD_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(LCD_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
def main():
  # Main program block

  # Initialise display
  lcd_init()
  lcd_string("Save information",LCD_LINE_1)
  lcd_string("to EEprom by I2C",LCD_LINE_2)
  time.sleep(1)
  info1_1 = [0x44,0x45,0x4c,0x4c,0x20,0x49,0x6E,0x74]
  info1_2 = [0x65,0x72,0x6e,0x20,0x20,0x20,0x20,0x20]
  info2_1 = [0x4D,0x61,0x6E,0x61,0x67,0x65,0x72,0x3a]
  info2_2 = [0x4B,0x61,0x72,0x65,0x6E,0x20,0x20,0x20]
  bus.write_i2c_block_data(EE_ADDR,0x00,info1_1)
  time.sleep(0.002)
  bus.write_i2c_block_data(EE_ADDR,0x00+8,info1_2)
  time.sleep(0.002)
  bus.write_i2c_block_data(EE_ADDR,0x00+16,info2_1)
  time.sleep(0.002)
  bus.write_i2c_block_data(EE_ADDR,0x00+24,info2_2)

  
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(1)
  
  lcd_string("Read information",LCD_LINE_1)
  lcd_string("from it by I2C",LCD_LINE_2)
  
  time.sleep(1)
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  first_line=bus.read_i2c_block_data(EE_ADDR,0x00,16)
  second_line=bus.read_i2c_block_data(EE_ADDR,0x10,16)
  print [str(unichr(x)) for x in first_line]
  print [str(unichr(x)) for x in second_line]
  
  lcd_string("The info. is... ",LCD_LINE_1)
  time.sleep(1)
  lcd_byte(LCD_LINE_1, LCD_CMD)
  for x in range(LCD_WIDTH):
    lcd_byte(first_line[x],LCD_CHR)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  for x in range(LCD_WIDTH):
    lcd_byte(second_line[x],LCD_CHR)
  
  time.sleep(5)
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)

