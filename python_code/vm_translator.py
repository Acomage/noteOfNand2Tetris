import argparse
import os

file_path = ""
function_current = "WarningNotInAFunction"


def set_file_path(path: str) -> None:
    global file_path
    file_path = path


def get_file_path() -> str:
    global file_path
    return file_path


def set_function_current(function_name: str) -> None:
    global function_current
    function_current = function_name


def get_function_current() -> str:
    global function_current
    return function_current


class Instruction:
    def to_asm(self) -> list[str]:
        raise NotImplementedError("Subclasses should implement this method")


class ArithmeticLogicalInstruction(Instruction):
    num_eq = -1
    num_gt = -1
    num_lt = -1

    def __init__(self, operation: str) -> None:
        self.operation = operation

    def __repr__(self) -> str:
        return self.operation

    def to_asm(self) -> list[str]:
        match self.operation:
            case "add":
                return [
                    "//add",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "M=D+M",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "sub":
                return [
                    "//sub",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "M=M-D",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "neg":
                return ["//neg", "@SP", "AM=M-1", "M=-M", "@SP", "M=M+1", ""]

            case "eq":
                ArithmeticLogicalInstruction.num_eq += 1
                return [
                    "//eq",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "D=D-M",
                    f"@EQ_TRUE.{ArithmeticLogicalInstruction.num_eq}",
                    "D;JEQ",
                    "@SP",
                    "A=M",
                    "M=0",
                    f"@EQ_END.{ArithmeticLogicalInstruction.num_eq}",
                    "0;JMP",
                    f"(EQ_TRUE.{ArithmeticLogicalInstruction.num_eq})",
                    "@SP",
                    "A=M",
                    "M=-1",
                    f"(EQ_END.{ArithmeticLogicalInstruction.num_eq})",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "gt":
                ArithmeticLogicalInstruction.num_gt += 1
                return [
                    "//gt",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "D=M-D",
                    f"@GT_TRUE.{ArithmeticLogicalInstruction.num_gt}",
                    "D;JGT",
                    "@SP",
                    "A=M",
                    "M=0",
                    f"@GT_END.{ArithmeticLogicalInstruction.num_gt}",
                    "0;JMP",
                    f"(GT_TRUE.{ArithmeticLogicalInstruction.num_gt})",
                    "@SP",
                    "A=M",
                    "M=-1",
                    f"(GT_END.{ArithmeticLogicalInstruction.num_gt})",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "lt":
                ArithmeticLogicalInstruction.num_lt += 1
                return [
                    "//lt",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "D=M-D",
                    f"@LT_TRUE.{ArithmeticLogicalInstruction.num_lt}",
                    "D;JLT",
                    "@SP",
                    "A=M",
                    "M=0",
                    f"@LT_END.{ArithmeticLogicalInstruction.num_lt}",
                    "0;JMP",
                    f"(LT_TRUE.{ArithmeticLogicalInstruction.num_lt})",
                    "@SP",
                    "A=M",
                    "M=-1",
                    f"(LT_END.{ArithmeticLogicalInstruction.num_lt})",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "and":
                return [
                    "//and",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "M=D&M",
                    "@SP",
                    "M=M+1",
                    "",
                ]

            case "or":
                return [
                    "//or",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@SP",
                    "AM=M-1",
                    "M=D|M",
                    "@SP",
                    "M=M+1",
                    "",
                ]
            case "not":
                return ["//not", "@SP", "AM=M-1", "M=!M", "@SP", "M=M+1", ""]
            case _:
                raise ValueError(f"Unknown arithmetic operation: {self.operation}")


class PushPopInstruction(Instruction):
    def __init__(self, command: str, segment: str, index: int) -> None:
        self.command = command
        self.segment = segment
        self.index = index

    def __repr__(self) -> str:
        return f"{self.command} {self.segment} {self.index}"

    def to_asm(self) -> list[str]:
        if self.segment in ["local", "argument", "this", "that"]:
            segment_base = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
            }[self.segment]
            if self.command == "push":
                return [
                    f"//push {self.segment} {self.index}",
                    f"@{segment_base}",
                    "D=M",
                    f"@{self.index}",
                    "A=D+A",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                    "",
                ]
            else:
                return [
                    f"//pop {self.segment} {self.index}",
                    f"@{segment_base}",
                    "D=M",
                    f"@{self.index}",
                    "D=D+A",
                    "@R13",
                    "M=D",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "@R13",
                    "A=M",
                    "M=D",
                    "",
                ]
        elif self.segment == "constant":
            return [
                f"//push constant {self.index}",
                f"@{self.index}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "",
            ]
        elif self.segment == "static":
            file_name = get_file_path().split("/")[-1].split(".")[0]
            if self.command == "push":
                return [
                    f"//push static {self.index}",
                    f"@{file_name}.{self.index}",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                    "",
                ]
            else:
                return [
                    f"//pop static {self.index}",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    f"@{file_name}.{self.index}",
                    "M=D",
                    "",
                ]
        else:
            base_address = 5 if self.segment == "temp" else 3
            if self.command == "push":
                return [
                    f"//push {self.segment} {self.index}",
                    f"@{base_address + self.index}",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                    "",
                ]
            else:
                return [
                    f"//pop {self.segment} {self.index}",
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    f"@{base_address + self.index}",
                    "M=D",
                    "",
                ]


class BranchingInstruction(Instruction):
    def __init__(self, command: str, label: str) -> None:
        self.command = command
        self.label = label

    def __repr__(self) -> str:
        return f"{self.command} {self.label}"

    def to_asm(self) -> list[str]:
        function_current = get_function_current()
        if self.command == "label":
            return [
                f"//label {self.label}",
                f"({function_current}${self.label})",
                "",
            ]
        elif self.command == "goto":
            return [
                f"//goto {self.label}",
                f"@{function_current}${self.label}",
                "0;JMP",
                "",
            ]
        elif self.command == "if-goto":
            return [
                f"//if-goto {self.label}",
                "@SP",
                "AM=M-1",
                "D=M",
                f"@{function_current}${self.label}",
                "D;JNE",
                "",
            ]
        else:
            raise ValueError(f"Unknown branching command: {self.command}")


class FunctionInstruction(Instruction):
    current_function_call_num = 0

    def __init__(
        self, command: str, function_name: str = "", num_args: int = 0
    ) -> None:
        self.command = command
        self.function_name = function_name
        self.num_args = num_args

    def __repr__(self) -> str:
        if self.command == "return":
            return "return"
        else:
            return f"{self.command} {self.function_name} {self.num_args}"

    def to_asm(self) -> list[str]:
        if self.command == "function":
            set_function_current(self.function_name)
            asm_lines = [
                f"//function {self.function_name} {self.num_args}",
                f"({self.function_name})",
            ]
            for _ in range(self.num_args):
                asm_lines.extend(
                    [
                        "@SP",
                        "A=M",
                        "M=0",
                        "@SP",
                        "M=M+1",
                        "",
                    ]
                )
            return asm_lines
        elif self.command == "call":
            i = FunctionInstruction.current_function_call_num
            FunctionInstruction.current_function_call_num += 1
            function_current = get_function_current()
            return [
                f"//call {self.function_name} {self.num_args}",
                f"@{function_current}$ret.{i}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@LCL",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@ARG",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@THIS",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                "@THAT",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                f"@{self.num_args + 5}",
                "D=A",
                "@SP",
                "D=M-D",
                "@ARG",
                "M=D",
                "@SP",
                "D=M",
                "@LCL",
                "M=D",
                f"@{self.function_name}",
                "0;JMP",
                f"({function_current}$ret.{i})",
                "",
            ]
        elif self.command == "return":
            FunctionInstruction.current_function_call_num = 0
            return [
                "//return",
                "@LCL",
                "D=M",
                "@R13",
                "M=D",
                "@5",
                "A=D-A",
                "D=M",
                "@R14",
                "M=D",
                "@SP",
                "A=M-1",
                "D=M",
                "@ARG",
                "A=M",
                "M=D",
                "D=A+1",
                "@SP",
                "M=D",
                "@R13",
                "AM=M-1",
                "D=M",
                "@THAT",
                "M=D",
                "@R13",
                "AM=M-1",
                "D=M",
                "@THIS",
                "M=D",
                "@R13",
                "AM=M-1",
                "D=M",
                "@ARG",
                "M=D",
                "@R13",
                "AM=M-1",
                "D=M",
                "@LCL",
                "M=D",
                "@R14",
                "A=M",
                "0;JMP",
                "",
            ]
        else:
            raise ValueError(f"Unknown function command: {self.command}")


class VMTranslator:
    def __init__(self, vm_code: str) -> None:
        self.instructions = [self.str_to_instruction(ins) for ins in self.cut(vm_code)]
        self.asm = []
        for ins in self.instructions:
            asm_lines = ins.to_asm()
            self.asm.extend(asm_lines)

    def cut(self, vm_code: str) -> list[str]:
        instructions = []
        instruction_current = ""
        iscomment = False
        meetaslash = False
        for char in vm_code:
            if char == "\n":
                instruction_current = instruction_current.strip()
                if instruction_current != "":
                    instructions.append(instruction_current)
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
        instruction_current = instruction_current.strip()
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
        elif (
            instruction.startswith("label")
            or instruction.startswith("goto")
            or instruction.startswith("if-goto")
        ):
            parts = instruction.split()
            command = parts[0]
            label = parts[1]
            return BranchingInstruction(command, label)
        elif (
            instruction.startswith("function")
            or instruction.startswith("call")
            or instruction == "return"
        ):
            parts = instruction.split()
            command = parts[0]
            if command == "return":
                return FunctionInstruction(command)
            else:
                function_name = parts[1]
                num_args = int(parts[2]) if len(parts) > 2 else 0
                return FunctionInstruction(command, function_name, num_args)
        else:
            raise ValueError(
                f"Unknown VM instruction: {instruction} in {get_file_path()}"
            )


def main():
    parser = argparse.ArgumentParser(description="VM to ASM Translator")
    parser.add_argument("inputpath", help="Path to the file or dir to read")
    parser.add_argument("-o", help="Output file path")
    args = parser.parse_args()
    inputpath = args.inputpath
    if not os.path.exists(inputpath):
        raise FileNotFoundError(f"Input path does not exist: {inputpath}")
    elif os.path.isdir(inputpath):
        if args.o:
            output_path = args.o
        else:
            dir_name = os.path.basename(os.path.normpath(inputpath))
            parent_dir = os.path.dirname(os.path.normpath(inputpath))
            output_path = os.path.join(parent_dir, dir_name + ".asm")
        with open(output_path, "w") as f:
            f.write("// Translated by VMTranslator\n")
            f.write("// Input directory: " + inputpath + "\n")
            f.write("\n")
            f.write("@256\n")
            f.write("D=A\n")
            f.write("@SP\n")
            f.write("M=D\n")
            # call function Sys.init
            initCall = FunctionInstruction("call", "Sys.init", 0)
            for line in initCall.to_asm():
                f.write(line + "\n")
        for file_name in os.listdir(inputpath):
            if file_name.endswith(".vm"):
                set_file_path(os.path.join(inputpath, file_name))
                set_function_current("WarningNotInAFunction")
                with open(os.path.join(inputpath, file_name), "r") as f:
                    content = f.read()
                vm_translator = VMTranslator(content)
                with open(output_path, "a") as f:
                    for line in vm_translator.asm:
                        f.write(line + "\n")
    else:
        set_file_path(args.inputpath)
        with open(args.inputpath, "r") as f:
            content = f.read()
        vm_translator = VMTranslator(content)
        if args.o:
            output_path = args.o
        else:
            base, _ = os.path.splitext(args.inputpath)
            output_path = base + ".asm"
        with open(output_path, "w") as f:
            for line in vm_translator.asm:
                f.write(line + "\n")


if __name__ == "__main__":
    main()
