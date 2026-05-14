import serial
import time

# Adjust serial port
SERIAL_PORT = "/dev/tty.usbserial-10"
PHONE_NUMBER = "+55987667891"
MESSAGE = "Hello from Digicom GSM modem"
SIM_PIN = None                           # Set to "1234" if SIM requires a PIN

# Open serial port with the standard default valuer of the modem being used
ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=9600,                # communication speed, must match modem
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,                    # each single line read waits max 1 second; higher-level timeout later (read_response)
)

time.sleep(0.2)

# Serial response parser
def read_response(timeout=5, terminators=("OK", "ERROR", ">")):
    """
    Read lines from the modem until a known terminator appears or the deadline expires.  
    Returns the full response as a string.
	Serial responses arrive asynchronously, so you'll usually get an empty string.  
	readline() with a per-line timeout + an outer timeout.
    """
    lines = []                                         # creates buffer for response
    deadline = time.time() + timeout                   # creates a deadline
    while time.time() < deadline:
        raw = ser.readline()                           # read one line
        line = raw.decode(errors="ignore").strip()     # decode bytes into string
        if not line:                                   # ignore empty read
            continue
        lines.append(line)                             # save response into lines[]
        print(f"    {line}")                           # prints modem response
        if any(t in line for t in terminators):        # checks for terminators
            break
    return "\n".join(lines)                            # returns the full response


def send_at(command, timeout=5, terminators=("OK", "ERROR", ">")):
    """Send an AT command and return the full modem response."""
    print(f">>> {command}")
    ser.write((command + "\r").encode())
    return read_response(timeout=timeout, terminators=terminators)

# checks if response contains "OK"
def assert_ok(response, label=""):
    if "OK" not in response:
        raise RuntimeError(f"Expected OK{' for ' + label if label else ''}, got: {response!r}")


try:
    ser.reset_input_buffer()  # clear buffer

    # Basic checks(serial cable, baud rate and modem response)
    assert_ok(send_at("AT"), "AT")

    # Disable echo so modem doesn't repeat commands back
    assert_ok(send_at("ATE0"), "ATE0")

    # SIM/network check
    pin_resp = send_at("AT+CPIN?")
    if "+CPIN: SIM PIN" in pin_resp:                                                         # if pin required
        if SIM_PIN is None:
            raise RuntimeError("SIM requires a PIN — set SIM_PIN at the top of the script.")
        assert_ok(send_at(f'AT+CPIN="{SIM_PIN}"'), "PIN entry")
        time.sleep(2)                                                                        # give the modem time to register after PIN
    elif "+CPIN: READY" not in pin_resp:
        raise RuntimeError(f"Unexpected CPIN response: {pin_resp!r}")

    creg = send_at("AT+CREG?")                                                               # check if modem connects to GSM network
    # +CREG: 0,1 → registered home; 0,5 → roaming
    if ",1" not in creg and ",5" not in creg:
        raise RuntimeError(f"Modem not registered to GSM network: {creg!r}")

    csq = send_at("AT+CSQ")                                                                  # check signal quality
    # First value: 0–9 = poor, 10–15 = good, 16–31 = excellent, 99 = unknown
    print(f"    Signal interpretation: 10-15=good, 16-31=excellent, 99=unknown")

    # Prepare SMS
    assert_ok(send_at("AT+CMGF=1"), "text mode")                                             # set text mode (not PDU)

    # Send SMS
    # tell the modem destination number; it responds with '>'
    print(f'>>> AT+CMGS="{PHONE_NUMBER}"')
    ser.write(f'AT+CMGS="{PHONE_NUMBER}"\r'.encode())                                        # double check terminator "\r"
    prompt = read_response(timeout=5, terminators=(">", "ERROR"))

    if ">" not in prompt:
        raise RuntimeError(f"Did not receive SMS prompt '>': {prompt!r}")

    # send the message body, terminated by Ctrl+Z (0x1A)
    # Do NOT send a trailing \r — the modem uses Ctrl+Z as the only delimiter
    print(f">>> {MESSAGE!r} + <CTRL+Z>")
    ser.write(MESSAGE.encode() + bytes([0x1A]))

    # Allow up to 10 seconds for network round-trip
    sms_resp = read_response(timeout=10, terminators=("OK", "ERROR", "+CMGS"))
    if "ERROR" in sms_resp:
        raise RuntimeError(f"SMS send failed: {sms_resp!r}")

    print("\n✓ SMS sent successfully.")

finally:
    ser.close()
