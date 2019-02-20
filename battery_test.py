import sys, time, csv, signal, dcload
err = sys.stderr.write
testIsRunning = True

def updateSettings(cmd, results):
    if results:
        print cmd, "failed:"
        print "  ", results
        exit(1)
    else:
        print cmd

def formatDataRow(data):
    return [time.asctime(), data['voltage'], data['current'], data['power']]

def writeData(row, csv_file):
    print row
    csv_file.writerow(row)

def stopTest(signal, frame):
    global testIsRunning
    print "Stopping the test prematurely"
    testIsRunning = False

def runBatteryTest(load, resistance):
    global testIsRunning

    print "Starting a constant-resistance test"
    updateSettings("Set to remote control", load.SetRemoteControl())

    # Configure test settings
    updateSettings("Set to constant resistance mode", load.SetMode('cr'))
    updateSettings("Set CR resistance", load.SetCRResistance(resistance))
    print "Function is = ", load.GetFunction()
    print "Mode is = ", load.GetMode()
    print "Resistance is = ", load.GetCRResistance()

    teststarttime = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = 'battery_test_' + teststarttime + '.csv'
    with open(filename, 'wb') as csvfile:
        csv_w = csv.writer(csvfile, delimiter=',')
        headers = ['time','voltage','current','power']
        writeData(headers, csv_w)

        # Get and write out the initial readings
        data = load.GetInputValues()
        writeData(formatDataRow(data), csv_w)

        # Start the actual test
        load.TurnLoadOn()
        time.sleep(1)

        while testIsRunning:
            data = load.GetInputValues()
            writeData(formatDataRow(data), csv_w)

            # stop if the read voltage drops below 3 volts, or amps below 100 mA
            if data['current'] < 0.1:
                break

            #sleep for a second before sampling again
            try:
                time.sleep(1)
            except IOError:
                pass


    #Stop the test and exit
    print "Test finished"
    updateSettings("Turned the load off", load.TurnLoadOff())
    updateSettings("Set to local control", load.SetLocalControl())

if __name__ == '__main__':
    # Support Ctrl-C early exit from test
    signal.signal(signal.SIGINT, stopTest)
    signal.signal(signal.SIGTERM, stopTest)

    resistance = float(sys.argv[1])

    load = dcload.DCLoad()
    load.Initialize('COM2', 9600)
    runBatteryTest(load, resistance)
