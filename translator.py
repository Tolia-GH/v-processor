import re
import sys
from enum import unique, Enum

from ISA import InstructionType, NO_ARGUMENT


@unique
class Section(Enum):
    DATA = 1
    TEXT = 2


def is_match(re_exp: str, string: str) -> bool:
    return bool(re.search(re_exp, string))


def is_valid_variable(line: str) -> bool:
    if (
            is_match("^.*: *0 *$", line) or
            is_match("^.*: *[1-9]+[0-9]* *$", line) or
            is_match("^.*: *\".*\" *, *[1-9]+[0-9]* *$", line) or
            is_match("^.*: *\".*\" *$", line)
    ):
        return True
    else:
        return False


def read_variable(line: str) -> tuple[str, str]:
    assert is_valid_variable(line), "Illegal variable {}".format(line)

    key = line.split(":", 1)[0]
    value = line.split(":", 1)[1]
    if is_match("^.*: *-?[1-9]+[0-9]* *$", line):  # number
        key = re.findall("\S*", key)[0]
        value = re.findall("-?[1-9]+[0-9]*", value)[0]
    elif is_match("^.*: *0 *$", line):
        key = re.findall("\S*", key)[0]
        value = '0'
    elif is_match("^.*: *\".*\" *$", line):  # string
        keys = re.findall("\S*", key)
        key = keys[0]
        value = re.findall("\".*\"", value)[0]
        value = value + "," + str(len(value) - 2)
    else:
        keys = re.findall("\S*", key)
        key = keys[0]
        values = value.rsplit(',', 1)
        left = values[0].rsplit("\"", 1)
        a = left[0] + "\""
        b = re.sub(r" ", "", values[1])
        value = a + "," + b
    return key, value


def init_line(line: str) -> str:
    line = line.split(";")[0]
    line = line.strip()
    line = re.sub(r"\t+", "", line)
    line = re.sub(r"\n", "", line)
    return line


def translate(source_name: str, target_name: str):
    result = ""
    variable = dict()
    function_point = dict()  # functions
    label_in_fun = dict()
    instruction_index = 0
    index = 0
    last_fun = ""

    section = Section.DATA
    is_first_fun = True

    lines_source = open(source_name).read().split('\n')

    # read each line of source file
    while index < len(lines_source):
        line = init_line(lines_source[index])  # read new line
        index += 1

        if line == "" or line == "\n":  # skip empty line
            continue
        if line.upper() == "SECTION .DATA":
            section = Section.DATA
            continue
        if line.upper() == "SECTION .TEXT":
            section = Section.TEXT
            continue

        # read section data
        if section == Section.DATA:
            key, value = read_variable(line)
            key = key.upper()
            assert key != 'INPUT' and key != 'OUTPUT', "Line {}:You can't declare a variable name as INPUT or OUTPUT".format(
                index)
            assert key not in variable.keys(), "Line {}:You can't declare a variable two or more times".format(index)
            variable[key] = value

        # read section text
        if section == Section.TEXT:
            # handle function or label
            if is_match("^\S*:$", line):
                line = line.upper()
                # function
                if is_match("^\.\S*:$", line):
                    line = line.replace(":", "")
                    label_in_fun[last_fun][line] = instruction_index
                # label
                else:
                    line = line.replace(":", "")
                    function_point[line] = instruction_index
                    label_in_fun[line] = dict()
                    last_fun = line
                    if is_first_fun:
                        assert last_fun == '_START', 'Your first function should be _start'
                        is_first_fun = False
            # handle normal instruction
            else:
                line = re.sub(r" +", " ", line)
                split = line.split(" ")
                split[0] = split[0].upper()
                assert split[0] in InstructionType.__members__, "Line {}, no such instrument".format(index)
                if InstructionType[split[0]] in NO_ARGUMENT:
                    assert len(split) == 1, "Line {}, this instrument have no argument".format(index)
                else:
                    assert len(split) == 2, "Line {}, only one argument allowed".format(index)
                if line != "":
                    if len(split) == 2:
                        if not is_match("^\'[A-Za-z]{1}\'$", split[1]):
                            split[1] = split[1].upper()
                        result = result + str(instruction_index) + " " + InstructionType[split[0]].value + " " + \
                                 split[1] + " " + "\n"
                    else:
                        result = result + str(instruction_index) + " " + InstructionType[
                            split[0]].value + " " + "\n"
                    instruction_index += 1

    # write target file
    with open(target_name, "w") as f:
        f.write(result)
        f.write("FUNCTION\n")
        for i in function_point:
            line = i + ":" + str(function_point[i]) + "\n"
            f.write(line)
        f.write("LABEL\n")
        for i in label_in_fun:
            for k in label_in_fun[i]:
                line = i + ":" + k + ":" + str(label_in_fun[i][k]) + "\n"
                f.write(line)
        f.write("VARIABLE\n")
        for i in variable:
            line = i + ":" + variable[i] + "\n"
            f.write(line)
    with open(target_name, "r") as f:
        index = 0
        while index < instruction_index:
            index += 1
            line = f.readline()
            line = init_line(line)
            term = line.split(" ")[1:]
            while "" in term:
                term.remove("")
            print(term)
            # a = check_ins(term, label_in_fun,function_point,index - 1),\
            #    "Input illegal instruction or parameter".format(index)

    # print(result)


if __name__ == "__main__":
    assert len(sys.argv) == 3, 'Please only input the name of source file and target file'
    _, source, target = sys.argv
    translate(source, target)
