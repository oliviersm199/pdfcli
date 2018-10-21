.. pdfcli documentation master file, created by
   sphinx-quickstart on Sat Oct 13 16:48:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pdfcli
==================================

A tool for manipulating pdf files from the command line.

*************
Installation
*************

.. code-block:: bash

   pip install pdfcli


*************
Merging
*************

.. code-block:: bash

   >>> pdfcli merge test_files/PDF1.pdf test_files/PDF2.pdf
   >>> ls
   PDF1.pdf        PDF2.pdf        PDF3.pdf        out.pdf

.. code-block:: bash

   >>> pdfcli merge PDF1.pdf PDF2.pdf PDF3.pdf -o MergedPDFS.pdf
   >>> ls
   PDF1.pdf        PDF2.pdf        PDF3.pdf        MergedPDFS.pdf

*************
Reordering
*************

.. code-block:: bash

   # Reversing the pdfs
   >>> pdfcli reorder test_files/PDF1.pdf --reverse

.. code-block:: bash

   #  Reordering based on page number
   >>> pdfcli reorder test_files/MultiPagePDF.pdf --order=3,1,2


*************
Deleting
*************

.. code-block:: bash

   # Delete third page, keep others
   >>> pdfcli delete test_files/MultiPagePDF.pdf 3


*************
Splitting
*************

.. code-block:: bash

   >>> pdfcli split test_files/MultiPagePDF.pdf 1
   Split test_files/MultiPagePDF.pdf at index 1 into out1.pdf and out2.pdf

*************
Rotating
*************

.. code-block:: bash

   # Clockwise Rotation
   >>> pdfcli rotate test_files/MultiPagePDF.pdf clockwise
   Pages were rotated clockwise successfully and saved at out.pdf

   # Counter-Clockwise Rotation
   >>> pdfcli rotate test_files/MultiPagePDF.pdf counter-clockwise
   Pages were rotated counter-clockwise successfully and saved at out.pdf


*************
Encrypting
*************

.. code-block:: bash

   # Can specify encryption key as option or environment variable PDFCLI_KEY
   >>> pdfcli encrypt test.pdf --key=oli123 --out encrypted.pdf
   PDF was successfully encrypted and saved at encrypted.pdf

*************
Decrypting
*************

.. code-block:: bash

   # Can specify decryption key as option or environment variable PDFCLI_KEY
   >>> pdfcli decrypt test.pdf --key=oli123 --out decrypted.pdf
   PDF was successfully decrypted and saved at decrypted.pdf

*************
Info
*************

.. code-block:: bash

   # Can retrieve metadata about PDF
   >>> pdfcli info test_files/PDF1.pdf
   Title: Microsoft Word - Document1
   Producer: Mac OS X 10.12.6 Quartz PDFContext
   Creator: Word
   CreationDate: D:20180930133024Z00'00'
   ModDate: D:20180930133024Z00'00'
   Keywords:
   AAPL:Keywords: []


*************
Help
*************


.. code-block:: bash

   >>> pdfcli --help
   Usage: pdfcli.py [OPTIONS] COMMAND [ARGS]...

   Options:
     --help  Show this message and exit.

   Commands:
     decrypt  Decrypts a PDF file given a key.
     delete   Delete pages in a PDF.
     encrypt  Encrypts a PDF file given a key.
     merge    Merge a set of PDF files together.
     reorder  Reorder the pages in a PDF.
     rotate   Rotate a PDF file clockwise or counter-clockwise.
     split    Split a PDF file into two.
