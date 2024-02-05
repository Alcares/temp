import subprocess
import platform
import re
import os

TEMP_FILE_PATH = "default_devices.py"


def read_temp_file() -> (str, str):
    with open(TEMP_FILE_PATH, 'r') as f:
        devices = eval(f.readline())
        output_device = devices['output']
        input_device = devices['input']

    os.remove(TEMP_FILE_PATH)

    return output_device, input_device


def write_to_temp_file(output_command: list, input_command: list):
    current_output_device = subprocess.run(output_command, shell=True,
                                           stdout=subprocess.PIPE, text=True).stdout
    current_input_device = subprocess.run(input_command, shell=True,
                                          stdout=subprocess.PIPE, text=True).stdout
    if platform.system() == 'Windows':
        current_output_device = re.search(r'ID\s*: (\{.*?\}\.\{.*?\})', current_output_device).group(1)
        current_input_device = re.search(r'ID\s*: (\{.*?\}\.\{.*?\})', current_input_device).group(1)

    with open(TEMP_FILE_PATH, 'w') as f:
        _ = {'input': current_input_device.strip(), 'output': current_output_device.strip()}
        f.write(f"{_}")


def get_windows_devices_to_change() -> list:
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
            write_to_temp_file(["SwitchAudioSource -c -t output"],
                               ["SwitchAudioSource -c -t input"])

            output_device = 'BlackHole 16ch'
            input_device = 'BlackHole 16ch'

        else:
            output_device, input_device = read_temp_file()

        commands = [f"SwitchAudioSource -t output -s '{output_device}'",
                    f"SwitchAudioSource -t input -s '{input_device}'"]

        for command in commands:
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    elif platform.system() == "Windows":
        if revert is False:
            write_to_temp_file(["powershell", "-Command", "Get-AudioDevice -Recording"],
                               ["powershell", "-Command", "Get-AudioDevice -Playback"])
            devices_to_change = get_windows_devices_to_change()

            for device in devices_to_change:
                subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{device}'"], shell=True,
                               stdout=subprocess.PIPE, text=True)
        else:
            output_device, input_device = read_temp_file()

            subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{output_device}'"], shell=True,
                           stdout=subprocess.PIPE, text=True)
            subprocess.run(["powershell", "-Command", f"Set-AudioDevice -ID '{input_device}'"], shell=True,
                           stdout=subprocess.PIPE, text=True)


if __name__ == '__main__':
    change_devices(revert=True)



