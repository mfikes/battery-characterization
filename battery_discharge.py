import serial
import time

def command(ser, cmd):
    ser.write(bytes(cmd + "\n", "utf-8"))
    # Give a little time for the command to be executed
    time.sleep(0.010)

def read(ser):
    command(ser, "++read eoi")
    return ser.read(100).decode("utf-8")

def setup_prologix(addr):
    ser = serial.Serial('/dev/cu.usbserial-PXEFMYB9', timeout=1)
    command(ser, "++addr " + str(addr));
    command(ser, "++mode 1")
    command(ser, "++auto 0")
    command(ser, "++eos 3")
    command(ser, "++eoi 1");
    return ser

def setup_instrument(ser):
    command(ser, "*rst")
    command(ser, "*idn?")
    print(read(ser))

def read_voltage(ser):
    command(ser, ":read?")
    s = read(ser)
    vals = s.split(",")
    voltage = float(vals[0])
    return voltage

def calculate_esr(voltage, voc, current):
    return (voc - voltage) / current

def lookup_voc_esr(soc, voc_esr_table):
    index = round((len(voc_esr_table)-1)*(100-soc)/100)
    return voc_esr_table[index]

if __name__ == '__main__':

    # Main parameters
    drain_current = 0.002
    cutoff_voltage = 1.0
    measurement_interval = 10
    recovery_interval = 2
    
    ser = setup_prologix(26)
    setup_instrument(ser)

    # Set high impedance off state so battery can't drive SMU
    command(ser, ":output:smode himp")

    # Source current, measure voltage
    # TODO Do this via commands rather than simulated key presses
    command(ser, ":system:key 19");
    command(ser, ":system:key 15");

    # Initially set to not drain and turn on output
    command(ser, ":source:current 0")
    command(ser, ":output:state on")

    voc_esr_table = []
    
    done = False
    while not(done):
        
        # Drain the battery for the measurement interval
        command(ser, ":source:current -" + str(drain_current))
        time.sleep(measurement_interval)
        voltage = read_voltage(ser)
        
        # Measure open circuit voltage
        command(ser, ":source:current 0")
        time.sleep(recovery_interval);
        voc = read_voltage(ser);

        esr = calculate_esr(voltage, voc, drain_current);

        print("{:.5f} V   {:.5f} V   {:.5f} Ω".format(voc, voltage, esr))
        voc_esr_table.append([voc, esr])
        
        if voltage < cutoff_voltage:
            done = True

    # Now shut off instrument and close comm
    command(ser, ":output:state off")
    ser.close()

    print("Cutoff voltage reached. Dumping battery charge model CSV.\n")
    
    # Print CSV for the battery charge model
    print("SOC,VOC,ESR")
    for soc in range(101):
        [voc, esr] = lookup_voc_esr(soc, voc_esr_table)
        print(str(soc) + "," + str(voc) + "," + str(esr))
