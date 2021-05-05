# Python to C Compiler
This is a Python to C compiler created with use of [PLY](https://www.dabeaz.com/ply/ply.html). <br />
<br />
This compiler uses a [subset of Python](https://docs.python.org/3/library/typing.html) that has explicit typing and uses brackets and semicolons to handle whitespace. It supports integers, booleans, lists and strings. 

## Example of Python Subset
```
def is_even(num: int)->bool: {
    if num % 2 == 0: {
        return True;
    } else: {
        return False;
    }
}
```

## How to Run the Compiler
To run the script, you need to execute the compiler.py file. Executing this file will put the
artifacts into the /out folder. If used without the -f argument, each example will be contained in a
subfolder. To verify the output files, run gcc -o out *.c and then run the ./out executable.

## Contributors
Alejandra Villegas <br />
Temy Chirkov <br />
Rochelle Solomon 
