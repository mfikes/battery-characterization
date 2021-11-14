from pymeasure.instruments.keithley import Keithley2400
from pymeasure.adapters import PrologixAdapter
import discharge_model
import time

# ********** Instrument communication **********

# Revise to set smu variable for your particular GPIB / Serial Setup

# Prologix USB to GPIB

adapter = PrologixAdapter('/dev/cu.usbserial-PXEFMYB9')
smu = Keithley2400(adapter.gpib(26))

# USB to RS-232 cable

#smu = Keithley2400('ASRL/dev/cu.usbserial-FTCGVYZA::INSTR',
#                   baud_rate=9600, write_termination='\r', read_termination='\r')

def calculate_esr(voltage, voc, current):
    return (voc - voltage) / current

def lookup_voc_esr(soc, voc_esr_table):
    index = round((len(voc_esr_table)-1)*(100-soc)/100)
    return voc_esr_table[index]

def create_discharge_model(voc_esr_table):
    return lambda soc : lookup_voc_esr(soc, voc_esr_table)

if __name__ == '__main__':

    # Main parameters
    drain_current = 0.0001
    cutoff_voltage = 1.0
    measurement_interval = 5
    settle_time = 0.01
    discharge_model_filename = 'discharge_model.csv'

    # Set high impedance off state so battery can't drive SMU
    smu.output_off_state = 'HIMP'
    smu.use_rear_terminals()

    # Enable 4-wire measurements
    smu.wires = 4

    # Initially set to not drain and turn on output
    smu.source_mode = "current"
    smu.measure_voltage()
    smu.source_current = 0
    smu.source_current_range = 1
    smu.compliance_voltage = 21
    smu.voltage_range = 5
    smu.source_enabled = True
    
    voc_esr_table = []
    
    while True:

        # Measure open circuit voltage
        smu.source_current = 0.0
        time.sleep(settle_time)
        voc = smu.voltage

        # Apply load and measure voltage
        smu.source_current = -drain_current
        time.sleep(settle_time)
        voltage = smu.voltage

        # Calculate ESR and capture results
        esr = calculate_esr(voltage, voc, drain_current)
        voc_esr_table.append([voc, esr])

        # Indicate progress
        print("{:.4f} V   {:.4f} V   {:.4f} Ω".format(voc, voltage, esr))

        # Bookkeeping
        if voltage < cutoff_voltage:
            break
        
        # With load applied, sleep for measurement interval
        time.sleep(measurement_interval)


    print("Writing battery charge model to " + discharge_model_filename)
    
    # Dump the battery charge model
    discharge_model.write(discharge_model_filename, create_discharge_model(voc_esr_table))

