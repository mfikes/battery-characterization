from pymeasure.instruments.keithley import Keithley2400
from pymeasure.instruments.bkprecision import BKPrecision8500
from pymeasure.adapters import PrologixAdapter
import discharge_model
import time

# ********** Instrument communication **********

# Revise to set instrument variable for your particular GPIB / Serial Setup

# Prologix USB to GPIB

# adapter = PrologixAdapter('/dev/cu.usbserial-PXEFMYB9')
# smu = Keithley2400(adapter.gpib(26))

# USB to RS-232 cable

# smu = Keithley2400('ASRL/dev/cu.usbserial-FTCGVYZA::INSTR',
#                   baud_rate=9600, write_termination='\r', read_termination='\r')

smu = None
dc_load = BKPrecision8500('ASRL/dev/cu.usbserial-FTBPC8BS::INSTR')


def calculate_esr(voltage, voc, current):
    return (voc - voltage) / current


def lookup_voc_esr(soc, voc_esr_table):
    index = round((len(voc_esr_table) - 1) * (100 - soc) / 100)
    return voc_esr_table[index]

def create_discharge_model(voc_esr_table):
    return lambda soc: lookup_voc_esr(soc, voc_esr_table)

def setup_instrument():
    if smu is not None:
        smu.output_off_state = 'HIMP'
        smu.use_rear_terminals()
        smu.wires = 4
        smu.source_mode = "current"
        smu.measure_voltage()
        smu.source_current = 0
        smu.source_current_range = 1
        smu.compliance_voltage = 21
        smu.voltage_range = 5
    else:
        a = 1

def set_instrument_enabled(enabled):
    if smu is not None:
        smu.source_enabled = enabled
    else:
        a = 1

def set_drain_current(drain_current):
    if smu is not None:
        smu.source_current = -drain_current;
    else:
        a = 1

def measure_voltage():
    if smu is not None:
        return smu.voltage
    else:
        return 0

if __name__ == '__main__':

    # Main parameters
    drain_current = 0.0001
    cutoff_voltage = 1.0
    measurement_interval = 5
    settle_time = 0.01
    discharge_model_filename = 'discharge_model.csv'

    setup_instrument()
    set_instrument_enabled(True)

    voc_esr_table = []

    while True:

        # Measure open circuit voltage
        set_drain_current(0)
        time.sleep(settle_time)
        voc = measure_voltage()

        # Apply load and measure voltage
        set_drain_current(drain_current)
        time.sleep(settle_time)
        voltage = measure_voltage()

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

    set_instrument_enabled(False)

    print("Writing battery charge model to " + discharge_model_filename)

    # Dump the battery charge model
    discharge_model.write(discharge_model_filename, create_discharge_model(voc_esr_table))
