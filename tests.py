import os
import unittest
import tempfile
import PyPDF2
from click.testing import CliRunner
from pdfcli import cli

TEST_PDF_FOLDER = "test_files"
TEST_PDF_FILENAMES = ['PDF1.pdf', 'PDF2.pdf', 'PDF3.pdf']
TEST_PDF_PATHS = [os.path.join(TEST_PDF_FOLDER, file_name)
                  for file_name in TEST_PDF_FILENAMES]


class BasePDFCLITestCase(unittest.TestCase):
    def setUp(self):
        self.test_pdf_file_handles = [open(path, 'rb') for path in TEST_PDF_PATHS]
        self.runner = CliRunner()

    def tearDown(self):
        for file_handle in self.test_pdf_file_handles:
            file_handle.close()

        if os.path.exists('test_files/out.pdf'):
            os.remove('test_files/out.pdf')

        if os.path.exists('out1.pdf'):
            os.remove('out1.pdf')

        if os.path.exists('out2.pdf'):
            os.remove('out2.pdf')


class TestPYPDF2(BasePDFCLITestCase):

    def test_pypdf2_merge(self):
        merger = PyPDF2.merger.PdfFileMerger()

        for file in self.test_pdf_file_handles:
            merger.append(file)

        self.assertEqual(len(merger.pages), 3)
        fp = tempfile.TemporaryFile()
        merger.write(fp)
        fp.seek(0)
        pdf_reader = PyPDF2.PdfFileReader(fp)
        self.assertEqual(pdf_reader.getNumPages(), 3)
        fp.close()

    def test_pypdf2_writer(self):
        reader_pdf1 = PyPDF2.PdfFileReader(self.test_pdf_file_handles[0])

        writer = PyPDF2.PdfFileWriter()
        writer.addPage(reader_pdf1.getPage(0))

        fp = tempfile.TemporaryFile()
        writer.write(fp)
        fp.seek(0)
        pdf_reader = PyPDF2.PdfFileReader(fp)

        self.assertEqual(pdf_reader.getNumPages(), 1)


class TestCLITool(BasePDFCLITestCase):
    def test_help_gets_called(self):
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)


class TestMerge(BasePDFCLITestCase):
    def test_merge_valid_input(self):
        result = self.runner.invoke(cli, ['merge', '--out', 'test_files/out.pdf'] + TEST_PDF_PATHS)
        self.assertEqual(result.exit_code, 0)
        with open('test_files/out.pdf', 'rb') as file_reader:
            merged_pdf = PyPDF2.PdfFileReader(file_reader)
            self.assertEqual(merged_pdf.getNumPages(), 3)

    def test_merge_invalid_path(self):
        result = self.runner.invoke(cli, ['merge', 'fake_path'])
        self.assertEqual(result.exit_code, 2)

    def test_merge_valid_path_not_pdf(self):
        result = self.runner.invoke(cli, ['merge', 'test_files/test.txt', 'test_files/PDF1.pdf'])
        self.assertEqual(result.exit_code, 2)

    def test_merge_no_files_provided(self):
        result = self.runner.invoke(cli, ['merge'])
        self.assertEqual(result.exit_code, 2)


class TestReorder(BasePDFCLITestCase):
    def test_reorder_valid_input_reverse(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf',
                                          '--out', 'test_files/out.pdf', '--reverse'])
        self.assertEqual(result.exit_code, 0)

    def test_reorder_valid_input_order_specified(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf', '--out',
                                          'test_files/out.pdf', '--order', '2,0,1'])
        self.assertEqual(result.exit_code, 0)

    def test_reorder_valid_input_order_indexes_out_of_range(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf', '--out',
                                          'test_files/out.pdf', '--order','2,1,0,4,5,6'])
        self.assertEqual(result.exit_code, 2)

    def test_reorder_valid_input_indexes_duplicated(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf', '--out',
                                          'test_files/out.pdf', '--order','2,1,0,0,1,2'])
        self.assertEqual(result.exit_code, 0)

    def test_reorder_invalid_input_indexes_not_integers(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf', '--out',
                                          'test_files/out.pdf', '--order', 'hello,I,am,1'])
        self.assertEqual(result.exit_code, 2)

    def test_reorder_invalid_input_order_empty(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/MultiPagePDF.pdf', '--out',
                                          'test_files/out.pdf', '--order', ''])

    def test_reorder_bad_file(self):
        result = self.runner.invoke(cli, ['reorder', 'test_files/test.txt', '--out',
                                          'test_files/out.pdf', '--order','1,0,2'])
        self.assertEqual(result.exit_code, 2)


class TestDelete(BasePDFCLITestCase):
    def test_delete_valid_input(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf','0','--out','test_files/out.pdf'])
        self.assertEqual(result.exit_code, 0)
        with open('test_files/out.pdf', 'rb') as file_reader:
            pdf = PyPDF2.PdfFileReader(file_reader)
            self.assertEqual(pdf.getNumPages(), 2)

    def test_delete_valid_input_two_pages_removed(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf', '0,1', '--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 0)
        with open('test_files/out.pdf', 'rb') as file_reader:
            pdf = PyPDF2.PdfFileReader(file_reader)
            self.assertEqual(pdf.getNumPages(), 1)

    def test_out_of_index_delete(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf', '0,5', '--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 2)

    def test_no_input_delete(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf', '', '--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 2)

    def test_same_index_specified_twice(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf', '0,0,0,1','--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 0)
        with open('test_files/out.pdf', 'rb') as file_reader:
            pdf = PyPDF2.PdfFileReader(file_reader)
            self.assertEqual(pdf.getNumPages(), 1)

    def test_delete_invalid_file(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/test.txt', '0,0,0,1', '--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 2)

    def test_delete_invalid_indexes(self):
        result = self.runner.invoke(cli, ['delete', 'test_files/MultiPagePDF.pdf', 'asdfasd,asdfasf', '--out', 'test_files/out.pdf'])
        self.assertEqual(result.exit_code, 2)


class TestSplit(BasePDFCLITestCase):
    def test_split_correct_input(self):
        result = self.runner.invoke(cli, ['split', 'test_files/MultiPagePDF.pdf', '1'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('out1.pdf'))
        self.assertTrue(os.path.exists('out2.pdf'))
        with open('out1.pdf', 'rb') as read_fp_one, open('out2.pdf', 'rb') as read_fp_two:
            num_pages_one = PyPDF2.PdfFileReader(read_fp_one).numPages
            self.assertEqual(num_pages_one, 1)
            num_pages_two = PyPDF2.PdfFileReader(read_fp_two).numPages
            self.assertEqual(num_pages_two, 2)

    def test_split_not_integer_split(self):
        result = self.runner.invoke(cli, ['split', 'test_files/MultiPagePDF.pdf', 'asdfasdf'])
        self.assertEqual(result.exit_code, 2)


    def test_split_not_in_range_integer(self):
        result = self.runner.invoke(cli, ['split', 'test_files/MultiPagePDF.pdf', '10'])
        self.assertEqual(result.exit_code, 2)

    def test_split_bad_file(self):
        result = self.runner.invoke(cli, ['split', 'test_files/test.txt', '3'])
        self.assertEqual(result.exit_code, 2)


class TestRotate(BasePDFCLITestCase):
    def test_rotate_clockwise(self):
        result = self.runner.invoke(cli, ['rotate', 'test_files/MultiPagePDF.pdf', 'clockwise'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('out.pdf'))

    def test_rotate_counter_clockwise(self):
        result = self.runner.invoke(cli, ['rotate', 'test_files/MultiPagePDF.pdf', 'counter-clockwise'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('out.pdf'))

    def test_rotate_bad_file(self):
        result = self.runner.invoke(cli, ['rotate', 'test_files.test.txt', 'clockwise'])
        self.assertEqual(result.exit_code, 2)























if __name__ == '__main__':
    unittest.main()
