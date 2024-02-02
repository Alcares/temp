import pyaudio
import subprocess
import re 	

pa = pyaudio.PyAudio()

command = "Get-AudioDevice -List"
result = subprocess.run(["powershell", "-Command", command], shell=True, stdout=subprocess.PIPE, text=True)
data = result.stdout.split("\n\n")

devices = []
for block in data:
    match = re.search(r'Name\s*: Line 1 \(Virtual Audio Cable\)\nID\s*: (\{.*?\}\.\{.*?\})', block)
    if match:
        print(match.group(1))
        devices.append(match.group(1))

for device in devices:
    result = subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{device}'"], shell=True, stdout=subprocess.PIPE, text=True)
    print(result.stdout)