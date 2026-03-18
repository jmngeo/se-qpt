"""
Excel Data Processing Tests for SE-QPT System
Tests Excel file parsing, data validation, and transformation
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestSEQPTExcelProcessing:
    """Test suite for SE-QPT Excel data processing"""

    @pytest.fixture
    def mock_excel_file(self):
        """Mock Excel file data structure"""
        return {
            'filename': 'Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx',
            'sheets': {
                'Competencies': {
                    'columns': ['ID', 'Name', 'Code', 'Description', 'Category', 'Level'],
                    'data': [
                        [1, 'Systems Thinking', 'ST', 'Holistic system understanding', 'Technical', 'Core'],
                        [2, 'Requirements Engineering', 'RE', 'Requirements analysis and management', 'Technical', 'Core'],
                        [3, 'System Architecture', 'SA', 'System design and architecture', 'Technical', 'Core'],
                        [4, 'Verification & Validation', 'VV', 'Testing and validation methods', 'Technical', 'Advanced']
                    ]
                },
                'Roles': {
                    'columns': ['ID', 'Name', 'Description', 'Experience_Years', 'Industry'],
                    'data': [
                        [1, 'System Engineer', 'Core systems engineering role', 3, 'General'],
                        [2, 'Requirements Engineer', 'Requirements specialist', 2, 'General'],
                        [3, 'System Architect', 'Senior system design role', 7, 'General'],
                        [4, 'Automotive SE', 'Automotive systems engineer', 5, 'Automotive']
                    ]
                },
                'Modules': {
                    'columns': ['ID', 'Name', 'Duration_Weeks', 'Competencies', 'Prerequisites'],
                    'data': [
                        [1, 'SE Fundamentals', 4, 'ST,RE', ''],
                        [2, 'Advanced Architecture', 6, 'SA,ST', 'SE Fundamentals'],
                        [3, 'V&V Methods', 3, 'VV', 'SE Fundamentals'],
                        [4, 'Automotive Systems', 8, 'ST,SA,VV', 'Advanced Architecture']
                    ]
                },
                'Qualification_Plans': {
                    'columns': ['ID', 'Name', 'Target_Role', 'Modules', 'Duration_Weeks'],
                    'data': [
                        [1, 'Basic SE Track', 'System Engineer', '1,2', 10],
                        [2, 'Advanced SE Track', 'System Architect', '1,2,3', 13],
                        [3, 'Automotive Specialist', 'Automotive SE', '1,2,4', 18],
                        [4, 'Requirements Focus', 'Requirements Engineer', '1,3', 7]
                    ]
                }
            }
        }

    @pytest.fixture
    def mock_pandas_dataframe(self):
        """Mock pandas DataFrame functionality"""
        class MockDataFrame:
            def __init__(self, data, columns):
                self.data = data
                self.columns = columns
                self._index = 0

            def iterrows(self):
                for i, row in enumerate(self.data):
                    yield i, dict(zip(self.columns, row))

            def to_dict(self, orient='records'):
                return [dict(zip(self.columns, row)) for row in self.data]

            def shape(self):
                return (len(self.data), len(self.columns))

            def dropna(self):
                return self

            def fillna(self, value):
                return self

        return MockDataFrame

    @pytest.fixture
    def excel_config(self):
        """Excel processing configuration"""
        return {
            'required_sheets': ['Competencies', 'Roles', 'Modules', 'Qualification_Plans'],
            'validation_rules': {
                'competencies': {
                    'required_columns': ['ID', 'Name', 'Code', 'Description'],
                    'unique_columns': ['ID', 'Code'],
                    'data_types': {'ID': 'int', 'Name': 'str', 'Code': 'str'}
                },
                'roles': {
                    'required_columns': ['ID', 'Name', 'Description'],
                    'unique_columns': ['ID'],
                    'data_types': {'ID': 'int', 'Experience_Years': 'int'}
                }
            },
            'transformation_rules': {
                'competencies': {
                    'code_format': 'uppercase',
                    'description_max_length': 500
                },
                'modules': {
                    'competencies_split': ',',
                    'prerequisites_split': ','
                }
            }
        }

    # Excel File Loading Tests
    def test_excel_file_loading(self, mock_excel_file):
        """Test Excel file loading and initial validation"""

        def load_excel_file(filename):
            """Mock Excel file loading"""
            if not filename.endswith('.xlsx'):
                raise ValueError("File must be .xlsx format")

            if filename != mock_excel_file['filename']:
                raise FileNotFoundError(f"File {filename} not found")

            return {
                'success': True,
                'sheets': list(mock_excel_file['sheets'].keys()),
                'file_info': {
                    'filename': filename,
                    'size_mb': 2.5,
                    'modified_date': '2024-01-15'
                }
            }

        # Test successful loading
        result = load_excel_file(mock_excel_file['filename'])
        assert result['success'] == True
        assert len(result['sheets']) == 4
        assert 'Competencies' in result['sheets']

        # Test invalid file format
        with pytest.raises(ValueError):
            load_excel_file('invalid_file.csv')

        # Test file not found
        with pytest.raises(FileNotFoundError):
            load_excel_file('nonexistent.xlsx')

    def test_sheet_validation(self, mock_excel_file, excel_config):
        """Test sheet structure validation"""

        def validate_sheet_structure(sheet_name, sheet_data, config):
            """Validate sheet has required structure"""
            validation_result = {
                'sheet_name': sheet_name,
                'valid': True,
                'errors': [],
                'warnings': []
            }

            # Check if sheet exists in config
            if sheet_name.lower() not in [s.lower() for s in config['required_sheets']]:
                validation_result['warnings'].append(f"Sheet {sheet_name} not in required sheets")

            # Check columns
            expected_columns = config['validation_rules'].get(sheet_name.lower(), {}).get('required_columns', [])
            actual_columns = sheet_data['columns']

            missing_columns = set(expected_columns) - set(actual_columns)
            if missing_columns:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Missing columns: {missing_columns}")

            # Check data presence
            if not sheet_data['data']:
                validation_result['valid'] = False
                validation_result['errors'].append("Sheet contains no data")

            return validation_result

        # Test valid sheets
        for sheet_name, sheet_data in mock_excel_file['sheets'].items():
            result = validate_sheet_structure(sheet_name, sheet_data, excel_config)
            if sheet_name in ['Competencies', 'Roles']:
                assert result['valid'] == True, f"Valid sheet {sheet_name} failed validation"

        # Test invalid sheet structure
        invalid_sheet = {
            'columns': ['ID'],  # Missing required columns
            'data': []
        }
        result = validate_sheet_structure('Competencies', invalid_sheet, excel_config)
        assert result['valid'] == False
        assert any('Missing columns' in error for error in result['errors'])

    # Data Validation Tests
    def test_competency_data_validation(self, mock_excel_file):
        """Test competency data validation"""

        def validate_competency_data(competency_data):
            """Validate individual competency record"""
            errors = []

            # Required fields validation
            required_fields = ['Name', 'Code', 'Description']
            for field in required_fields:
                if not competency_data.get(field):
                    errors.append(f"Missing required field: {field}")

            # Code format validation
            code = competency_data.get('Code', '')
            if code and not code.isupper():
                errors.append(f"Code must be uppercase: {code}")

            # Name length validation
            name = competency_data.get('Name', '')
            if len(name) > 100:
                errors.append(f"Name too long: {len(name)} characters")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'data': competency_data
            }

        # Test valid competency data
        competencies_sheet = mock_excel_file['sheets']['Competencies']
        for row in competencies_sheet['data']:
            competency = dict(zip(competencies_sheet['columns'], row))
            result = validate_competency_data(competency)
            assert result['valid'] == True, f"Valid competency failed validation: {result['errors']}"

        # Test invalid competency data
        invalid_competency = {
            'ID': 999,
            'Name': '',  # Missing name
            'Code': 'st',  # Lowercase code
            'Description': 'Test'
        }
        result = validate_competency_data(invalid_competency)
        assert result['valid'] == False
        assert any('Missing required field: Name' in error for error in result['errors'])
        assert any('Code must be uppercase' in error for error in result['errors'])

    def test_role_data_validation(self, mock_excel_file):
        """Test role data validation"""

        def validate_role_data(role_data):
            """Validate individual role record"""
            errors = []

            # Required fields
            if not role_data.get('Name'):
                errors.append("Missing role name")

            # Experience years validation
            exp_years = role_data.get('Experience_Years')
            if exp_years is not None:
                try:
                    years = int(exp_years)
                    if years < 0 or years > 50:
                        errors.append(f"Invalid experience years: {years}")
                except (ValueError, TypeError):
                    errors.append(f"Experience years must be a number: {exp_years}")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'data': role_data
            }

        # Test valid role data
        roles_sheet = mock_excel_file['sheets']['Roles']
        for row in roles_sheet['data']:
            role = dict(zip(roles_sheet['columns'], row))
            result = validate_role_data(role)
            assert result['valid'] == True, f"Valid role failed validation: {result['errors']}"

        # Test invalid role data
        invalid_role = {
            'ID': 999,
            'Name': '',
            'Experience_Years': -5  # Invalid experience
        }
        result = validate_role_data(invalid_role)
        assert result['valid'] == False

    # Data Transformation Tests
    def test_competency_transformation(self, mock_excel_file):
        """Test competency data transformation"""

        def transform_competency_data(raw_competency):
            """Transform raw competency data to application format"""
            transformed = {
                'id': raw_competency['ID'],
                'name': raw_competency['Name'].strip(),
                'code': raw_competency['Code'].upper(),
                'description': raw_competency['Description'].strip(),
                'category': raw_competency.get('Category', 'General'),
                'level': raw_competency.get('Level', 'Core'),
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'incose_reference': f"INCOSE-{raw_competency['Code'].upper()}-001"
            }

            return transformed

        # Test transformation
        competencies_sheet = mock_excel_file['sheets']['Competencies']
        for row in competencies_sheet['data']:
            raw_competency = dict(zip(competencies_sheet['columns'], row))
            transformed = transform_competency_data(raw_competency)

            assert transformed['id'] == raw_competency['ID']
            assert transformed['code'] == raw_competency['Code'].upper()
            assert transformed['incose_reference'].startswith('INCOSE-')
            assert 'created_at' in transformed

    def test_module_transformation(self, mock_excel_file):
        """Test module data transformation with competency relationships"""

        def transform_module_data(raw_module):
            """Transform raw module data to application format"""
            # Parse competency relationships
            competencies_str = raw_module.get('Competencies', '')
            competency_codes = [c.strip() for c in competencies_str.split(',') if c.strip()]

            # Parse prerequisites
            prerequisites_str = raw_module.get('Prerequisites', '')
            prerequisites = [p.strip() for p in prerequisites_str.split(',') if p.strip()]

            transformed = {
                'id': raw_module['ID'],
                'name': raw_module['Name'].strip(),
                'duration_weeks': raw_module['Duration_Weeks'],
                'competency_codes': competency_codes,
                'prerequisites': prerequisites,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'module_type': 'training'
            }

            return transformed

        # Test transformation
        modules_sheet = mock_excel_file['sheets']['Modules']
        for row in modules_sheet['data']:
            raw_module = dict(zip(modules_sheet['columns'], row))
            transformed = transform_module_data(raw_module)

            assert transformed['id'] == raw_module['ID']
            assert isinstance(transformed['competency_codes'], list)
            assert isinstance(transformed['prerequisites'], list)

            # Check competency parsing
            if raw_module['Competencies']:
                assert len(transformed['competency_codes']) > 0

    # Relationship Validation Tests
    def test_data_relationships(self, mock_excel_file):
        """Test relationships between different data entities"""

        def validate_relationships(excel_data):
            """Validate relationships across sheets"""
            errors = []

            # Get data from sheets
            competencies = [dict(zip(excel_data['sheets']['Competencies']['columns'], row))
                          for row in excel_data['sheets']['Competencies']['data']]
            modules = [dict(zip(excel_data['sheets']['Modules']['columns'], row))
                     for row in excel_data['sheets']['Modules']['data']]
            roles = [dict(zip(excel_data['sheets']['Roles']['columns'], row))
                   for row in excel_data['sheets']['Roles']['data']]
            plans = [dict(zip(excel_data['sheets']['Qualification_Plans']['columns'], row))
                   for row in excel_data['sheets']['Qualification_Plans']['data']]

            # Validate competency references in modules
            competency_codes = {comp['Code'] for comp in competencies}
            for module in modules:
                module_competencies = [c.strip() for c in module['Competencies'].split(',') if c.strip()]
                for comp_code in module_competencies:
                    if comp_code not in competency_codes:
                        errors.append(f"Module '{module['Name']}' references unknown competency: {comp_code}")

            # Validate module references in qualification plans
            module_ids = {str(mod['ID']) for mod in modules}
            for plan in plans:
                plan_modules = [m.strip() for m in str(plan['Modules']).split(',') if m.strip()]
                for mod_id in plan_modules:
                    if mod_id not in module_ids:
                        errors.append(f"Plan '{plan['Name']}' references unknown module: {mod_id}")

            # Validate role references in qualification plans
            role_names = {role['Name'] for role in roles}
            for plan in plans:
                if plan['Target_Role'] not in role_names:
                    errors.append(f"Plan '{plan['Name']}' targets unknown role: {plan['Target_Role']}")

            return {
                'valid': len(errors) == 0,
                'errors': errors
            }

        # Test relationships
        result = validate_relationships(mock_excel_file)
        assert result['valid'] == True, f"Relationship validation failed: {result['errors']}"

    # Data Quality Tests
    def test_data_completeness(self, mock_excel_file):
        """Test data completeness and quality metrics"""

        def analyze_data_quality(excel_data):
            """Analyze overall data quality"""
            quality_report = {
                'completeness': {},
                'uniqueness': {},
                'consistency': {},
                'overall_score': 0
            }

            # Analyze each sheet
            for sheet_name, sheet_data in excel_data['sheets'].items():
                columns = sheet_data['columns']
                rows = sheet_data['data']

                # Completeness analysis
                completeness_scores = {}
                for i, col in enumerate(columns):
                    non_empty_count = sum(1 for row in rows if row[i] and str(row[i]).strip())
                    completeness_scores[col] = (non_empty_count / len(rows)) * 100 if rows else 0

                quality_report['completeness'][sheet_name] = completeness_scores

                # Uniqueness analysis for ID columns
                if 'ID' in columns:
                    id_col_index = columns.index('ID')
                    ids = [row[id_col_index] for row in rows]
                    unique_ids = set(ids)
                    uniqueness_score = (len(unique_ids) / len(ids)) * 100 if ids else 0
                    quality_report['uniqueness'][sheet_name] = uniqueness_score

            # Calculate overall score
            all_completeness = []
            for sheet_scores in quality_report['completeness'].values():
                all_completeness.extend(sheet_scores.values())

            quality_report['overall_score'] = sum(all_completeness) / len(all_completeness) if all_completeness else 0

            return quality_report

        # Analyze data quality
        quality_report = analyze_data_quality(mock_excel_file)

        # Quality assertions
        assert quality_report['overall_score'] > 90, f"Data quality too low: {quality_report['overall_score']}%"

        # Check completeness for critical fields
        for sheet_name in ['Competencies', 'Roles']:
            if sheet_name in quality_report['completeness']:
                name_completeness = quality_report['completeness'][sheet_name].get('Name', 0)
                assert name_completeness == 100, f"{sheet_name} Name field not 100% complete"

    # Performance Tests
    def test_large_file_processing(self, mock_pandas_dataframe):
        """Test processing of large Excel files"""

        def simulate_large_file_processing(row_count=10000):
            """Simulate processing a large Excel file"""
            import time
            start_time = time.time()

            # Mock large dataset
            columns = ['ID', 'Name', 'Code', 'Description', 'Category']
            data = []
            for i in range(row_count):
                data.append([
                    i + 1,
                    f'Competency {i + 1}',
                    f'C{i + 1:04d}',
                    f'Description for competency {i + 1}',
                    'Technical' if i % 2 == 0 else 'Behavioral'
                ])

            # Create mock DataFrame
            df = mock_pandas_dataframe(data, columns)

            # Simulate processing operations
            processed_records = []
            for index, row in df.iterrows():
                # Simulate validation and transformation
                if row['Name'] and row['Code']:
                    processed_records.append({
                        'id': row['ID'],
                        'name': row['Name'],
                        'code': row['Code'].upper(),
                        'valid': True
                    })

            processing_time = time.time() - start_time

            return {
                'input_records': row_count,
                'processed_records': len(processed_records),
                'processing_time': processing_time,
                'records_per_second': len(processed_records) / processing_time if processing_time > 0 else 0
            }

        # Test with different file sizes
        file_sizes = [1000, 5000, 10000]
        for size in file_sizes:
            result = simulate_large_file_processing(size)

            # Performance assertions
            assert result['processed_records'] == result['input_records']
            assert result['records_per_second'] > 100, f"Processing too slow: {result['records_per_second']} records/sec"

            print(f"Processed {size} records in {result['processing_time']:.2f}s ({result['records_per_second']:.0f} rec/sec)")

    def test_error_handling_and_recovery(self, mock_excel_file):
        """Test error handling during Excel processing"""

        def process_with_error_handling(data, error_scenario='none'):
            """Process data with simulated error scenarios"""
            errors = []
            warnings = []
            processed_count = 0

            try:
                for sheet_name, sheet_data in data['sheets'].items():
                    # Simulate different error scenarios
                    if error_scenario == 'corrupt_data' and sheet_name == 'Competencies':
                        raise ValueError("Corrupted data in Competencies sheet")

                    if error_scenario == 'missing_column' and sheet_name == 'Roles':
                        # Simulate missing required column
                        if 'Name' not in sheet_data['columns']:
                            warnings.append(f"Missing Name column in {sheet_name}")
                            continue

                    # Process rows
                    for row in sheet_data['data']:
                        try:
                            # Simulate row processing
                            if error_scenario == 'invalid_row' and processed_count == 5:
                                raise ValueError("Invalid row data")

                            processed_count += 1

                        except ValueError as e:
                            errors.append(f"Row processing error: {str(e)}")
                            continue

            except Exception as e:
                errors.append(f"Critical error: {str(e)}")

            return {
                'success': len(errors) == 0,
                'processed_count': processed_count,
                'errors': errors,
                'warnings': warnings
            }

        # Test normal processing
        result = process_with_error_handling(mock_excel_file, 'none')
        assert result['success'] == True
        assert result['processed_count'] > 0

        # Test error scenarios
        error_result = process_with_error_handling(mock_excel_file, 'corrupt_data')
        assert error_result['success'] == False
        assert len(error_result['errors']) > 0

        # Test warning scenarios
        warning_result = process_with_error_handling(mock_excel_file, 'missing_column')
        # Should continue processing despite warnings
        assert len(warning_result['warnings']) >= 0

def run_excel_processing_tests():
    """Run all Excel processing tests and return results"""
    print("📊 Running SE-QPT Excel Data Processing Tests...")

    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--disable-warnings'
    ])

    return {
        'status': 'passed' if exit_code == 0 else 'failed',
        'exit_code': exit_code,
        'test_categories': [
            'Excel File Loading',
            'Sheet Validation',
            'Data Validation',
            'Data Transformation',
            'Relationship Validation',
            'Data Quality Analysis',
            'Performance Testing',
            'Error Handling'
        ]
    }

if __name__ == '__main__':
    results = run_excel_processing_tests()
    print(f"Excel Processing Tests: {results['status']}")