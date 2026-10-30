# main.py
# Entry point for the CPU simulator

import sys
from cpu import CPU
from memory import Memory

def load_instructions(filename):
    """
    Load instructions froma a text file.
    Each line is one instruction.
    """
    with open(filename, "r") as file: 
        return [line.strip() for line in file if line.strip()]

def main():
    # Load instruction from file 
    # Usage: python main.py [-q] [program.asm]   (default: instructions.txt)
    #   -q  quiet mode: print only SYSCALL output
    args = sys.argv[1:]
    quiet = "-q" in args
    files = [a for a in args if a != "-q"]
    filename = files[0] if files else "instructions.txt"
    instructions = load_instructions(filename)

    #create memory
    memory = Memory()

    #create CPU
    cpu = CPU(instructions, memory, quiet=quiet)

    #run the CPU
    cpu.run()

# Only run main() if this file is excutec directly (not imported as a module)
if __name__ == "__main__":
    main()