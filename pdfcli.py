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
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
def merge(files, out, key):
    '''
    Merge a set of PDF files together.
    '''
    _merge(*files,
           out=out,
           key=key)


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
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
def reorder(file, order, reverse, out, key):
    '''
    Reorder the pages in a PDF.
    '''
    _reorder(file=file,
             order=order,
             reverse=reverse,
             out=out,
             key=key)


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
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
def delete(file, delete_indexes, out, key):
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
            out=out,
            key=key)


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
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
@click.option('--out-second',
              default='out2.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out2.pdf")
def split(file, split_index, out_first, out_second, key):
    '''Split a PDF file into two.'''
    _split(file=file,
           index=split_index,
           out_first=out_first,
           out_second=out_second,
           key=key)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.argument('direction',
                nargs=1,
                type=click.Choice(['clockwise', 'counter-clockwise']))
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
@click.option('-o', '--out',
              default='out.pdf',
              type=click.Path(),
              help="The path of the output pdf. defaults to out.pdf")
def rotate(file, direction, out, key):
    '''
    Rotate a PDF file clockwise or counter-clockwise.
    '''
    _rotate(file=file,
            direction=direction,
            out=out,
            key=key)


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
def encrypt(file, out, key):
    '''
    Encrypts a PDF file given a key.
    '''
    _encrypt(file=file, out=out, key=key)


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
def decrypt(file, out, key):
    '''
    Decrypts a PDF file given a key.
    '''
    _decrypt(file=file, out=out, key=key)


@cli.command()
@click.argument('file',
                nargs=1,
                type=click.Path(exists=True))
@click.option('-k', '--key',
              envvar='PDFCLI_KEY',
              help="Password to decrypt PDF with. Can also be specified as environment variable PDFCLI_KEY")
def info(file, key):
    '''
    Retrieves metadata info from PDF file.
    '''
    _info(file=file, key=key)


def _merge(*files, **kwargs):
    decrypt_key = _encr_key_encoding(kwargs['key'])

    if len(files) == 0:
        raise click.BadParameter('There were no files provided to merge')

    merger = PyPDF2.merger.PdfFileMerger()
    for file in files:
        with open(file, 'rb') as fp:
            pdf_reader = get_pdf_reader(fp, file, key=decrypt_key)
            merger.append(pdf_reader)

    merger.write(kwargs['out'])
    click.echo("Merged files %s into %s" % (files, kwargs['out']))


def _reorder(*args, **kwargs):
    file_arg = kwargs['file']
    reverse = kwargs['reverse']
    order = kwargs['order']
    out = kwargs['out']
    decrypt_key = _encr_key_encoding(kwargs['key'])

    if not reverse and not order:
        raise click.UsageError("Either the reverse or out switch must be set when using reorder.")

    if order:
        try:
            order = order.split(",")
            order = [int(num) for num in order]
        except ValueError as e:
            raise click.BadParameter("order must be a list of integers representing indexes in PDF.")

    with open(file_arg, 'rb') as pdf_fp, open(out, 'wb') as pdf_fp_w:
        pdf_reader = get_pdf_reader(pdf_fp, file_arg, key=decrypt_key)

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
    decrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp:
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg, key=decrypt_key)
        num_pages = pdf_reader.getNumPages()

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
    decrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp, open(out_first, 'wb') as pdf_fp_one, \
            open(out_second, 'wb') as pdf_fp_two:
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg, key=decrypt_key)

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
    decrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp, open(out, 'wb') as pdf_writer_fp:
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg, key=decrypt_key)

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
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg)

        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.appendPagesFromReader(pdf_reader)
        pdf_writer.encrypt(encrypt_key)
        pdf_writer.write(pdf_writer_fp)
        click.echo("PDF was successfully encrypted and saved at %s" % out)


def _decrypt(*args, **kwargs):
    file_arg = kwargs['file']
    out = kwargs['out']
    decrypt_key = _encr_key_encoding(kwargs['key'])

    with open(file_arg, 'rb') as pdf_reader_fp, open(out, 'wb') as pdf_writer_fp:
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg, key=decrypt_key)

        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.appendPagesFromReader(pdf_reader)
        pdf_writer.write(pdf_writer_fp)
        click.echo("PDF was successfully decrypted and saved at %s" % out)


def _info(*args, **kwargs):
    file_arg = kwargs['file']
    decrypt_key = _encr_key_encoding(kwargs['key'])
    with open(file_arg, 'rb') as pdf_reader_fp:
        pdf_reader = get_pdf_reader(pdf_reader_fp, file_arg, key=decrypt_key)
        document_info = pdf_reader.getDocumentInfo()
        for key in document_info.keys():
            value = str(document_info[key])
            click.echo("%s: %s" % (_strip_forward_slash(key), value))


def _encr_key_encoding(key):
    '''
    Passes the proper key encoding in Python 2 versus
    Python 3 due to a bug in pyPDF2 library.
    '''
    if not key:
        return None
    elif int(sys.version[0]) == 3:
        return key
    else:
        return key.encode('utf-8')

def _strip_forward_slash(key):
    return key.strip('/')


def get_pdf_reader(pdf_fp, file_arg, key=None):
    try:
        pdf_reader = PyPDF2.PdfFileReader(pdf_fp)
        if key:
            pdf_reader.decrypt(key)
        return pdf_reader
    except PyPDF2.utils.PdfReadError as e:
        raise click.BadParameter("PDF File could not be recognized %s." % (file_arg))


if __name__ == '__main__':
    cli()
