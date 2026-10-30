#cpu.py 
#simulates a simple CPU

from isa import Instruction

DISP_FORMAT = "HEX" # INT or HEX form

class CPU:
    def __init__(self, instructions, memory, quiet=False):
        """
        instructions: list of instruction strings
        memory: Memory object
        quiet: True = print only SYSCALL output (no listing, no register/memory dump)
        """

        self.PC = 0
        self.BASE_PC = self.PC
        self.registers = [0] * 32
        self.registers[29] = 0x7FFFEFFC  # $sp starts at the same address as QtSpim/MARS
        self.memory = memory
        self.running = True
        self.quiet = quiet
        self.input_buffer = []  # numbers typed but not read yet by SYSCALL 5

        # Parse instructions into Instruction objects
        #   decode(); docode2(); decode3()
        # decode() split opcode and operands
        # decode2() prepare value of operands
        # decode3() convert instruction to hexcode
        self.instructions = [
            Instruction(line) for line in instructions
        ]

        # display all instruction hexcode and raw instruction
        # and copy all instruction to memory
        if self.instructions[0].opcode == '.ORG':
            textpos = self.instructions[0].operands[0]
        for instrctn in self.instructions:
            # put hexcmd in to memory
            strPC = ('0'*7+hex(textpos)[2:])[-8:]
            if not self.quiet:
                print(strPC, instrctn.hexcmd, instrctn.raw, end='\t')
            if instrctn.hexcmd != None:
                for i in range(4):
                    #print(int(instrctn.hexcmd[i*2:i*2+2],16), end=" ")
                    val = int(instrctn.hexcmd[i*2:i*2+2],16)
                    self.memory.write(textpos, val)
                    textpos += 1
            if not self.quiet:
                print()


    def fetch(self):
        """
        Fetch the next instruction using PC
        """

        if self.PC - self.BASE_PC >= len(self.instructions):
            self.running = False 
            return None

        instr = self.instructions[self.PC - self.BASE_PC]
        
        return instr

    def validate(self):
        """
        Check is all status are valid
        """
        if self.registers[0] != 0:
            print("****************Warning: register 0 must alwasys be zero")
            self.registers[0] = 0
            #return 1  # zero change
        for i  in range(32):
            L = len(hex(self.registers[i]))
            if L > 8+2:
                print('"****************Warning: register', i, 'too large')
                self.registers[i] = int(hex(self.registers[i])[-8:])
            #return 2 # register too large
    
    def pc2hex(self):
        strpc = ('0'*7+hex(self.PC*4)[2:])[-8:]
        return strpc.upper()

    def run(self):
        """
        Main fetch-decode-execute loop
        """
        while self.running:
            instr = self.fetch()
            # instr.decode() #skip this since perform in constructor
            
            
            if instr is None:
                break
            if not self.quiet:
                print(f"Executed: {self.pc2hex()} {instr.raw}")
            self.execute(instr)


            # Debug output uncomment below
            if instr.opcode != '.ORG' and not self.quiet:
                self.debug()
                pass

            self.validate()
            self.PC += 1
        #Show register after finish
        if not self.quiet:
            print("Last STATE")
            self.debug()

    def debug(self):
        """
        Show all register
        """
        W = 5
        print(f"Registers:")
        for i in range(len(self.registers)):
            if i%W==0: print(f"{i:>2}-{i+W-1:>2}", end="")
            val = self.registers[i]
            if DISP_FORMAT == 'HEX':
                if val < 0: val = 2**32 + val
                hval = ('0'*7 + hex(val)[2:])[-8:]
                print(f"{hval:>11}",end="")
            else:
                print(f"{val:>11}",end="")
                
            if i%W==W-1: print()
        print("\n"+"-" * 80)
        self.memory.dump(4*(self.BASE_PC+1))  #Start from first line of text
        print("-" * 80)

    def execute(self, instr):
        """
        Execute a single instruction 
        """
        opcode = instr.opcode
        ops = instr.operands
        # ADD rd, rs, rt        # Adds the values in register rs and rt and stores the result in rd
        if opcode == "ADD":
            rd,rs,rt = ops[0], ops[1], ops[2]
            self.registers[rd] = self.registers[rs] + self.registers[rt]

        # ADDI rt, rs, immediate # Adds an immediate value to the value in register rs and store the result in rt 
        elif opcode == "ADDI":
            rt, rs, imm = ops[0], ops[1], ops[2]
            imm = imm & 0xffff
            if imm >= 2**15: imm = -(2**16 - imm)
            self.registers[rt] = self.registers[rs] + imm

        # ADDIU rt, rs, immediate # Adds an immediate unsigned value to the value in register rs and store the result in rt 
        elif opcode == "ADDIU":
            rt, rs, imm = ops[0], ops[1], ops[2]
            self.registers[rt] = (self.registers[rs] + imm) & 0xffffffff
            
        # SW rt, offset(rs)     # Stores the value form register rt into memory at address (rs + offset)
        elif opcode == "SW":
            rt, rs, offset = ops[0], ops[1], ops[2]
            address = self.registers[rs] + offset
            value = self.registers[rt]
            self.memory.write(address, value)

        # LUI rt, immediate     # Loads an immediate into upper half of register rt
        elif opcode == "LUI":
            rt, imm = ops[0], ops[1]
            self.registers[rt] = imm<<16

        # ORI rt, immediate     # OR an immediate with lower half of register rt
        elif opcode == "ORI":
            rt, rs, imm = ops[0], ops[1], ops[2]
            self.registers[rt] = self.registers[rs] | (0xffff & imm)
            
        # LW rt, offset(rs)     # Loads a value from memroy at addres (rs + offset) into register rt
        elif opcode == "LW":
            rt, rs, offset = ops[0], ops[1], ops[2]
            address = self.registers[rs] + offset
            self.registers[rt] = self.memory.read(address)    

        # SLTI rt, rs, immediate # Set if less than rt = rs<immediate? 1:0
        elif opcode == "SLTI":
            rt, rs, imm = ops[0], ops[1], ops[2]
            if self.registers[rs] >= 2**31:
                self.registers[rs] = -(2**32 - self.registers[rs])
            if imm >= 2**15: imm = -(2**16 - imm)
            self.registers[rt] = 1 if self.registers[rs]<imm else 0
        
        # SLTIU rt, rs, immediate # Set if less than rt = rs<immediate? 1:0
        elif opcode == "SLTIU":
            rt, rs, imm = ops[0], ops[1], ops[2]
            if self.registers[rs]<0:
                self.registers[rs] = (2**32 + self.registers[rs])
            if imm < 0: imm = 2**16 + imm
            self.registers[rt] = 1 if self.registers[rs]<imm else 0

        # BEQ rs, rt, offset
        # If the values in registers rs and rt are equal,
        # branch to a new instruction by modifyin the PC    
        elif opcode == "BEQ":
            rt, rs, offset = ops[0], ops[1], ops[2]

            # Compare registers and update PC if equal 
            if self.registers[rs] == self.registers[rt]:
                self.PC += offset
                if not self.quiet: print(f"BEQ check: R{rs}={self.registers[rs]} R{rt}={self.registers[rt]}")

        # BNE rs, rt, offset
        # If the values in registers rs and rt are not equal,
        # branch to a new instruction by modifyin the PC    
        elif opcode == "BNE":
            rt, rs, offset = ops[0], ops[1], ops[2]

            # Compare registers and update PC if equal 
            if self.registers[rs] != self.registers[rt]:
                self.PC += offset
                if not self.quiet: print(f"BNE check: R{rs}={self.registers[rs]} R{rt}={self.registers[rt]}")

        # J address
        # branch to specific address by modifying the PC  
        elif opcode == "J":
            target = ops[0]//4
            self.PC = target - 1 #step back 1 instruction since +1 in the loop run

        # JAL address
        # save return address (byte address of the next instruction) in $31, then jump like J
        elif opcode == "JAL":
            self.registers[31] = (self.PC + 1) * 4
            target = ops[0]//4
            self.PC = target - 1 #step back 1 instruction since +1 in the loop run

        # JR rs
        # jump to the byte address stored in register rs (return from function with JR $31)
        elif opcode == "JR":
            rs = ops[0]
            self.PC = self.registers[rs]//4 - 1 #step back 1 instruction since +1 in the loop run

        # SYSCALL
        # service number in $2:  1 = print $4,  5 = read int into $2,  10 = exit
        elif opcode == "SYSCALL":
            service = self.registers[2]
            if service == 1:
                val = self.registers[4] & 0xffffffff
                if val >= 2**31: val -= 2**32   # show as signed 32-bit
                print(val)
            elif service == 5:
                while not self.input_buffer:    # numbers may be on one line ("5 2") or one per line
                    self.input_buffer = input().split()
                self.registers[2] = int(self.input_buffer.pop(0))
            elif service == 10:
                self.running = False
            else:
                print(f"error unknown SYSCALL service {service}")
                self.running = False

        # HALT
        # Stops CPU execution
        elif opcode  == "HALT":
            self.running = False

        # .ORG directive
        # Change PC to new value
        # Hope this line occur as first line of text part and using only one time
        elif opcode  == ".ORG":
            self.PC = ops[0]//4 - 1 #step back 1 instruction since +1 in the loop run
            self.BASE_PC = self.PC
            #self.running = False


