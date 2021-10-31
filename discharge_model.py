import csv

# A dischage model is represented by a function that maps
# SOC (integers in the range 0 to 100) to a [VOC, ESR] tuple.

def write(filename, model):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile);
        writer.writerow(["SOC", "VOC", "ESR"])
        for soc in range(101):
            [voc, esr] = model(soc)
            writer.writerow([soc, voc, esr])
        
