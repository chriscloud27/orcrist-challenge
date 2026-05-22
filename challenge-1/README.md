# Challenge 1: Basic search
> We've found a sample.log file with 3360 lines but we need some info. Can you help us?

## Count all lines with 500 HTTP code. 
### How to obain the result
Using built-in Unix commands to quickly receive a result. `grep` is great to search within files/folders. `wc` is great to count results.

### Executed Commands
terminal> `grep -o "500" challenge-1/sample.log | wc -l`
```
714
```

### Short Explanation
Navigating the `sample.log` file with greap and focussing on the 500 errors. Then count the outputted entries as a simple number which is 714. So 714 internal server errors.


## Count all GET requests from yoko to /rrhh location and if it was successful (200).

### How to obain the result
Using `grep` to search within the file. Pipe the output multiple times to stripe down the output on the expected outcome.

### Executed Commands
terminal> `grep "yoko" challenge-1/sample.log | grep "/rrhh" | grep "200" | wc -l`
grep "yoko" challenge-1/sample.log | grep "200" | grep "/rrhh" | wc -l
```
11
```

### Short Explanation
First receiving all lines with "yoko" to then search for the path "/rrhh" and the http/200. The sequence path <> http/200 is not important and `grep "yoko" challenge-1/sample.log | grep "200" | grep "/rrhh" | wc -l` outputs the same result.


## How many requests go to /?
### How to obain the result
The `/` needs to be escaped to finish the command.

### Executed Commands
terminal> `grep "\/" challenge-1/sample.log | wc -l`
```
3360
```

### Short Explanation
The prefix "\" escapes the slash.


## Count all lines without 5XX HTTP code.
### How to obain the result
Use a regex to count all lines that contain with a 5xx HTTP status. The `-v` flag inverts the output. 

### Executed Commands
terminal> `grep -v "5[0-9][0-9]" challenge-1/sample.log | wc -l`
```
2191
```

### Short Explanation
There is not difference between HTTP/1.0 and HTTP/2.0. Without the `-v` flag 1469 lines are found. +2191 lines this equals the total amount of 3660 lines. Optional the `-E` command can be used to enable regex interpretation.


## Replace all 503 HTTP codes by 500, how many requests have a 500 HTTP code?
### How to obain the result
Count before, change, count again. Use `sed` which differs in Mac (BSD) and Linux (GNU) and needs a different syntax in the `-i` flag.

### Executed Commands
terminal> `sed -i '' 's/ 503 / 500 /g' challenge-1/sample.log`
terminal> `grep " 500 " challenge-1/sample.log | wc -l`
```
1469
```

### Short Explanation
The count before is 714. 
The count after is 1469.