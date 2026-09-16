'''
Automated test suite for repopy's file system engine.
'''

from repopy.file_system import FileSystemEngine

def test_read_requirements_filters_comments_and_blanks(tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('requests>=2.28\n\n# comment\npytest\n    \n')

    fs_engine = FileSystemEngine(tmp_path)
    deps = fs_engine.read_requirements()

    assert deps == ['requests>=2.28', 'pytest']


def test_read_requirements_missing_file(tmp_path):
    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.read_requirements() == []


def test_read_requirements_empty_file(tmp_path):
    req_file = tmp_path / 'requirements.txt'
    req_file.write_text('')

    fs_engine = FileSystemEngine(tmp_path)
    assert fs_engine.read_requirements() == []