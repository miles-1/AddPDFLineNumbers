import sys
from os.path import exists, join, dirname, basename
from csv import DictReader
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText

csv_headers = (
    "page",
    "x_pos",
    "start_y_pos",
    "end_y_pos",
    "space_pattern",
    "num_count",
    "start_num",
    "font_size"
)

generated_csv_params = {
    "x_proportion": 0.05,
    "y_proportion": 0.05,
    "num_lines": 60,
    "font_size": 8,
}

### Functions ###

def get_y_pos(start_y_pos: float, end_y_pos: float, space_pattern: str, num_count: int, **_) -> list[int]:
    if isinstance(space_pattern, int) or not space_pattern.replace("|", "").replace(".", "").isdigit():
        space_pattern = (1.,)
    else:
        space_pattern = tuple(
            float(space) 
            for space in space_pattern.split("|") 
            if (space not in ("", ".") or float(space) != 0.)
        )
    total_space = ((num_count - 1) // len(space_pattern)) * sum(space_pattern) + \
        sum(space_pattern[:(num_count - 1) % len(space_pattern)])
    space_scale = (end_y_pos - start_y_pos) / total_space
    scaled_space_pattern = tuple(space * space_scale for space in space_pattern)
    y_positions = [start_y_pos]
    for i in range(num_count - 1):
        most_recent = y_positions[-1]
        y_positions.append(most_recent + scaled_space_pattern[i % len(space_pattern)])
    return y_positions

def check_arg_exists(file_name: str, extension: str, error_extension: str) -> None:
    if not file_name.lower().endswith(extension):
        raise TypeError(error_extension)
    elif not exists(file_name):
        raise ValueError(f"File name {file_name} does not exist.")

def get_line_num_rows(csv_file_name: str) -> None|list[dict]:
    with open(csv_file_name, "r") as f:
        reader = DictReader(f)
        if not all(header in reader.fieldnames for header in csv_headers):
            raise NameError("Bad header names in csv file.")
        rows = list(reader)
    for row in rows:
        for k, v in row.items():
            if v.isdigit():
                row[k] = int(v)
            elif v.replace(".", "", 1).isdigit():
                row[k] = float(v)
    return rows

def generate_line_num_csv(pdf_file_name: str, csv_file_name: str) -> bool:
    if exists(csv_file_name):
        return False
    x_prop, y_prop = generated_csv_params["x_proportion"], generated_csv_params["y_proportion"]
    num_lines, font_size = generated_csv_params["num_lines"], generated_csv_params["font_size"]
    with PdfReader(pdf_file_name) as pdf_reader, open(csv_file_name, "w") as csv_writer:
        csv_writer.write(",".join(csv_headers) + "\n")
        for page_indx, page in enumerate(pdf_reader.pages):
            _, _, width, height = page.mediabox
            csv_writer.write(f"{page_indx},{width * y_prop:.2f},{height * x_prop:.2f},{height * (1 - x_prop):.2f},1,{num_lines},continue,{font_size}\n")
    return True

def read_csv_info(csv_file_name: str) -> tuple[list[dict], any]:
    rows = get_line_num_rows(csv_file_name)
    highest_line_num = sum(int(row["num_count"]) for row in rows)
    line_num_decimal_places = len(str(highest_line_num))
    return rows, lambda x: f"{x:>0{line_num_decimal_places}}"

def annotate_pdf(pdf_file_name: str, csv_rows: list, get_num: any, mark_position: bool) -> None:
    writer = PdfWriter()
    new_pdf_file_name = join(dirname(pdf_file_name), f"linenums_{basename(pdf_file_name)}")
    page_heights = []
    with PdfReader(pdf_file_name) as pdf_reader:
        for page in pdf_reader.pages:
            writer.add_page(page)
            page_heights.append(page.mediabox.height)
    current_num = 1
    for row in csv_rows:
        page = row["page"]
        font_size = row["font_size"]
        x = row["x_pos"]
        y_poss = get_y_pos(**row)
        current_num = current_num if row["start_num"] == "continue" else int(row["start_num"])
        for y in y_poss:
            y_prime = page_heights[page] - y
            annotation = FreeText(
                text=f"{y:.1f}" if mark_position else get_num(current_num),
                rect=(x,y_prime,x+20,y_prime+20),
                font_size=f"{font_size}pt",
            )
            current_num += 1
            writer.add_annotation(page_number=page, annotation=annotation)
    with open(new_pdf_file_name, "wb") as fp:
        writer.write(fp)

### main ####

if __name__ == "__main__":
    # check args
    args = sys.argv[1:]
    if len(args) == 0:
        raise TypeError("Missing required arguments: pdf file (optional: line number csv file).")
    elif len(args) == 1:
        pdf_file_name = args[0]
        check_arg_exists(pdf_file_name, ".pdf", "The first argument of the script must be a .pdf file.")
        csv_file_name = join(dirname(pdf_file_name), f"linenums_{basename(pdf_file_name)[:-4]}.csv")
        was_csv_generated = generate_line_num_csv(pdf_file_name, csv_file_name)
    elif len(args) == 2:
        pdf_file_name, csv_file_name = args
        check_arg_exists(pdf_file_name, ".pdf", "The first argument of the script must be a .pdf file.")
        check_arg_exists(csv_file_name, ".csv", "The second argument of the script must be a line number csv file.")
        was_csv_generated = False
    else:
        raise TypeError("Excessive number of arguments provided. At most two are allowed: the PDF file name and the line number file.")
    # run program
    annotate_pdf(pdf_file_name, *read_csv_info(csv_file_name), was_csv_generated)




