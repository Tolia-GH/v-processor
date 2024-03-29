import re
from enum import Enum, unique


@unique
class RegisterType(Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    IP = "IP"  # 计数
    BR = "BR"  # 缓存，例如用于存储除法的余数等等
    AC = "AC"  # 结果储存
    PS = "PS"  # NZVC
    SP = "SP"  # 堆栈
    AR = "AR"  # 地址

    IR = "IR"


@unique
class Opcode(Enum):
    # math
    ADD = "ADD"  # ADD REG1, REG2: REG1 = REG1 + REG2
    SUB = "SUB"  # SUB REG1, REG2: REG1 = REG1 - REG2
    MUL = "MUL"  # MUL REG1, REG2: REG1 = REG1 * REG2
    DIV = "DIV"  # DIV REG1, REG2: REG1 = REG1 / REG2
    XOR = "XOR"  # XOR REG1, REG2: REG1 = REG1 xor REG2
    MOD = "MOD"  # MOD REG1, REG2: REG1 = REG1 % REG2
    CMP = "CMP"  # CMP REG1, REG2: NZVC = REG1 - REG2
    INV = "INV"  # INV REG: REG = REG + 1
    DEC = "DEC"  # DEC REG: REG = REG - 1

    # data control
    MOV = 'MOV'  # MOV REG1, REG2: REG1 = REG2
    LD = 'LD'  # LD REG: AC = REG
    ST = 'ST'  # ST REG: REG = AC
    IN = 'IN'  # IN
    OUT = 'OUT'  # OUT

    # stack
    PUSH = "PUSH"  # PUSH REG: stack(SP) = REG, SP - 1
    POP = "POP"  # POP REG: REG = stack(SP), SP + 1

    # jump
    JMP = "JMP"  # JMP LABEL: IP = (LABEL)
    JE = "JE"
    JNE = "JNE"
    JZ = "JZ"
    JNZ = "JNZ"
    JL = "JL"
    JLE = "JLE"
    JG = "JG"
    JGE = "JGE"
    CALL = "CALL"
    RET = "RET"

    # STOP
    HLT = "HLT"


MATH_INSTRUCTION = (
    Opcode.ADD, Opcode.SUB, Opcode.MUL,
    Opcode.DIV, Opcode.XOR, Opcode.MOD,
    Opcode.CMP, Opcode.INV, Opcode.DEC
)
DATA_INSTRUCTION = (
    Opcode.MOV, Opcode.LD, Opcode.ST,
    Opcode.IN, Opcode.OUT
)
STACK_INSTRUCTION = (
    Opcode.POP, Opcode.PUSH
)
JUMP_INSTRUCTION = (
    Opcode.JMP, Opcode.JE, Opcode.JNE,
    Opcode.JZ, Opcode.JNZ, Opcode.JL,
    Opcode.JLE, Opcode.JG, Opcode.JGE,
    Opcode.CALL, Opcode.RET
)

NO_ARGUMENT = (
    Opcode.HLT, Opcode.IN, Opcode.OUT,
    Opcode.RET
)
ONE_ARGUMENT = (
    Opcode.INV, Opcode.DEC, Opcode.LD,
    Opcode.ST, Opcode.POP, Opcode.PUSH,
    Opcode.JMP, Opcode.JE, Opcode.JNE,
    Opcode.JZ, Opcode.JNZ, Opcode.JL,
    Opcode.JLE, Opcode.JG, Opcode.JGE,
    Opcode.CALL,
)
TWO_ARGUMENT = (
    Opcode.ADD, Opcode.SUB, Opcode.MUL,
    Opcode.DIV, Opcode.XOR, Opcode.MOD,
    Opcode.CMP, Opcode.MOV,
)


class Instruction:
    def __init__(self, instruction: Opcode, args: []):
        self.instruction = instruction
        self.args = args

    def to_string(self) -> str:
        result = ""
        result = result + self.instruction.value
        k = 0
        for i in self.args:
            if k == 0:
                result = result + " " + i
                k += 1
            else:
                result = result + " " + i
        return result


@unique
class CodeType(Enum):
    INS = 1  # instructions
    FUN = 2  # Function
    LAB = 3  # label
    VAR = 4  # variable


def read_code(filename: str) -> {}:
    program = {'Instruction': [], 'Variable': {}, 'Function': {}}
    code_type = CodeType.INS

    index = 0
    lines_file = open(filename).read().split('\n')

    # assert line != "", "You open a file, whose format is not property"
    while index < len(lines_file):
        line = lines_file[index]
        index += 1

        if line == "":
            continue
        if line == "FUNCTION":
            code_type = CodeType.FUN
        elif line == "LABEL":
            code_type = CodeType.LAB
        elif line == "VARIABLE":
            code_type = CodeType.VAR
        else:
            ins: Instruction
            if code_type == CodeType.INS:
                term = line.split(" ")
                ins_type = Opcode[term[1]]  # get opcode
                while "" in term:
                    term.remove("")
                if term[1] == 'HLT':
                    ins = Instruction(ins_type, [])
                else:
                    ins = Instruction(ins_type, term[2:])
                program['Instruction'].append(ins)
            elif code_type == CodeType.FUN:
                term = line.split(":")
                while "" in term:
                    term.remove("")
                program['Function'][term[0]] = dict()
                program['Function'][term[0]]['self'] = int(term[1])
            elif code_type == CodeType.LAB:
                term = line.split(":")
                while "" in term:
                    term.remove("")
                program['Function'][term[0]][term[1]] = int(term[2])
            elif code_type == CodeType.VAR:
                term = line.split(":", 1)
                while "" in term:
                    term.remove("")
                program['Variable'][term[0]] = term[1]

    return program


def is_match(re_exp: str, string: str) -> bool:
    return bool(re.search(re_exp, string))


char = {
    ' ': 0, 'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10,
    'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21,
    'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26, 'A': 27, 'B': 28, 'C': 29, 'D': 30, 'E': 31, 'F': 32,
    'G': 33, 'H': 34, 'I': 35, 'J': 36, 'K': 37, 'L': 38, 'M': 39, 'N': 40, 'O': 41, 'P': 42, 'Q': 43,
    'R': 44, 'S': 45, 'T': 46, 'U': 47, 'V': 48, 'W': 49, 'X': 50, 'Y': 51, 'Z': 52, '': 53, '0': 54,
    '1': 55, '2': 56, '3': 57, '4': 58, '5': 59, '6': 60, '7': 61, '8': 62, '9': 63, '!': 64, ',': 65,
    '.': 66, '-': 67, '*': 68, '?': 69, '+': 70, '/': 71, '@': 72, '\0': 73, '\n': 74,
}
de_char = {
    0: ' ', 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j',
    11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u',
    22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z', 27: 'A', 28: 'B', 29: 'C', 30: 'D', 31: 'E', 32: 'F',
    33: 'G', 34: 'H', 35: 'I', 36: 'J', 37: 'K', 38: 'L', 39: 'M', 40: 'N', 41: 'O', 42: 'P', 43: 'Q',
    44: 'R', 45: 'S', 46: 'T', 47: 'U', 48: 'V', 49: 'W', 50: 'X', 51: 'Y', 52: 'Z', 53: '', 54: '0',
    55: '1', 56: '2', 57: '3', 58: '4', 59: '5', 60: '6', 61: '7', 62: '8', 63: '9', 64: '!', 65: ',',
    66: '.', 67: '-', 68: '*', 69: '?', 70: '+', 71: '/', 72: '@', 73: '\0', 74: '\n'
}


def get_char(i: int):
    return char[i]


def char_var(i: str):
    assert len(i) == 1, 'Function char_var() is used to translate only one char to it\'s value'
    return de_char[i]
