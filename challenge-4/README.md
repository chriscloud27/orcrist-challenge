# Challenge-4
Oh, no! We don't know what happened to this binary! Can you help us? When we execute the binary, it always returns Ooooh, what's wrong? :(. How can we fix it? We expected the message Congrats! :).

TIP: The binary was compiled for x86_64 Linux.

# how-to obtain the result
terminal> `docker run -v /path/to/binary:/binary alpine /binary`

# executed commands
> I tried finding it myself as not being aware of how. I wanted to learn before I'd ask Claude on the solution. I did not find it within ~30 min of time (see ARCHIVE section). Going boths ways was giving me a good understanding of solution path and how to fix in future.

Inspecting the binary file with a simple command
terminal> `strings challenge-4/blackbox`

**Output**
```bash
/lib64/ld-linux-x86-64.so.2
libc.so.6
printf
__cxa_finalize
access
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u+UH
[]A\A]A^A_
the_magic_filez.txt
Congrats! :)
Ooooh, what's wrong? :(
:*3$"
GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0
...
```

The output shows that a file `the_magix_filez.txt` and Claude explains me that `acccess()` is called to check for the existing file which is required to print the `Congrats! :)` message. Verify and see how `access()` is called.
terminal> `objdump -d challenge-4/blackbox 2>/dev/null | grep -A 20 "<main>"`
I cannot interprete the output so I asked to interprete. The logic for the binary is:

- Calls access("the_magic_filez.txt", F_OK) — checks if the file exists
- If it exists (eax == 0): prints Congrats! :) → returns 0
- If it doesn't exist (eax != 0): prints Ooooh, what's wrong? :( → returns 255 (0xFFFFFFFF)

So, creating the file `the_magix_filez.txt` in the same directory that the binary is stored in will fix the issue. 

Let's try if that's the case:
terminal>
```bash
docker run --rm -it \
  --platform linux/amd64 \
  -v "$(pwd)/challenge-4/blackbox:/binary" \
  ubuntu:22.04 /bin/bash
root@e13f803c7e00:/# touch the_magic_filez.txt && /binary
Congrats! :)root@e13f803c7e00:/# 
````

We got it! 


# ARCHIVE
**Hint**
Run the docker container locally from Mac as the architecture of macOS cannot directly run an x86_64 Linux binary on macOS because they use different executable formats (ELF vs. Mach-O) and system interfaces. I chose an Ubuntu container iamge for troubleshooting.

terminal> `docker run --rm --platform linux/amd64 -v "$(pwd)/challenge-4/blackbox:/binary:ro" ubuntu:22.04 /binary`

**Further analytics (before asking Claude on the solution)**

**Jump into the container image:**
```
docker run -d \
  --name challenge4-debug \
  --platform linux/amd64 \
  --cap-add=SYS_PTRACE \
  -v "$(pwd)/challenge-4/blackbox:/binary:ro" \
  ubuntu:22.04 \
  sleep infinity
```
```
docker exec -it ede bash
```

**Output**
```
Ooooh, what's wrong? :(%  
```

Good. I am seeing the error now.



# short explanation
1. I opened the binary to reconstruct the error message myself.
1. On my research I found that the idea that the file may need some parameters or further requirements. // Also I found that the "rosetta error" may indicate this file is missing or the path is incorrect. 
2. I analyzed the file to retrieve more information about it: `file challenge-4/blackbox`
```
challenge-4/blackbox: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=1caf23a27b0de40853dfb8afd9ef67eb12b9d73f, for GNU/Linux 3.2.0, not stripped
```
1. I run a libary check: `ldd /binary`
```
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fffff591000)
    /lib64/ld-linux-x86-64.so.2 (0x00007ffffffc4000)
```
1. Interprete the outputs with the help of AI

    The file command confirms your binary is a standard x86-64 Linux executable requiring the /lib64/ld-linux-x86-64.so.2 dynamic linker (glibc-based). 

    The ldd output shows the binary is dynamically linked against libc.so.6 and expects the standard glibc linker. This confirms it was compiled for a glibc-based system (like Ubuntu), not a musl-based one (like Alpine). 

    The "rosetta error" occurs because the Alpine container lacks the glibc dynamic linker. (I started the binary with alpine at the beginning and then changed to Ubuntu)
1. I install the library I believe is missing: `apt-get install -y libc6` but the message "Ooooh, what's wrong?" keeps showing up.

2. `readelf` is not installed in the container image so I install it and run an interpreter
```
apt-get update
apt-get install -y binutils
readelf -a /binary | grep -i interpreter
readelf -d /binary | grep -i NEEDED
```
**Output**
````
root@ec0c87e047ba:/# readelf -a /binary | grep -i interpreter
      [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
root@ec0c87e047ba:/# 
root@ec0c87e047ba:/# readelf -d /binary | grep -i NEEDED
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
````
1. Given the analysis the binary is correctly linked against libc.so.6 and the dynamic linker is present in the Ubuntu container, the problem is likely logical, not technical. 
1. Further dynamic analytics: `apt-get install strace && strace /binary`
```
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
[ Process PID=495 runs in 64 bit mode. ]
[ Process PID=495 runs in x32 mode. ]
Ooooh, what's wrong? :(+++ exited with 255 +++
```
1. The error message from the binary "Ooooh, what's wrong? :(", followed by exited with 255 means the binary itself is running but is failing an internal check, likely due to incorrect input.
1. Trying to run the binary with input: `/binary orcrist` and `/binary --help` receiving still the same output.
1. Further with: `apt-get install ltrace && ltrace /binary` outputs "/proc/543/exe" is ELF from incompatible architecture"
1. May be a permissions/security restriction in Docker. Enhance docker command to use the CAP_SYS_PTRACE capability: 
```
docker run -d \
  --name challenge4-debug \
  --platform linux/amd64 \
  --cap-add=SYS_PTRACE \
  -v "$(pwd)/challenge-4/blackbox:/binary:ro" \
  ubuntu:22.04 \
  sleep infinity
```
1. Permissions ok. Start docker run again. Further check with utils: `apt-get update && apt-get install -y binutils`