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
    Merge a set of PDF files together
    '''
    for filename in files:
        click.echo(filename)


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
@click.option('-r', '--reverse',
              type=click.BOOL,
              help="Set to True to reverse the order of the PDFs")
def reorder(file, order, reverse, out):
    '''
    Change a PDF pages order

    For example if you have three pages and you want to place the 2nd page first,
    the first page last and the last page second then you would write:pdfcli reorder 2 3 1
    '''
    if not reverse and not out:
        raise click.UsageError("Either the reverse or out switch must be set when using reorder.")


if __name__ == '__main__':
    cli()