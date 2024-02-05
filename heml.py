import subprocess
import platform
import re


def get_windows_devices_to_change() -> list:
    current_output = subprocess.run(["powershell", "-Command", "Get-AudioDevice -Playback"],
                                    shell=True, stdout=subprocess.PIPE, text=True).stdout

    current_input = subprocess.run(["powershell", "-Command", "Get-AudioDevice -Recording"],
                                   shell=True, stdout=subprocess.PIPE, text=True).stdout

    current_output_device = re.search(r'ID\s*: (\{.*?\}\.\{.*?\})', current_output).group(1)
    current_input_device = re.search(r'ID\s*: (\{.*?\}\.\{.*?\})', current_input).group(1)

    command = "Get-AudioDevice -List"
    result = subprocess.run(["powershell", "-Command", command], shell=True, stdout=subprocess.PIPE, text=True)
    audio_devices_list = result.stdout.split("\n\n")

    devices_to_change = []
    for audio_device in audio_devices_list:
        match = re.search(r'Name\s*: Line 1 \(Virtual Audio Cable\)\nID\s*: (\{.*?\}\.\{.*?\})', audio_device)
        if match:
            print(match.group(1))
            devices_to_change.append(match.group(1))

    return devices_to_change


def change_devices(revert: bool = False):
    """
    Changes input/output system devices for the purpose of running tests.
    Saves information about what devices were changed so that they can be restored after the tests are finished

    :param revert: Changes back the devices
    """
    if platform.system() == "Darwin":

        if revert is False:
            current_input_device = subprocess.run(["SwitchAudioSource -c -t input"],
                                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                  text=True).stdout
            current_output_device = subprocess.run(["SwitchAudioSource -c -t output"],
                                                   shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                   text=True).stdout

            with open('default_devices.py', 'w') as f:
                _ = {'input': current_input_device.strip(), 'output': current_output_device.strip()}
                f.write(f"{_}")

            mac_output = 'BlackHole 16ch'
            mac_input = 'BlackHole 16ch'

        else:
            with open('default_devices.py', 'r') as f:
                devices = eval(f.readline())
                mac_output = devices['output']
                mac_input = devices['input']

        commands = [f"SwitchAudioSource -t output -s '{mac_output}'",
                    f"SwitchAudioSource -t input -s '{mac_input}'"]

        for command in commands:
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    elif platform.system() == "Windows":
        if revert is False:
            devices_to_change = get_windows_devices_to_change()
            for device in devices_to_change:
                result = subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{device}'"], shell=True,
                                        stdout=subprocess.PIPE, text=True)
                print(result.stdout)
        else:
            with open('default_devices.py', 'r') as f:
                devices = eval(f.readline())
                win_output = devices['output']
                win_input = devices['input']
            result = subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{win_output}'"], shell=True,
                                    stdout=subprocess.PIPE, text=True)
            result = subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{win_input}'"], shell=True,
                                    stdout=subprocess.PIPE, text=True)


if __name__ == '__main__':
    change_devices(True)

