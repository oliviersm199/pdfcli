from setuptools import setup


setup(
    name="pdfcli",
    version="0.1",
    py_modules=['pdfcli'],
    install_requires=[
        'Click>=7.0, <8.0',
        'PyPDF2>=1.26.0,<2.0'
    ],
    license="MIT",
    author="Olivier Simard-Morissette",
    author_email="olivier.morissette@gmail.com",
    description="Simple utility for merging and reordering PDF pages",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points='''
        [console_scripts]
        pdfcli.py=pdfcli.py:cli
    '''
)