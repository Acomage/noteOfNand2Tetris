import argparse

file_path = ""


def set_file_path(path: str) -> None:
    global file_path
    file_path = path


def get_file_path() -> str:
    global file_path
    return file_path


class Instruction:
    def to_asm(self) -> str:
        raise NotImplementedError("Subclasses should implement this method")


class ArithmeticLogicalInstruction(Instruction):
    num_eq = -1
    num_gt = -1
    num_lt = -1

    def __init__(self, operation: str) -> None:
        self.operation = operation

    def __repr__(self) -> str:
        return self.operation

    def to_asm(self) -> str:
        match self.operation:
            case "add":
                return """//add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D+M
@SP
M=M+1
"""

            case "sub":
                return """//sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
"""

            case "neg":
                return """//neg
@SP
M=M-1
A=M
M=-M
@SP
M=M+1
"""

            case "eq":
                ArithmeticLogicalInstruction.num_eq += 1
                return f"""//eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=D-M
@EQ_TRUE.{ArithmeticLogicalInstruction.num_eq}
D;JEQ
@SP
A=M
M=0
@EQ_END.{ArithmeticLogicalInstruction.num_eq}
0;JMP
(EQ_TRUE.{ArithmeticLogicalInstruction.num_eq})
@SP
A=M
M=-1
(EQ_END.{ArithmeticLogicalInstruction.num_eq})
@SP
M=M+1"""

            case "gt":
                ArithmeticLogicalInstruction.num_gt += 1
                return f"""//gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@GT_TRUE.{ArithmeticLogicalInstruction.num_gt}
D;JGT
@SP
A=M
M=0
@GT_END.{ArithmeticLogicalInstruction.num_gt}
0;JMP
(GT_TRUE.{ArithmeticLogicalInstruction.num_gt})
@SP
A=M
M=-1
(GT_END.{ArithmeticLogicalInstruction.num_gt})
@SP
M=M+1"""

            case "lt":
                ArithmeticLogicalInstruction.num_lt += 1
                return f"""//lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@LT_TRUE.{ArithmeticLogicalInstruction.num_lt}
D;JLT
@SP
A=M
M=0
@LT_END.{ArithmeticLogicalInstruction.num_lt}
0;JMP
(LT_TRUE.{ArithmeticLogicalInstruction.num_lt})
@SP
A=M
M=-1
(LT_END.{ArithmeticLogicalInstruction.num_lt})
@SP
M=M+1"""

            case "and":
                return """//and
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D&M
@SP
M=M+1"""

            case "or":
                return """//or
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D|M
@SP
M=M+1"""

            case "not":
                return """//not
@SP
M=M-1
A=M
M=!M
@SP
M=M+1"""
            case _:
                raise ValueError(f"Unknown arithmetic operation: {self.operation}")


class PushPopInstruction(Instruction):
    def __init__(self, command: str, segment: str, index: int) -> None:
        self.command = command
        self.segment = segment
        self.index = index

    def __repr__(self) -> str:
        return f"{self.command} {self.segment} {self.index}"

    def to_asm(self) -> str:
        if self.segment in ["local", "argument", "this", "that"]:
            segment_base = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
            }[self.segment]
            if self.command == "push":
                return f"""//push {self.segment} {self.index}
@{segment_base}
D=M
@{self.index}
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1"""
            else:
                return f"""//pop {self.segment} {self.index}
@{segment_base}
D=M
@{self.index}
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D"""
        elif self.segment == "constant":
            return f"""//push constant {self.index}
@{self.index}
D=A
@SP
A=M
M=D
@SP
M=M+1"""
        elif self.segment == "static":
            file_name = get_file_path().split("/")[-1].split(".")[0]
            if self.command == "push":
                return f"""//push static {self.index}
@{file_name}.{self.index}
D=M
@SP
A=M
M=D
@SP
M=M+1"""
            else:
                return f"""//pop static {self.index}
@SP
M=M-1
A=M
D=M
@{file_name}.{self.index}
M=D"""
        else:
            base_address = 5 if self.segment == "temp" else 3
            if self.command == "push":
                return f"""//push {self.segment} {self.index}
@{base_address + self.index}
D=M
@SP
A=M
M=D
@SP
M=M+1"""
            else:
                return f"""//pop {self.segment} {self.index}
@SP
M=M-1
A=M
D=M
@{base_address + self.index}
M=D"""


class BranchingInstruction(Instruction):
    pass


class FunctionInstruction(Instruction):
    pass


class VMTranslator:
    def __init__(self, vm_code: str) -> None:
        self.instructions = [self.str_to_instruction(ins) for ins in self.cut(vm_code)]
        self.asm = [ins.to_asm() for ins in self.instructions]

    def cut(self, vm_code: str) -> list[str]:
        instructions = []
        instruction_current = ""
        iscomment = False
        meetaslash = False
        for char in vm_code:
            if char == "\n":
                if instruction_current != "":
                    instructions.append(instruction_current.strip())
                    instruction_current = ""
                iscomment = False
            elif char == "/":
                if meetaslash:
                    iscomment = True
                    meetaslash = False
                else:
                    meetaslash = True
            else:
                if not iscomment:
                    instruction_current += char
        if instruction_current != "":
            instructions.append(instruction_current)
        return instructions

    def str_to_instruction(self, instruction: str) -> Instruction:
        if instruction in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return ArithmeticLogicalInstruction(instruction)
        elif instruction.startswith("push") or instruction.startswith("pop"):
            parts = instruction.split()
            command = parts[0]
            segment = parts[1]
            index = int(parts[2])
            return PushPopInstruction(command, segment, index)
        else:
            raise ValueError(f"Unknown VM instruction: {instruction}")


def main():
    parser = argparse.ArgumentParser(description="Read a file into a string.")
    parser.add_argument("filepath", help="Path to the file to read")
    parser.add_argument("-o", help="Output file path", default="output.asm")
    args = parser.parse_args()
    set_file_path(args.filepath)
    with open(args.filepath, "r") as f:
        content = f.read()
    vm_translator = VMTranslator(content)
    with open(args.o, "w") as f:
        for line in vm_translator.asm:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
