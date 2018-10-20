import sys
import click
import PyPDF2


@click.group()
def cli():
    pass


@cli.command()
@click.argument('files',
                nargs=-1,
                type=click.Path(exists=True))
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
def merge(files, out):
    '''
    Merge a set of PDF files together.
    '''
    _merge(*files,
           out=out)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
@click.option('-d', '--order',
              type=click.STRING,
              help="The reordering of the pdf as a list. For example if you have three pages and you want to place the"
                   "2nd page first, the first page last and the last page second then you would write:"
                   "pdfcli reorder 2 3 1")
@click.option('--reverse/--no-reverse', default=False, help="Set to True to reverse the order of the PDFs")
def reorder(file, order, reverse, out):
    '''
    Reorder the pages in a PDF.
    '''
    _reorder(file=file,
             order=order,
             reverse=reverse,
             out=out)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.argument('delete-indexes',
                type=click.STRING)
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
def delete(file, delete_indexes, out):
    '''
    Delete pages in a PDF.
    '''
    if delete_indexes:
        try:
            delete_indexes = delete_indexes.split(",")
            delete_indexes = [int(num) for num in delete_indexes]
        except ValueError as e:
            raise click.BadParameter("delete indexes must be a list of integers representing indexes in PDF.")
    else:
        raise click.BadParameter("must specify indexes to delete.")

    _delete(file=file,
            delete=delete_indexes,
            out=out)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.argument('split-index',
                nargs=1,
                default=0,
                type=click.INT)
@click.option('--out-first',
              default='out1.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out1.pdf")
@click.option('--out-second',
              default='out2.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out2.pdf")
def split(file, split_index, out_first, out_second):
    '''Split a PDF file into two.'''
    _split(file=file,
           index=split_index,
           out_first=out_first,
           out_second=out_second)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.argument('direction',
                nargs=1,
                type=click.Choice(['clockwise', 'counter-clockwise']))
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
def rotate(file, direction, out):
    '''
    Rotate a PDF file clockwise or counter-clockwise.
    '''
    _rotate(file=file,
            direction=direction,
            out=out)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
@click.option('-k', '--key',
              prompt=True,
              hide_input=True,
              confirmation_prompt=True,
              envvar='PDFCLI_KEY',
              help="Password to encrypt pdf with. Can also be specified as environment variable PDFCLI_KEY")
def encrypt(file, key, out):
    '''
    Encrypts a PDF file given a key.
    '''
    _encrypt(file=file, key=key, out=out)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.option('-k', '--key',
              prompt=True,
              hide_input=True,
              confirmation_prompt=True,
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
def decrypt(file, key, out):
    '''
    Decrypts a PDF file given a key.
    '''
    _decrypt(file=file, key=key, out=out)


def _merge(*files, **kwargs):
    if len(files) == 0:
        raise click.BadParameter('There were no files provided to merge')

    merger = PyPDF2.merger.PdfFileMerger()
    for file in files:
        with open(file, 'rb') as fp:
            try:
                merger.append(PyPDF2.PdfFileReader(file, 'rb'))
            except PyPDF2.utils.PdfReadError as e:
                raise click.BadParameter("PDF File could not be recognized %s." % (file))

    merger.write(kwargs['out'])
    click.echo("Merged files %s into %s" % (files, kwargs['out']))


def _reorder(*args, **kwargs):
    file_arg = kwargs['file']
    reverse = kwargs['reverse']
    order = kwargs['order']
    out = kwargs['out']

    if not reverse and not order:
        raise click.UsageError("Either the reverse or out switch must be set when using reorder.")

    if order:
        try:
            order = order.split(",")
            order = [int(num) for num in order]
        except ValueError as e:
            raise click.BadParameter("order must be a list of integers representing indexes in PDF.")

    with open(file_arg, 'rb') as pdf_fp, open(out, 'wb') as pdf_fp_w:
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_fp)
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF File could not be recognized %s." % (file_arg))

        pdf_writer = PyPDF2.PdfFileWriter()
        num_pages = pdf_reader.getNumPages()

        if order:
            for index in order:
                if index > num_pages - 1:
                    raise click.BadParameter('Indexes start from zero must be less than the number of pages')

        if reverse:
            order = [i for i in range(num_pages - 1, -1, -1)]

        for index in order:
            pdf_writer.addPage(pdf_reader.getPage(index))

        pdf_writer.write(pdf_fp_w)
        click.echo("Reordered pages in %s and rewrote file to %s" % (file_arg, out))


def _delete(*args, **kwargs):
    file_arg = kwargs['file']
    delete_pages = kwargs['delete']
    out = kwargs['out']

    with open(file_arg, 'rb') as pdf_reader_fp:
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_reader_fp)
            num_pages = pdf_reader.getNumPages()
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF File could not be recognized %s." % (file_arg))

        for page in delete_pages:
            if page > num_pages - 1:
                raise click.BadParameter('All indexes must be within range of the length of the PDF')

        with open(out, 'wb') as pdf_writer_fp:
            pdf_writer = PyPDF2.PdfFileWriter()
            for i in range(num_pages):
                if i not in delete_pages:
                    pdf_writer.addPage(pdf_reader.getPage(i))

            pdf_writer.write(pdf_writer_fp)
            click.echo("Deleted pages %s from %s and created new PDF at %s" % (delete_pages, file_arg, out))


def _split(*args, **kwargs):
    file_arg = kwargs['file']
    split_index = kwargs['index']
    out_first = kwargs['out_first']
    out_second = kwargs['out_second']

    with open(file_arg, 'rb') as pdf_reader_fp, open(out_first, 'wb') as pdf_fp_one, \
            open(out_second, 'wb') as pdf_fp_two:

        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_reader_fp)
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF File could not be recognized %s." % file_arg)

        pdf_writer_one = PyPDF2.PdfFileWriter()
        pdf_writer_two = PyPDF2.PdfFileWriter()

        num_pages = pdf_reader.getNumPages()

        if split_index > num_pages - 1:
            raise click.BadParameter('The split index must be less than the number of pages')

        for i in range(num_pages):
            if i < split_index:
                pdf_writer_one.addPage(pdf_reader.getPage(i))
            else:
                pdf_writer_two.addPage(pdf_reader.getPage(i))
            pdf_writer_one.write(pdf_fp_one)
            pdf_writer_two.write(pdf_fp_two)
        click.echo("Split %s at index %s into %s and %s" % (file_arg, split_index, out_first, out_second))


def _rotate(*args, **kwargs):
    file_arg = kwargs['file']
    direction = kwargs['direction']
    out = kwargs['out']
    with open(file_arg, 'rb') as pdf_reader_fp, open(out, 'wb') as pdf_writer_fp:
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_reader_fp)
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF File could not be recognized %s." % file_arg)

        pdf_writer = PyPDF2.PdfFileWriter()
        num_pages = pdf_reader.getNumPages()

        for i in range(num_pages):
            page = pdf_reader.getPage(i)
            if direction == "clockwise":
                page = page.rotateClockwise(90)
            else:
                page = page.rotateCounterClockwise(90)
            pdf_writer.addPage(page)
        pdf_writer.write(pdf_writer_fp)
        click.echo("Pages were rotated %s successfully and saved at %s" % (direction, out))


def _encrypt(*args, **kwargs):
    file_arg = kwargs['file']
    out = kwargs['out']
    encrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp, open(out, 'wb') as pdf_writer_fp:
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_reader_fp)
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF File could not be recognized %s." % file_arg)

        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.appendPagesFromReader(pdf_reader)
        pdf_writer.encrypt(encrypt_key)
        pdf_writer.write(pdf_writer_fp)
        click.echo("PDF was successfully encrypted and saved at %s" % out)


def _decrypt(*args, **kwargs):
    file_arg = kwargs['file']
    out = kwargs['out']
    encrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp, open(out, 'wb') as pdf_writer_fp:
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_reader_fp)
        except PyPDF2.utils.PdfReadError as e:
            raise click.BadParameter("PDF FILE could not be recognized %s." % file_arg)

        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_reader.decrypt(encrypt_key)
        pdf_writer.appendPagesFromReader(pdf_reader)
        pdf_writer.write(pdf_writer_fp)
        click.echo("PDF was successfully decrypted and saved at %s" % out)


def _encr_key_encoding(key):
    '''
    Passes the proper key encoding in Python 2 versus
    Python 3 due to a bug in pyPDF2 library.
    '''
    if int(sys.version[0]) == 3:
        return key
    else:
        return key.encode('utf-8')



if __name__ == '__main__':
    cli()
