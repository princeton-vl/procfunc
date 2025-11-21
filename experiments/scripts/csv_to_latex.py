import csv
import argparse

def csv_to_latex(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Calculate max width for each column
    col_widths = [0] * len(rows[0])
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # Start LaTeX table
    num_cols = len(rows[0])
    col_spec = " | ".join(["c"] * num_cols)
    latex = f"\\begin{{tabular}}{{| {col_spec} |}}\n"
    latex += "\\hline\n"
    
    # Header row (first row)
    header_cells = [f"\\textbf{{{cell.ljust(col_widths[i])}}}" for i, cell in enumerate(rows[0])]
    latex += " & ".join(header_cells) + " \\\\\n"
    latex += "\\hline\n"
    
    # Data rows
    for row in rows[1:]:
        padded_cells = [cell.ljust(col_widths[i]) for i, cell in enumerate(row)]
        latex += " & ".join(padded_cells) + " \\\\\n"
    
    latex += "\\hline\n"
    latex += "\\end{tabular}"
    
    print(latex)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert CSV to LaTeX table')
    parser.add_argument('input', help='Input CSV file')
    
    args = parser.parse_args()
    print("\n\n" + args.input + "\n" + "="*100 + "\n")
    csv_to_latex(args.input)