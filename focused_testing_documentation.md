# Focused Testing Techniques Documentation

## Defect Coverage with Unit Tests

### Issue #1: Lack of NoneType Exception Handling
**Test Class:** `TestNoneTypeExceptions`
**Number of Tests:** 8

### Issue #4: Lack of HTTP Request Timeouts  
**Test Class:** `TestHTTPTimeoutHandling`
**Number of Tests:** 8

---

## Testing Techniques Used (From Code Complete Chapter 22.3)

### 1. **Equivalence-class partitioning**
- **Where used:** 
  - `test_equivalence_class_valid_html()` - Valid HTML (valid class)
  - `test_equivalence_class_invalid_html()` - Invalid HTML (invalid class)
  - `test_equivalence_class_successful_request()` - Successful HTTP (valid class)
  - `test_equivalence_class_failed_request()` - Failed HTTP (invalid class)
- **Description:** Dividing input data into equivalence classes where all members should behave similarly
- **Example:** Valid HTML with all elements vs Invalid HTML missing elements

### 2. **Boundary-value analysis**
- **Where used:**
  - `test_boundary_value_empty_html()` - Completely empty HTML
  - `test_boundary_value_minimal_html()` - Minimal valid HTML structure
  - `test_boundary_value_timeout_edge()` - Edge of timeout conditions
- **Description:** Testing at the boundaries of input domains
- **Example:** Empty HTML, minimal HTML structure

### 3. **Error guessing**
- **Where used:**
  - `test_error_guessing_none_elements()` - Guessing None.text access error
  - `test_error_guessing_common_network_issues()` - Guessing network errors
- **Description:** Using experience and intuition to guess likely error conditions
- **Example:** Accessing .text on None elements, common network failures

### 4. **Statement & branch coverage**
- **Where used:**
  - `test_statement_branch_coverage_scrapenews2()` - Testing both valid and error paths
  - `test_statement_branch_coverage_fetch()` - Testing success and exception branches
- **Description:** Ensuring all statements and branches in code are executed during testing
- **Example:** Testing both success and failure paths in fetch() method

### 5. **Path / condition coverage**
- **Where used:**
  - `test_path_condition_coverage_scrape_site()` - Testing all conditional paths in scrape_site
  - `test_path_condition_coverage_fetch_flow()` - Testing different execution paths in fetch
- **Description:** Testing all possible paths through conditional statements
- **Example:** Testing all if/elif/else conditions in scrape_site() method

### 6. **Data-flow or state-based**
- **Where used:**
  - `test_data_flow_state_based_news_queue()` - Testing queue state changes
- **Description:** Testing how data flows through the system and state transitions
- **Example:** Queue empty → add data → queue full → retrieve data → queue empty

### 7. **Stress / performance**
- **Where used:**
  - `test_stress_performance_multiple_requests()` - Multiple rapid HTTP requests
- **Description:** Testing system behavior under stress conditions and performance requirements
- **Example:** 10 rapid consecutive HTTP requests with timing verification

### 8. **Regression**
- **Where used:**
  - `test_regression_fetch_behavior_consistency()` - Ensuring consistent behavior
- **Description:** Ensuring that previously working functionality continues to work
- **Example:** Multiple identical calls should produce identical results

---

## Test Coverage Summary

### Issue #1 (NoneType Exceptions): 8 tests
1. `test_equivalence_class_valid_html` - Equivalence-class partitioning
2. `test_equivalence_class_invalid_html` - Equivalence-class partitioning  
3. `test_boundary_value_empty_html` - Boundary-value analysis
4. `test_boundary_value_minimal_html` - Boundary-value analysis
5. `test_error_guessing_none_elements` - Error guessing
6. `test_statement_branch_coverage_scrapenews2` - Statement & branch coverage
7. `test_path_condition_coverage_scrape_site` - Path/condition coverage
8. `test_data_flow_state_based_news_queue` - Data-flow or state-based

### Issue #4 (HTTP Timeout): 8 tests
1. `test_equivalence_class_successful_request` - Equivalence-class partitioning
2. `test_equivalence_class_failed_request` - Equivalence-class partitioning
3. `test_boundary_value_timeout_edge` - Boundary-value analysis
4. `test_error_guessing_common_network_issues` - Error guessing
5. `test_statement_branch_coverage_fetch` - Statement & branch coverage
6. `test_path_condition_coverage_fetch_flow` - Path/condition coverage
7. `test_stress_performance_multiple_requests` - Stress/performance
8. `test_regression_fetch_behavior_consistency` - Regression

**Total number of tests:** 16 (exactly 8 per defect)
**Testing techniques used:** 8 (exactly matching the image) 