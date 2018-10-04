# pdfcli

A tool for manipulating pdf files from the command line.

## Installation

```bash
pip install pdfcli
```


## Usage

The pdfcli command line tool allows you to perform page level manipulations
of PDF files. Supported operations include:


### Merging
```bash
# By default merge will combine pdfs in order that 
# they are written on command line and write out
# to out.pdf
 
>>> pdfcli merge test_files/PDF1.pdf test_files/PDF2.pdf
>>> ls
PDF1.pdf        PDF2.pdf        PDF3.pdf        out.pdf
```

```bash
# Specify the output file
 
>>> pdfcli merge PDF1.pdf PDF2.pdf PDF3.pdf -o MergedPDFS.pdf
>>> ls 
MergedPDFS.pdf  PDF1.pdf        PDF2.pdf        PDF3.pdf
```

### Reordering

```bash
# Reversing the pdfs 
>>> pdfcli reorder test_files/PDF1.pdf --reverse
```

```bash
#  Reordering based on page number
>>> pdfcli reorder test_files/MultiPagePDF.pdf --order=3,1,2
```

### Deleting
```bash
# Delete third page, keep others
>>> pdfcli delete test_files/MultiPagePDF.pdf 3
```


### Splitting
```bash
>>> pdfcli split test_files/MultiPagePDF.pdf 1
Split test_files/MultiPagePDF.pdf at index 1 into out1.pdf and out2.pdf
>>> ls
```


### Getting Help


#### Command Help

```bash
>>> pdfcli --help
Usage: pdfcli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  delete   Delete pages in a PDF at a particular index
  merge    Merge a set of PDF files together For example if you want to...
  reorder  Change a PDF pages order For example if you have three pages and...
  split    Split a file at a particular index

```

#### Subcommmand Help

```bash
>>> pdfcli merge --help
 
Usage: pdfcli merge [OPTIONS] [FILES]...

  Merge a set of PDF files together

  For example if you want to merge example1.pdf example2.pdf and
  example3.pdf in that order, then you would write: pdfcli merge
  example1.pdf example2.pdf example3.pdf

Options:
  -o, --out PATH  The path of the output pdf. defaults to out.pdf
  --help          Show this message and exit.

```

