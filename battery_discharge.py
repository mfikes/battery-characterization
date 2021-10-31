import prologix
import time

def setup_instrument(gpib, addr):
    gpib.command(addr, "*rst")
    print(gpib.query(addr, "*idn?"))

def read_voltage(gpib, addr):
    s = gpib.query(addr, ":read?")
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

    port = '/dev/cu.usbserial-PXEFMYB9'
    addr = 26
    
    gpib = prologix.Prologix(port,True)
    setup_instrument(gpib, addr)
    
    # Set high impedance off state so battery can't drive SMU
    gpib.command(addr, ":output:smode himp")

    # Source current, measure voltage
    # TODO Do this via commands rather than simulated key presses
    gpib.command(addr, ":system:key 19")
    gpib.command(addr, ":system:key 15")

    # Initially set to not drain and turn on output
    gpib.command(addr, ":source:current 0")
    gpib.command(addr, ":output:state on")

    voc_esr_table = []
    
    done = False
    while not(done):
        
        # Drain the battery for the measurement interval
        gpib.command(addr, ":source:current -" + str(drain_current))
        time.sleep(measurement_interval)
        voltage = read_voltage(gpib, addr)
        
        # Measure open circuit voltage
        gpib.command(addr, ":source:current 0")
        time.sleep(recovery_interval);
        voc = read_voltage(gpib, addr);

        esr = calculate_esr(voltage, voc, drain_current);

        print("{:.5f} V   {:.5f} V   {:.5f} Ω".format(voc, voltage, esr))
        voc_esr_table.append([voc, esr])
        
        if voltage < cutoff_voltage:
            done = True

    # Now shut off instrument and close comm
    gpib.command(addr, ":output:state off")

    print("Cutoff voltage reached. Dumping battery charge model CSV.\n")
    
    # Print CSV for the battery charge model
    print("SOC,VOC,ESR")
    for soc in range(101):
        [voc, esr] = lookup_voc_esr(soc, voc_esr_table)
        print(str(soc) + "," + str(voc) + "," + str(esr))
