import unittest
from backend.routes.data_management import extract_year_month_from_filename

class TestDataManagement(unittest.TestCase):

    def test_extract_year_month_from_filename(self):
        # Test with different filename formats
        self.assertEqual(extract_year_month_from_filename('sample_data_2023-01.xlsx'), (2023, 1))
        self.assertEqual(extract_year_month_from_filename('sample_data_2023_1.xlsx'), (2023, 1))
        self.assertEqual(extract_year_month_from_filename('2023年1月.xlsx'), (2023, 1))
        self.assertEqual(extract_year_month_from_filename('2023年12月.xlsx'), (2023, 12))
        self.assertEqual(extract_year_month_from_filename('prefix_2024-12.xlsx'), (2024, 12))

    def test_extract_year_month_from_filename_invalid(self):
        # Test with invalid filenames
        self.assertEqual(extract_year_month_from_filename('sample_data.xlsx'), (None, None))
        self.assertEqual(extract_year_month_from_filename('2023-01.xlsx'), (None, None))
        self.assertEqual(extract_year_month_from_filename('sample_data_2023-13.xlsx'), (2023, 13))
        self.assertEqual(extract_year_month_from_filename('sample_data_2023-0.xlsx'), (2023, 0))

if __name__ == '__main__':
    unittest.main()
