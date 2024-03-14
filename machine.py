from ISA import *

N = 1
Z = 2
V = 4
C = 8
MAX = 2 ** 31 - 1  # 2^31-1
MIN = -2 ** 31  # -2^31


class Cell:
    def __init__(self):
        self.value = -1
        self.ins = Instruction(Opcode.ADD, [])


class Register:
    def __init__(self, reg_type: RegisterType):
        self.name = reg_type
        if reg_type == RegisterType.SP:
            self.value = 256
        else:
            self.value = 0

    # return an int or an instruction
    def get_value(self):
        return self.value

    # set an int or an instruction
    def set_value(self, value):
        self.value = value

    def to_string(self):
        if isinstance(self.value, Instruction):
            return self.value.to_string()
        else:
            return str(self.value)


class Buffer:
    def __init__(self, size):
        self.buf = [-1] * size
        self.read_pointer = 0
        self.write_pointer = 0
        self.size = size


class DataPath:
    def __init__(self, size: int, input_file: str):
        self.memory = [Cell()] * size
        self.stack = [0] * 256
        self.size = size
        self.input_buffer = Buffer(256)
        self.output_buffer = Buffer(256)
        self.registers = {
            'BR': Register(RegisterType.BR),
            'AC': Register(RegisterType.AC),
            'SP': Register(RegisterType.SP),
            'PS': Register(RegisterType.PS),
            'IP': Register(RegisterType.IP),
            'AR': Register(RegisterType.AR),
            'AR1': Register(RegisterType.AR),
            'IR': Register(RegisterType.IR),
            'R1': Register(RegisterType.R1),
            'R2': Register(RegisterType.R2),
            'R3': Register(RegisterType.R3),
            'R4': Register(RegisterType.R4)
        }
        self.input_index = int(size * 3 / 4 - 1)
        self.output_index = self.input_index
        self.io_part = int(size * 3 / 4 - 1)
        if input_file != '':
            with open(input_file) as f:
                c = f.read()
                for i in c:
                    assert self.input_index < self.size, 'Input file too large!'
                    self.set_value_memory(self.input_index, char[i])
                    self.input_index += 1

    def set_value_memory(self, index: int, value: int):
        old_cell = self.memory[index]
        new_cell = Cell()
        new_cell.ins = old_cell.ins
        new_cell.value = value
        self.memory[index] = new_cell

    def get_value_register(self, choice: str):
        return self.registers[choice].get_value()

    def set_value_register(self, choice: str, value):
        self.registers[choice].set_value(value)

    def add_value_register(self, choice: str, value: int):
        self.registers[choice].add(value)

    def min_value_register(self, choice: str, value: int):
        self.registers[choice].min(value)

    def get_string_register(self, choice: str) -> str:
        return self.registers[choice].to_string()

    def get_value_memory(self, index: int) -> int:
        return self.memory[index].value

    def print_registers(self):
        print("BR:%s, R1:%s, R2:%s, R3:%s, R4:%s, AC:%s, SP:%s, PS:%s, IP:%s, AR:%s, IR:%s" %
              (self.get_string_register('BR'), self.get_string_register('R1'),
               self.get_string_register('R2'), self.get_string_register('R3'),
               self.get_string_register('R4'), self.get_string_register('AC'),
               self.get_string_register('SP'), self.get_string_register('PS'),
               self.get_string_register('IP'), self.get_string_register('IP'),
               self.registers['IR'].to_string()), end="")


class ALU:
    def __init__(self):
        self.left = 0
        self.right = 0
        self.nzvc = 0

    @staticmethod
    def add(left: int, right: int):
        result = left + right
        if left + right > MAX:
            result = result & (2 ** 31 - 1)
            result = -2 ** 31 + result
        elif left + right < MIN:
            result = -left - right
            result = result & (2 ** 31 - 1)
            result = result - 1
        return result

    @staticmethod
    def min(left: int, right: int):
        result = left - right
        if left - right > MAX:
            result = result & (2 ** 31 - 1)
            result = -2 ** 31 + result
        elif left - right < MIN:
            result = -left - right
            result = result & (2 ** 31 - 1)
        return result

    @staticmethod
    def div(left: int, right: int):
        return int(left / right)

    @staticmethod
    def mul(left: int, right: int):
        return left * right

    @staticmethod
    def or_operation(left: int, right: int):
        return left | right

    @staticmethod
    def inversion(left: int, right: int):
        return -(left + right)

    def min_one(self):
        self.right = self.get_right() - 1

    def add_one(self):
        self.right = self.get_right() + 1

    def act(self, f):
        if f == ALU.add:
            if self.left > 0 > f(self.left, self.right) and self.right > 0:
                self.nzvc = V + C + N
            elif self.left < 0 <= f(self.left, self.right) and self.right < 0:
                if f(self.left, self.right) == 0:
                    self.nzvc = Z + V + C
                else:
                    self.nzvc = V + C
            else:
                if f(self.left, self.right) == 0:
                    self.nzvc = Z
                if f(self.left, self.right) < 0:
                    self.nzvc = N
        elif f == ALU.min:
            if self.left > 0 > self.right and f(self.left, self.right) < 0:
                self.nzvc = V + C + N
            elif self.left < 0 < self.right and f(self.left, self.right) >= 0:
                if f(self.left, self.right) == 0:
                    self.nzvc = Z + V + C
                else:
                    self.nzvc = V + C
            else:
                if f(self.left, self.right) == 0:
                    self.nzvc = Z
                if f(self.left, self.right) < 0:
                    self.nzvc = N
        return f(self.get_left(), self.get_right())

    def put_left(self, value: int):
        self.left = value

    def put_right(self, value: int):
        self.right = value

    def get_left(self):
        v = self.left
        self.left = 0
        return v

    def get_right(self):
        v = self.right
        self.right = 0
        return v


class CPU:
    def __init__(self, data_path: DataPath, program: {}):
        self.program = program
        self.fun = {}
        self.var = {}
        self.position = []
        self.data_path = data_path
        self.tick = 0  # clock tick
        self.ic = 0  # instruction counter
        self.alu = ALU()

    def tick_tick(self):
        self.tick += 1

    def ic_count(self):
        self.ic += 1

    def current_tick(self):
        return self.tick

    def decode(self):
        self.fun = self.program['Function']
        end = 0
        for i in self.program['Instruction']:
            new_cell = Cell()
            new_cell.ins = i
            self.data_path.memory[end] = new_cell
            end += 1
        end = len(self.program['Instruction'])
        for i in self.program['Variable']:
            self.var[i] = end
            if self.program['Variable'][i].isdigit():  # while variable is number
                v = int(self.program['Variable'][i])
                assert MAX >= v >= MIN, "Input value of variable {} is out of range".format(i)
                new_cell = Cell()
                new_cell.value = v
                self.data_path.memory[end] = new_cell
                end += 1
            else:
                # else:
                string = self.program['Variable'][i].rsplit(',')
                length = int(string[1])
                v = string[0]
                v = v[1:len(v) - 1]
                i = 0
                while i < length:
                    new_cell = Cell()
                    if i < len(v):
                        new_cell.value = char[v[i]]
                        self.data_path.memory[end] = new_cell
                    end += 1
                    i += 1

    def read_ins(self):
        # IP->AR
        self.alu.put_right(self.data_path.get_value_register('IP'))
        r = self.alu.act(ALU.or_operation)
        self.data_path.set_value_register('AR', r)
        self.tick_tick()
        # IP + 1 -> IP, [AR] -> IR
        self.data_path.set_value_register("IP", self.data_path.get_value_register('IP') + 1)
        self.tick_tick()
        self.data_path.set_value_register('IR', self.data_path.memory[self.data_path.get_value_register("AR")].ins)

    def read_var(self, var: str):
        # VAR -> AR
        pos = self.var[var]
        self.alu.put_right(pos)
        self.data_path.set_value_register("AR", self.alu.get_right())
        self.tick_tick()
        return self.data_path.get_value_memory(self.data_path.get_value_register("AR"))

    def addressing_arg(self, arg: str):
        if arg.isdigit():
            # Decoder -> AR
            self.data_path.set_value_register("AR", int(arg))
            self.tick_tick()
            return self.data_path.get_value_memory(int(arg))
        elif is_match("^#-?[1-9][0-9]*", arg) or is_match("^#0$", arg):
            return int(arg[1:])
        elif is_match("^\'.{1}\'$", arg) or arg == '\'\'':
            if arg == '\'\'':
                return char['']
            else:
                return char[arg[1]]
        else:
            assert arg in self.var.keys(), 'You use a variable {} which is not defined before'.format(arg)
            return self.read_var(arg)

    # get proper value
    def addressing(self, ins: Instruction):
        arg = ins.args[0]
        if arg.isdigit():
            # Decoder -> AR
            self.data_path.set_value_register("AR", int(arg))
            self.tick_tick()
            return self.data_path.get_value_memory(int(arg))
        elif is_match("^#-?[1-9][0-9]*", arg) or is_match("^#0$", arg):
            return int(arg[1:])
        elif is_match("^\'.{1}\'$", arg) or arg == '\'\'':
            if arg == '\'\'':
                return char['']
            else:
                return char[arg[1]]
        else:
            assert arg in self.var.keys(), 'You use a variable {} which is not defined before'.format(arg)
            return self.read_var(arg)

    def math(self, ins: Instruction, opr):
        self.alu.put_right(self.addressing(ins))
        self.alu.put_left(self.data_path.get_value_register("AC"))
        self.tick_tick()
        if opr == ALU.div:
            # result ->　AC
            r = self.alu.act(opr)
            self.data_path.set_value_register("AC", r)
            self.tick_tick()
        else:
            # result ->　AC
            result = self.alu.act(opr)
            self.data_path.set_value_register("AC", result)
            self.tick_tick()

    def set_nzvc(self, var: int):
        self.alu.nzvc = var

    def get_nzvc(self):
        return self.alu.nzvc

    def ins_execute(self, ins: Instruction, position: str) -> int:
        if ins.instruction == Opcode['HLT']:
            return 1
        # for math instr
        elif ins.instruction in MATH_INSTRUCTION:
            if ins.instruction == Opcode['ADD']:
                self.math(ins, ALU.add)
                self.data_path.set_value_register("PS", self.get_nzvc())
            elif ins.instruction == Opcode['SUB']:
                self.math(ins, ALU.min)
                self.data_path.set_value_register("PS", self.get_nzvc())
            elif ins.instruction == Opcode['MUL']:
                self.math(ins, ALU.mul)
            elif ins.instruction == Opcode['DIV']:
                self.math(ins, ALU.div)
            elif ins.instruction == Opcode['INV']:
                # -AC->AC, nzvc -> PS
                self.alu.put_left(self.data_path.get_value_register("AC"))
                self.tick_tick()
                self.data_path.set_value_register("AC", self.alu.act(ALU.inversion))
                self.set_nzvc(Z)
                self.data_path.set_value_register("PS", self.get_nzvc())
                self.tick_tick()
            # CMP
            else:
                self.alu.put_right(self.addressing(ins))
                # AC - arg0 to check nzvc -> PS
                self.alu.put_left(self.data_path.get_value_register("AC"))
                self.alu.act(ALU.min)
                self.data_path.set_value_register("PS", self.get_nzvc())
                self.tick_tick()
        # for data instr
        elif ins.instruction in DATA_INSTRUCTION:
            arg0 = ins.args[0]  # REG0, var, number
            arg1 = ins.args[1]  # REG1, var, number
            if ins.instruction == Opcode['MOV']:
                if arg0 != 'INPUT' or arg0 != 'OUTPUT' or arg1 != 'INPUT' or arg1 != 'OUTPUT':
                    # REG1 -> REG0
                    if arg0 in RegisterType.__members__ and arg1 in RegisterType.__members__:
                        self.data_path.set_value_register(arg0, self.data_path.get_value_register(arg1))
                        self.tick_tick()
                    # arg1 -> REG0
                    elif arg0 in RegisterType.__members__ and arg1 not in RegisterType.__members__:
                        self.data_path.set_value_register(arg0, self.addressing_arg(arg1))
                        self.tick_tick()
                    # REG1 -> arg0
                    elif arg0 not in RegisterType.__members__ and arg1 in RegisterType.__members__:
                        assert (arg0 in self.var.keys() or
                                is_match("^[1-9][0-9]*", arg0)), 'You have to declare where you want to save the value by declaring a variable or address'
                        # arg0 ->　AR
                        if arg0 in self.var.keys():  # if arg0 is var
                            self.data_path.set_value_register("AR", self.var[arg0])
                        else:  # if arg0 is number
                            self.data_path.set_value_register("AR", int(arg0))

                        # REG1 -> [AR]
                        self.data_path.set_value_memory(self.data_path.get_value_register("AR"),
                                                        self.data_path.get_value_register(arg1))
                        self.tick_tick()
                    # arg1 -> arg0
                    elif arg0 not in RegisterType.__members__ and arg1 not in RegisterType.__members__:
                        if arg0 in self.var.keys():  # if arg0 is var
                            self.data_path.set_value_register("AR", self.var[arg0])
                        else:  # if arg0 is number
                            self.data_path.set_value_register("AR", int(arg0))
                        if arg1 in self.var.keys():  # if arg1 is var
                            self.data_path.set_value_register("AR", self.var[arg1])
                        else:  # if arg0 is number
                            self.data_path.set_value_register("AR", int(arg1))

                        self.tick_tick()

            elif ins.instruction == Opcode['LD']:
                assert arg0 != 'OUTPUT', 'Instruction LD can\'t call OUTPUT'
                if arg0 != 'INPUT':
                    # arg0 -> AC
                    self.data_path.set_value_register('AC', self.addressing(ins))
                    self.tick_tick()
                elif arg0 == 'INPUT':
                    # index -> AR， io->ac
                    assert self.data_path.output_index < self.data_path.size, 'Read input out of range!'
                    self.data_path.set_value_register("AR", self.data_path.output_index)
                    self.data_path.output_index += 1
                    self.tick_tick()
                    self.data_path.set_value_register("AC",
                                                      self.data_path.memory[
                                                          self.data_path.get_value_register('AR')].value)
                    self.tick_tick()
            # ST
            else:
                assert arg0 != 'INPUT', 'Instruction ST can\'t call input'
                if arg0 != 'OUTPUT':

                    assert (arg0 in self.var.keys() or
                            is_match("^[1-9][0-9]*", arg0)), 'You have to declare where you want to save the value by declaring a variable or address'
                    # arg0 ->　AR
                    if arg0 in self.var.keys():
                        self.alu.put_right(self.var[arg0])
                    else:
                        self.alu.put_right(int(arg0))
                    self.data_path.set_value_register("AR", self.alu.act(ALU.or_operation))
                    # AC -> [AR]
                    self.data_path.set_value_memory(self.data_path.get_value_register("AR"),
                                                    self.data_path.get_value_register("AC"))
                    self.tick_tick()
                else:
                    # AC -> output_buffer
                    self.data_path.output_buffer.buf[
                        self.data_path.output_buffer.write_pointer] = self.data_path.get_value_register('AC')
                    self.data_path.output_buffer.write_pointer += 1
                    self.tick_tick()
        elif ins.instruction in STACK_INSTRUCTION:
            if ins.instruction == Opcode.PUSH:
                # SP-1 -> SP
                self.data_path.set_value_register('SP', self.data_path.get_value_register('SP') - 1)
                self.tick_tick()
                # AC -> STACK[SP]
                self.data_path.stack[self.data_path.get_value_register("SP")] = self.data_path.get_value_register("AC")
                self.tick_tick()
            else:
                # [SP] -> AC
                self.data_path.set_value_register("AC", self.data_path.stack[self.data_path.get_value_register("SP")])
                self.tick_tick()
                # SP + 1 -> SP
                self.data_path.set_value_register('SP', self.data_path.get_value_register('SP') - 1)
                self.tick_tick()
        else:
            if ins.instruction == Opcode.JMP:
                # Decoder -> IP
                arg0 = ins.args[0]
                assert arg0 in self.fun[
                    position].keys(), "You are trying jump to a label which is not in his own function"
                self.data_path.set_value_register("IP", self.fun[position][arg0])
                self.tick_tick()
            elif ins.instruction == Opcode.CALL:
                # AC->BR save parameter
                self.alu.put_left(self.data_path.get_value_register('AC'))
                self.data_path.set_value_register("BR", self.alu.act(ALU.or_operation))
                self.tick_tick()
                # IP ->　AC
                arg0 = ins.args[0]
                assert arg0 in self.fun.keys(), "You are trying call a not existed function"
                self.alu.put_right(self.data_path.get_value_register('IP'))
                self.data_path.set_value_register("AC", self.alu.act(ALU.or_operation))
                self.tick_tick()
                # push
                new_ins = Instruction(Opcode.PUSH, [])
                self.ins_execute(new_ins, position)
                # Decoder -> IP
                self.data_path.set_value_register("IP", self.fun[arg0]['self'])
                self.position.append(arg0)
                self.tick_tick()
                # BR->AC save parameter
                self.alu.put_left(self.data_path.get_value_register('BR'))
                self.data_path.set_value_register("AC", self.alu.act(ALU.or_operation))
                self.tick_tick()
            elif ins.instruction == Opcode.RET:
                # AC->BR make sure that result of function is saved
                self.data_path.set_value_register("BR", self.data_path.get_value_register("AC"))
                self.tick_tick()
                # pop
                new_ins = Instruction(Opcode.POP, [])
                self.ins_execute(new_ins, self.position[-1])
                self.position.pop()
                # AC -> IP
                self.alu.put_left(self.data_path.get_value_register("AC"))
                self.data_path.set_value_register("IP", self.alu.act(ALU.or_operation))
                self.tick_tick()
                # BR->AC
                self.data_path.set_value_register("AC", self.data_path.get_value_register("BR"))
                self.tick_tick()
            elif ins.instruction == Opcode.JZ:
                if self.data_path.get_value_register("PS") | Z == Z and self.data_path.get_value_register("PS") != 0:
                    ins_2 = Instruction(Opcode.JMP, args=ins.args)
                    self.ins_execute(ins_2, position)
            elif ins.instruction == Opcode.JS:
                if self.data_path.get_value_register("PS") | N == N and self.data_path.get_value_register("PS") != 0:
                    ins_2 = Instruction(Opcode.JMP, args=ins.args)
                    self.ins_execute(ins_2, position)
            # JNZ
            else:
                if self.data_path.get_value_register("PS") != Z:
                    ins_2 = Instruction(Opcode.JMP, args=ins.args)
                    self.ins_execute(ins_2, position)
        return 0

    def run_ins(self, position: str) -> int:
        ins: Instruction
        self.read_ins()
        ins = self.data_path.get_value_register("IR")
        result = self.ins_execute(ins, position)

        self.ic_count()
        print("DEBUG:machine:{ ", end="")
        print("IC:{}".format(self.ic), end=", ")
        print("Tick:{}".format(self.tick), end=", ")
        self.data_path.print_registers()
        print(" }", end="  ")
        print(ins.to_string())
        return result

    def run(self):
        head_instr = '_START'  # set the start position of program
        self.position.append(head_instr)
        while True:
            r = self.run_ins(position=self.position[-1])
            if r == 1:
                break
        print("Output:")
        first = True
        output_result = True
        result = ""
        for i in self.data_path.output_buffer.buf:
            if first:
                first = False
                if i == -1:
                    output_result = False
            if i != -1:
                print(de_char[i], end="")
                result = result + de_char[i]
            else:
                break
        print()
        if output_result:
            return result
        else:
            return str(self.data_path.get_value_register("AC"))


def start(sourcefile, input_file):
    program = read_code(sourcefile)  # get program from machine code
    data_path = DataPath(256, input_file)  # initialize data path
    cpu = CPU(program=program, data_path=data_path)  # initialize cpu
    cpu.decode()
    out = cpu.run()  # run program
    return out


if __name__ == "__main__":
    import sys

    assert len(sys.argv) == 3, 'Please only input the name of one file after compiling'
    start(sys.argv[1], sys.argv[2])
