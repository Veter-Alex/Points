import os
import tempfile

from src.parsers import DateTimeExtractor


def test_normalize_datetime_iso():
    date, time = DateTimeExtractor.normalize_datetime("2025-08-17", "12:00:00")
    assert date == "17.08.2025"
    assert time == "12:00:00"

def test_normalize_datetime_short_time():
    date, time = DateTimeExtractor.normalize_datetime("2025-08-17", "12:00")
    assert date == "17.08.2025"
    assert time == "12:00:00"

def test_normalize_datetime_non_iso():
    date, time = DateTimeExtractor.normalize_datetime("17.08.2025", "12:00:00")
    assert date == "17.08.2025"
    assert time == "12:00:00"

def test_normalize_datetime_empty_time():
    date, time = DateTimeExtractor.normalize_datetime("2025-08-17", "")
    assert date == "17.08.2025"
    assert time == "00:00:00"

def test_extract_from_file_metadata():
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        tmp.write(b'<test></test>')
        tmp.flush()
        date, time = DateTimeExtractor.extract_from_file_metadata(tmp.name)
        assert date is not None
        assert time is not None
    os.remove(tmp.name)

def test_extract_datetime_with_fallback():
    # parsed_date and parsed_time present
    date, time = DateTimeExtractor.extract_datetime_with_fallback("2025-08-17", "12:00:00", "dummy.xml")
    assert date == "2025-08-17"
    assert time == "12:00:00"
    # parsed_date missing, fallback to file metadata
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        tmp.write(b'<test></test>')
        tmp.flush()
        file_date, file_time = DateTimeExtractor.extract_from_file_metadata(tmp.name)
        date, time = DateTimeExtractor.extract_datetime_with_fallback(None, "12:00:00", tmp.name)
        assert date == file_date
        assert time == "12:00:00"
        date, time = DateTimeExtractor.extract_datetime_with_fallback("2025-08-17", None, tmp.name)
        assert date == "2025-08-17"
        assert time == file_time
    os.remove(tmp.name)
