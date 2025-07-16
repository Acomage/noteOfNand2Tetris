import argparse
from typing import Optional


class Instruction:
    def to_binary(self) -> str:
        raise NotImplementedError("Subclasses should implement this method")


class AInstruction(Instruction):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"@{self.value}"

    def to_binary(self) -> str:
        return f"{self.value:016b}"


class CInstruction(Instruction):
    def __init__(self, dest: Optional[str], comp: str, jump: Optional[str]) -> None:
        self.dest = dest
        self.comp = comp
        self.jump = jump

    def __repr__(self) -> str:
        dest_str = f"{self.dest}=" if self.dest else ""
        jump_str = f";{self.jump}" if self.jump else ""
        return f"{dest_str}{self.comp}{jump_str}"

    def to_binary(self) -> str:
        dest_bits = self.dest_to_bits(self.dest)
        comp_bits = self.comp_to_bits(self.comp)
        jump_bits = self.jump_to_bits(self.jump)
        return f"111{comp_bits}{dest_bits}{jump_bits}"

    def dest_to_bits(self, dest: Optional[str]) -> str:
        dest_table = {
            None: "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111",
        }
        return dest_table.get(dest, "000")

    def comp_to_bits(self, comp: str) -> str:
        comp_table = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101",
        }
        return comp_table.get(comp, "0000000")

    def jump_to_bits(self, jump: Optional[str]) -> str:
        jump_table = {
            None: "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111",
        }
        return jump_table.get(jump, "000")


class Assember:
    def __init__(self, asm: str) -> None:
        self.tagsTable: dict[str, int] = {
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
        }
        self.varTable: dict[str, int] = {}
        self.instructions = [self.str_to_instruction(ins) for ins in self.cut(asm)]
        self.binary = [ins.to_binary() for ins in self.instructions]

    def cut(self, asm: str) -> list[str]:
        instructions = []
        instruction_current = ""
        iscomment = False
        meetaslash = False
        isTag = False
        line_number = 0
        tag_current = ""
        for char in asm:
            if char == "\n":
                if instruction_current != "":
                    instructions.append(instruction_current)
                    instruction_current = ""
                    line_number += 1
                iscomment = False
            elif char == "/":
                if meetaslash:
                    iscomment = True
                    meetaslash = False
                else:
                    meetaslash = True
            elif char == "(":
                if not iscomment:
                    isTag = True
            elif char == ")":
                if isTag:
                    self.tagsTable[tag_current] = line_number
                    isTag = False
                    tag_current = ""
                else:
                    if not iscomment:
                        raise ValueError("Unmatched opening parenthesis")
            else:
                if not iscomment and char != " ":
                    if isTag:
                        tag_current += char
                    else:
                        instruction_current += char
        if instruction_current != "":
            instructions.append(instruction_current)
        return instructions

    def str_to_instruction(self, instruction: str) -> Instruction:
        if instruction.startswith("@"):
            value = instruction[1:]
            if value.isdigit():
                return AInstruction(int(value))
            elif value in self.tagsTable:
                return AInstruction(self.tagsTable[value])
            elif value in self.varTable:
                return AInstruction(self.varTable[value])
            else:
                new_var = len(self.varTable) + 16  # Start from R16
                self.varTable[value] = new_var
                return AInstruction(new_var)
        else:
            parts = instruction.split(";")
            comp_dest = parts[0].split("=")
            comp = comp_dest[-1]
            dest = comp_dest[0] if len(comp_dest) > 1 else None
            jump = parts[1] if len(parts) > 1 else None
            return CInstruction(dest, comp, jump)


def main():
    parser = argparse.ArgumentParser(description="Hack Assembler")
    parser.add_argument("filepath", help="Path to the file to read")
    parser.add_argument("-o", help="Output file path")
    args = parser.parse_args()
    with open(args.filepath, "r") as f:
        content = f.read()
    assember = Assember(content)
    if not args.o:
        output_path = args.filepath.replace(".asm", ".hack")
    else:
        output_path = args.o
    with open(output_path, "w") as f:
        for line in assember.binary:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
