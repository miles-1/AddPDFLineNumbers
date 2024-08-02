# Add Line Numbers to Existing PDF

This command-line program can be used to add line numbers to an existing pdf. It is not fully automated and requires user input, but is much faster and neater than manually adding line numbers via annotations.

To add line numbers to a file `target.pdf`, begin by running the script as follows:
```bash
python /path_to_folder/main.py target.pdf
```
This will create two new documents: `linenums_target.pdf` and `linenums_target.csv`. The new `.pdf` file is the same as the original, but with annotations added to the margin. These annotations give the vertical position where they are placed, which acts as a ruler (see below). In the new `.csv` document, you will find the following headers, described here:
- `page`: the page number where the given row's instructions will be applied, where the first page is page `0`.
- `y_pos`: the horizontal position of line numbers, where the auto-generated position is 5% of the page width.
- `start_x_pos` and `end_x_pos`: the start and end vertical position of line numbers, where the auto-geerated position is 5% and 95% of the page height.
- `space_pattern`: the pattern of spaces between line numbers, where `1` is even spacing between all numbers and `1|1|2.5` would indicate that every third number would be followed by a 2.5x bigger gap.
- `num_count`: The number of line numbers to put inside the specified `x_pos` range.
- `start_num`: The initial number in the range, where `continue` indicates that numbers should just continue from the previous ones.
- `font_size`: The size of the font to use for annotations.

Default values are inserted into all fields in the generated `linenums_target.csv` file. It serves as a convenient starting point, where one can use the initially-generated `.pdf` as a reference to adjust the rows of the `.csv`, where its annotations act as a ruler to specify the start and end of each line number range. Note that multiple rows in the `.csv` file can give line number instructions for a single page.

After editing this csv file, this script can be re-run, just as it was initially, and the new `.csv` file will then be applied, so that line numbers will appear as specified.


# Dependencies

This program uses `pypdf` to add line numbers as annotations to the pdf. To install, run:
```bash
pip install pypdf
```