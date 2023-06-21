import sys
from project.my_language.interpreter import interpreter, BaseOutput
from pathlib import Path


class OutputToStdin(BaseOutput):
    def write(self, text: str):
        print(text)

    def write_error(self, text: str):
        sys.stderr.write(text)


if __name__ == "__main__":
    print(sys.argv)

    if len(sys.argv) < 2:
        sys.stderr.write("Either the file path or the program text was not provided.")

    output = OutputToStdin()
    content_or_path = Path(sys.argv[1])
    if content_or_path.is_file():
        file_format = ".mylg"

        if not content_or_path.name.endswith(file_format):
            sys.stderr.write(f"Incorrect file format. Expected: {file_format}")

        with open(content_or_path) as file:
            interpreter(file.read(), output)
    else:
        text_program = "\n".join(sys.argv[1:])
        interpreter(text_program, output)
