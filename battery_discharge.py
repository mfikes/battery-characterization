from prologix import Prologix
from keithley_2400 import Keithley_2400
import time

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
    load_interval = 0.1

    port = '/dev/cu.usbserial-PXEFMYB9'
    
    smu = Keithley_2400(Prologix(port,True))

    # Set high impedance off state so battery can't drive SMU
    smu.set_off_state_high_impedance()
    
    # Source current, measure voltage
    smu.source_current()
    smu.measure_voltage()

    # Initially set to not drain and turn on output
    smu.set_source_current(0)
    smu.output_on()
    
    voc_esr_table = []
    
    while True:

        # Measure open circuit voltage
        smu.set_source_current(0)
        time.sleep(recovery_interval);
        voc = smu.read_voltage();

        # Apply load and measure voltage
        smu.set_source_current(-drain_current)
        time.sleep(load_interval)
        voltage = smu.read_voltage()

        # Calculate ESR and capture results
        esr = calculate_esr(voltage, voc, drain_current);
        voc_esr_table.append([voc, esr])

        # Indicate progress
        print("{:.5f} V   {:.5f} V   {:.5f} Ω".format(voc, voltage, esr))

        # Bookkeeping
        if voltage < cutoff_voltage:
            break
        
        # With load applied, sleep for measurement interval
        time.sleep(measurement_interval)


    print("Cutoff voltage reached. Dumping battery charge model CSV.\n")
    
    # Print CSV for the battery charge model
    print("SOC,VOC,ESR")
    for soc in range(101):
        [voc, esr] = lookup_voc_esr(soc, voc_esr_table)
        print(str(soc) + "," + str(voc) + "," + str(esr))
