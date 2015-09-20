from ntpath import basename, dirname
import os
import subprocess
from subprocess import Popen
import sys
from os import remove

x264_path = 'C:\\Program Files (x86)\\megui\\tools\\x264\\x264.exe '
ffmpeg_path = 'C:\\Program Files (x86)\\megui\\tools\\ffmpeg\\ffmpeg.exe '


def read_cli(process):
    text = ''
    for line in process.stderr:
        line = line.rstrip() + '\n'
        sys.stdout.write(line.encode('utf-8'))
        if any(string in line for string in ('[error]', 'wrong', 'does not', '[warning],', 'ffms', 'encoded', 'ffmpeg',
                                             'Input', 'Output', 'Stream')):
            text += line
        if any(string in line for string in ('[error]', 'wrong', 'does not')):
            return False
    text.replace('\n\n', '\n')
    text += '\n\n'
    return text


def file_list_gen(root_path):
    for root_path, subdirectories, files in os.walk(root_path):
        for name in files:
            if os.path.splitext(name)[1].lower() == '.avi' and 'MVI' in os.path.splitext(name)[0]:
                yield os.path.join(root_path, name)


def file_encode(path):
    full_file_name = basename(path)
    file_name = os.path.splitext(full_file_name)[0]
    dir_path = dirname(path)

    with open('logfile.txt', 'a') as log_file:
        text = 'Processing file: ' + path + '\n'

        # ================ Video encode ================
        commandline = x264_path + \
            '--level 4.1 --preset placebo --tune film --crf 19.0 ' \
            '--qpmin 10 --qpmax 51 --vbv-bufsize 78125 --vbv-maxrate 62500 ' \
            '--output "' + dir_path + '\\output.mp4" "' + path + '"'
        process = Popen(commandline, stderr=subprocess.PIPE)
        text += read_cli(process)

        process.wait()

        # ================ Audio encode ================
        commandline = ffmpeg_path + '-y -i "' + path + '" -codec:a libmp3lame -qscale:a 0  "' + \
            dir_path + '\\' + file_name + '.mp3"'
        process = Popen(commandline, stderr=subprocess.PIPE)

        text += read_cli(process)

        process.wait()

        # ================ Merge ================
        commandline = ffmpeg_path + '-y -i "' + dir_path + '\\output.mp4" -i "' + dir_path + '\\' + file_name + '.mp3" ' \
            '-c:v copy -c:a copy "' + dir_path + '\\' + file_name + '.mp4"'
        process = Popen(commandline, stderr=subprocess.PIPE)

        text += read_cli(process)

        process.wait()

        log_file.write(text.encode('utf-8'))

        remove(dir_path + '\\' + file_name + '.mp3')
        remove(dir_path + '\\output.mp4')

    return True


files_list = file_list_gen(os.getcwd())

for full_path in files_list:
    if not file_encode(full_path):
        with open('logfile.txt', 'a') as log:
            log.write('========== File ' + full_path + ' is soooo bad. ==========\n')

    with open('logfile.txt', 'a') as log:
        log.write('\n==================================================\n')
