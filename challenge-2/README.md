# Python Script
## how-to obtain the result
Run the Python script with the requested flags to inspect system metrics.

From repository root:
- `python3 challenge-2/myscript.py -h`
- `python3 challenge-2/myscript.py -d`
- `python3 challenge-2/myscript.py -c`
- `python3 challenge-2/myscript.py -p`
- `python3 challenge-2/myscript.py -r`
- `python3 challenge-2/myscript.py -o`

You can combine options in one command, for example:
- `python3 challenge-2/myscript.py -d -c -r`


## executed commands 
- `python3 challenge-2/myscript.py -h`
- `python3 challenge-2/myscript.py -d`
- `python3 challenge-2/myscript.py -c`
- `python3 challenge-2/myscript.py -p`
- `python3 challenge-2/myscript.py -r`
- `python3 challenge-2/myscript.py -o`


## short explanation
The script provides a small CLI called `myscript.py` with five options:
- `-d/--disk`: shows per-volume disk total/used/free/used percentage.
- `-c/--cpu`: shows logical and physical cores, CPU usage, and frequency.
- `-p/--ports`: lists listening ports.
- `-r/--ram`: shows total/used/free memory and used percentage.
- `-o/--overview`: prints the top 10 processes by CPU usage.

If no option is passed, the script prints the help output.


### macOS vs Unix/Linux notes
- CLI usage is the same on both: `python3 challenge-2/myscript.py [options]`.
- The script itself uses OS-specific system commands/APIs under the hood, so values can differ by platform.
- CPU frequency may show `N/A` on some macOS machines (for example Apple Silicon), while Linux hosts often expose it via `/proc/cpuinfo`.
- Listening ports are collected with a fallback chain: `lsof` first, then `ss`, then `netstat`. Availability of these tools depends on the OS and installed packages.
- Process and memory numbers are point-in-time snapshots and can change between runs on any shell/OS.