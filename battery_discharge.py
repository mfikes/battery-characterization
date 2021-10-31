from prologix import Prologix
from keithley_2400 import Keithley_2400
import discharge_model
import time

def calculate_esr(voltage, voc, current):
    return (voc - voltage) / current

def lookup_voc_esr(soc, voc_esr_table):
    index = round((len(voc_esr_table)-1)*(100-soc)/100)
    return voc_esr_table[index]

def create_discharge_model(voc_esr_table):
    return lambda soc : lookup_voc_esr(soc, voc_esr_table)

if __name__ == '__main__':

    # Main parameters
    drain_current = 0.002
    cutoff_voltage = 1.0
    measurement_interval = 10
    recovery_interval = 2
    discharge_model_filename = 'foo.csv'

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

    print("Writing battery charge model to " + discharge_model_filename)
    
    # Dump the battery charge model
    discharge_model.write(discharge_model_filename, create_discharge_model(voc_esr_table))

