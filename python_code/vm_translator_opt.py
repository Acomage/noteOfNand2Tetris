import argparse
import os

file_path = ""
function_current = "WarningNotInAFunction"


eq_share = [
    "(Eq_share)",
    "@SP",
    "AM=M-1",
    "D=M",
    "A=A-1",
    "D=M-D",
    "M=-1",
    "@EQ_TRUE",
    "D;JEQ",
    "@SP",
    "A=M-1",
    "M=0",
    "(EQ_TRUE)",
    "@R15",
    "A=M",
    "0;JMP",
]
gt_share = [
    "(Gt_share)",
    "@SP",
    "AM=M-1",
    "D=M",
    "A=A-1",
    "D=M-D",
    "M=-1",
    "@GT_TRUE",
    "D;JGT",
    "@SP",
    "A=M-1",
    "M=0",
    "(GT_TRUE)",
    "@R15",
    "A=M",
    "0;JMP",
]
lt_share = [
    "(Lt_share)",
    "@SP",
    "AM=M-1",
    "D=M",
    "A=A-1",
    "D=M-D",
    "M=-1",
    "@LT_TRUE",
    "D;JLT",
    "@SP",
    "A=M-1",
    "M=0",
    "(LT_TRUE)",
    "@R15",
    "A=M",
    "0;JMP",
]
call_share = [
    "(Call_share)",
    "@R13",
    "D=M",
    "@SP",
    "A=M",
    "M=D",
    "@LCL",
    "D=M",
    "@SP",
    "AM=M+1",
    "M=D",
    "@ARG",
    "D=M",
    "@SP",
    "AM=M+1",
    "M=D",
    "@THIS",
    "D=M",
    "@SP",
    "AM=M+1",
    "M=D",
    "@THAT",
    "D=M",
    "@SP",
    "AM=M+1",
    "M=D",
    "@R14",
    "D=M",
    "@SP",
    "D=M-D",
    "@ARG",
    "M=D",
    "@SP",
    "MD=M+1",
    "@LCL",
    "M=D",
    "@R15",
    "A=M",
    "0;JMP",
]
return_share = [
    "(Return_share)",
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
]


def gen_Function_m_Local_share(m: int) -> list[str]:
    if m == 2:
        return [
            f"(Function{m}Local_share)",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=0",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=0",
            "@R15",
            "A=M",
            "0;JMP",
        ]
    else:
        return [
            f"(Function{m}Local_share)",
            f"@{m}",
            "D=A",
            f"(Function{m}Local_shareInitLoop)",
            f"@Function{m}Local_shareInitLoopEnd",
            "D=D-1;JLT",
            "@SP",
            "AM=M+1",
            "A=A-1",
            "M=0",
            f"@Function{m}Local_shareInitLoop",
            "0;JMP",
            f"(Function{m}Local_shareInitLoopEnd)",
            "@R15",
            "A=M",
            "0;JMP",
        ]


Function_Local_set = set()

function_Local_share = []


def deal_with_Function_Local_share(m: int) -> None:
    global function_Local_share
    global Function_Local_set
    if m not in Function_Local_set:
        Function_Local_set.add(m)
        function_Local_share.extend(gen_Function_m_Local_share(m))


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
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "A=A-1",
                    "M=D+M",
                ]

            case "sub":
                return [
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "A=A-1",
                    "M=M-D",
                ]

            case "neg":
                return ["@SP", "A=M-1", "M=-M"]

            case "eq":
                ArithmeticLogicalInstruction.num_eq += 1
                return [
                    f"@Eq_{ArithmeticLogicalInstruction.num_eq}",
                    "D=A",
                    "@R15",
                    "M=D",
                    "@Eq_share",
                    "0;JMP",
                    f"(Eq_{ArithmeticLogicalInstruction.num_eq})",
                ]

            case "gt":
                ArithmeticLogicalInstruction.num_gt += 1
                return [
                    f"@Gt_{ArithmeticLogicalInstruction.num_gt}",
                    "D=A",
                    "@R15",
                    "M=D",
                    "@Gt_share",
                    "0;JMP",
                    f"(Gt_{ArithmeticLogicalInstruction.num_gt})",
                ]

            case "lt":
                ArithmeticLogicalInstruction.num_lt += 1
                return [
                    f"@Lt_{ArithmeticLogicalInstruction.num_lt}",
                    "D=A",
                    "@R15",
                    "M=D",
                    "@Lt_share",
                    "0;JMP",
                    f"(Lt_{ArithmeticLogicalInstruction.num_lt})",
                ]

            case "and":
                return [
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "A=A-1",
                    "M=D&M",
                ]

            case "or":
                return [
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    "A=A-1",
                    "M=D|M",
                ]
            case "not":
                return ["@SP", "A=M-1", "M=!M"]
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
                    f"@{segment_base}",
                    "D=M",
                    f"@{self.index}",
                    "A=D+A",
                    "D=M",
                    "@SP",
                    "M=M+1",
                    "A=M-1",
                    "M=D",
                ]
            else:
                return [
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
                ]
        elif self.segment == "constant":
            return [
                f"@{self.index}",
                "D=A",
                "@SP",
                "M=M+1",
                "A=M-1",
                "M=D",
            ]
        elif self.segment == "static":
            file_name = get_file_path().split("/")[-1].split(".")[0]
            if self.command == "push":
                return [
                    f"@{file_name}.{self.index}",
                    "D=M",
                    "@SP",
                    "M=M+1",
                    "A=M-1",
                    "M=D",
                ]
            else:
                return [
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    f"@{file_name}.{self.index}",
                    "M=D",
                ]
        else:
            base_address = 5 if self.segment == "temp" else 3
            if self.command == "push":
                return [
                    f"@{base_address + self.index}",
                    "D=M",
                    "@SP",
                    "M=M+1",
                    "A=M-1",
                    "M=D",
                ]
            else:
                return [
                    "@SP",
                    "AM=M-1",
                    "D=M",
                    f"@{base_address + self.index}",
                    "M=D",
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
                f"({function_current}${self.label})",
            ]
        elif self.command == "goto":
            return [
                f"@{function_current}${self.label}",
                "0;JMP",
            ]
        elif self.command == "if-goto":
            return [
                "@SP",
                "AM=M-1",
                "D=M",
                f"@{function_current}${self.label}",
                "D;JNE",
            ]
        else:
            raise ValueError(f"Unknown branching command: {self.command}")


class FunctionInstruction(Instruction):
    current_function_call_num = 0
    call_num = -1
    function_define_num = -1

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
            if self.num_args == 0:
                return [
                    f"({self.function_name})",
                ]
            elif self.num_args == 1:
                return [
                    f"({self.function_name})",
                    "@SP",
                    "M=M+1",
                    "A=M-1",
                    "M=0",
                ]
            else:
                deal_with_Function_Local_share(self.num_args)
                FunctionInstruction.function_define_num += 1
                return [
                    f"({self.function_name})",
                    f"@FunctionLocal_share_{FunctionInstruction.function_define_num}",
                    "D=A",
                    "@R15",
                    "M=D",
                    f"@Function{self.num_args}Local_share",
                    "0;JMP",
                    f"(FunctionLocal_share_{FunctionInstruction.function_define_num})",
                ]
        elif self.command == "call":
            i = FunctionInstruction.current_function_call_num
            FunctionInstruction.current_function_call_num += 1
            FunctionInstruction.call_num += 1
            function_current = get_function_current()
            return [
                f"@{function_current}$ret.{i}",
                "D=A",
                "@R13",
                "M=D",
                f"@{self.num_args + 4}",
                "D=A",
                "@R14",
                "M=D",
                f"@Call_{FunctionInstruction.call_num}",
                "D=A",
                "@R15",
                "M=D",
                "@Call_share",
                "0;JMP",
                f"(Call_{FunctionInstruction.call_num})",
                f"@{self.function_name}",
                "0;JMP",
                f"({function_current}$ret.{i})",
            ]
        elif self.command == "return":
            FunctionInstruction.current_function_call_num = 0
            return [
                "@Return_share",
                "0;JMP",
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


class Asm:
    pass


class AAsm(Asm):
    def __init__(self, asm_code: str) -> None:
        self.value = asm_code[1:]

    def __repr__(self) -> str:
        return f"@{self.value}"


class CAsm(Asm):
    def __init__(self, asm_code: str) -> None:
        parts = asm_code.split(";")
        comp_dest = parts[0].split("=")
        self.comp = comp_dest[-1]
        self.dest = comp_dest[0] if len(comp_dest) > 1 else ""
        self.jump = parts[1] if len(parts) > 1 else ""

    def __repr__(self) -> str:
        fst = f"{self.dest}=" if self.dest else ""
        snd = self.comp
        thrd = f";{self.jump}" if self.jump else ""
        return f"{fst}{snd}{thrd}"


class LAsm(Asm):
    def __init__(self, asm_code: str) -> None:
        self.label = asm_code[1:-1]

    def __repr__(self) -> str:
        return f"({self.label})"


class AsmOptimizer:
    def __init__(self, asm_code: list[str]) -> None:
        self.asm = [parse(line) for line in asm_code if line.strip()]
        self.basic_blocks = self.cut_to_basic_blocks()
        self.reachable_blocks = self.find_reachable_blocks()
        self.optimized_asm = [item for block in self.reachable_blocks for item in block]

    def cut_to_basic_blocks(self) -> list[list[Asm]]:
        blocks: list[list[Asm]] = []
        current_block: list[Asm] = []
        for ins in self.asm:
            if isinstance(ins, LAsm):
                if current_block:
                    blocks.append(current_block)
                current_block = [ins]
            elif isinstance(ins, CAsm) and ins.jump == "JMP":
                current_block.append(ins)
                blocks.append(current_block)
                current_block = []
            else:
                current_block.append(ins)
        if current_block:
            blocks.append(current_block)
        return blocks

    def find_reachable_blocks(self) -> list[list[Asm]]:
        reachable_blocks: list[int] = []
        visited = set()
        table = {"Start": 0} if self.basic_blocks else {}
        for index, block in enumerate(self.basic_blocks):
            if isinstance(block[0], LAsm):
                label = block[0].label
                table[label] = index
        stack = ["Start"] if self.basic_blocks else []
        while stack:
            label = stack.pop()
            index = table[label]
            if index not in visited:
                visited.add(index)
                reachable_blocks.append(index)
                block = self.basic_blocks[index]
                for i, ins in enumerate(block):
                    if isinstance(ins, CAsm) and ins.jump and i > 0:
                        last_ins = block[i - 1]
                        if isinstance(last_ins, AAsm):
                            target_label = last_ins.value
                            stack.append(target_label)
                            share_list = [
                                "Eq_share",
                                "Gt_share",
                                "Lt_share",
                                "Call_share",
                            ]
                            global Function_Local_set
                            share_list.extend(
                                [f"Function{m}Local_share" for m in Function_Local_set]
                            )
                            if target_label in share_list:
                                next_block = self.basic_blocks[index + 1]
                                if isinstance(next_block[0], LAsm):
                                    target_label = next_block[0].label
                                    stack.append(target_label)
                if label.startswith("Call_"):
                    next_block = self.basic_blocks[index + 1]
                    if isinstance(next_block[0], LAsm):
                        target_label = next_block[0].label
                        stack.append(target_label)
                if not (isinstance(block[-1], CAsm) and block[-1].jump == "JMP"):
                    next_block = (
                        self.basic_blocks[index + 1]
                        if index + 1 < len(self.basic_blocks)
                        else []
                    )
                    if next_block and isinstance(next_block[0], LAsm):
                        target_label = next_block[0].label
                        stack.append(target_label)

        reachable_blocks.sort()
        return [self.basic_blocks[i] for i in reachable_blocks]


class VMCodeOptimizer:
    def __init__(self, vm_code: list[Instruction]) -> None:
        self.vm_code = vm_code


def parse(asm_code: str) -> Asm:
    if asm_code.startswith("@"):
        return AAsm(asm_code)
    elif asm_code.startswith("("):
        return LAsm(asm_code)
    else:
        return CAsm(asm_code)


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
        asm = ["@256", "D=A", "@SP", "M=D"]
        initCall = FunctionInstruction("call", "Sys.init", 0)
        asm.extend(initCall.to_asm())
        asm.extend(eq_share)
        asm.extend(gt_share)
        asm.extend(lt_share)
        asm.extend(call_share)
        asm.extend(return_share)
        asm.extend(function_Local_share)
        for file_name in os.listdir(inputpath):
            if file_name.endswith(".vm"):
                set_file_path(os.path.join(inputpath, file_name))
                set_function_current("WarningNotInAFunction")
                with open(os.path.join(inputpath, file_name), "r") as f:
                    content = f.read()
                vm_translator = VMTranslator(content)
                asm.extend(vm_translator.asm)
        asm_optimizer = AsmOptimizer(asm)
        with open(output_path, "w") as f:
            for line in asm_optimizer.optimized_asm:
                f.write(f"{line}" + "\n")
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
        asm = ["@StartUp", "0;JMP"]
        asm.extend(eq_share)
        asm.extend(gt_share)
        asm.extend(lt_share)
        asm.extend(call_share)
        asm.extend(return_share)
        asm.extend(function_Local_share)
        asm.append("(StartUp)")
        asm.extend(vm_translator.asm)
        asm_optimizer = AsmOptimizer(asm)
        with open(output_path, "w") as f:
            for line in asm_optimizer.optimized_asm:
                f.write(f"{line}" + "\n")


if __name__ == "__main__":
    main()
