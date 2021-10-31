from prologix import Prologix
from keithley_2400 import Keithley_2400, OutputState, OffState
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

    port = '/dev/cu.usbserial-PXEFMYB9'
    
    smu = Keithley_2400(Prologix(port,True))

    # Set high impedance off state so battery can't drive SMU
    smu.set_off_state(OffState.HIGH_IMPEDANCE)
    
    # Source current, measure voltage
    smu.source_current()
    smu.measure_voltage()

    # Initially set to not drain and turn on output
    smu.set_source_current(0)
    smu.set_output_state(OutputState.ON);
    
    voc_esr_table = []
    
    done = False
    while not(done):
        
        # Drain the battery for the measurement interval
        smu.set_source_current(drain_current)
        time.sleep(measurement_interval)
        voltage = smu.read_voltage()
        
        # Measure open circuit voltage
        smu.set_source_current(0)
        time.sleep(recovery_interval);
        voc = smu.read_voltage();

        esr = calculate_esr(voltage, voc, drain_current);

        print("{:.5f} V   {:.5f} V   {:.5f} Ω".format(voc, voltage, esr))
        voc_esr_table.append([voc, esr])
        
        if voltage < cutoff_voltage:
            done = True

    print("Cutoff voltage reached. Dumping battery charge model CSV.\n")
    
    # Print CSV for the battery charge model
    print("SOC,VOC,ESR")
    for soc in range(101):
        [voc, esr] = lookup_voc_esr(soc, voc_esr_table)
        print(str(soc) + "," + str(voc) + "," + str(esr))
