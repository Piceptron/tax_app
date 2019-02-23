# Deductive
> "Don't Spend Money to Save Money!"

**Target**: Self contained workers
**Purpose**: Cut out the middleman revolving tax/accounting people, as they charge rediculous rates.
**Research Needed**:

- The Accounting Process
- Product Recommendation Software

## Acounting Expenses
- Home & Office
- Vehicle
- Supplies & Tools
- Computers & Software
- Travel
- Meals and Entertainment

## MVP (Minimum Viable Product)
- Receipt OCR
- End of the year sums
- Image Uploading
- Dummy discrete categories

## Database

### Receipt
| Data Type | Identifier    |
|-----------|---------------|
| `int`     | `id`          |
| `long 64` | `image_str`   |
| `int`     | `year`        |
| `int`     | `month`       |
| `int`     | `day`         |
| `int`     | `user_id`     |
| `float`   | `tax_percent` |
| `float`   | `price`       |
| `str`     | `company`     |
| `str`     | `metadata`    |

### User
| Data Type | Identifier    |
|-----------|---------------|
| `str`     | `company`     |
| `float`   | `income`      |
| `str`     | `location`    |
| `{}`      | `contact_info`|
| `str`     | `job_type`    |

## Issues
- Accounting is complicated

## Remarks
- accuracy doesn't matter
    - demo clearly shows how product works
    - commercial aspect of this pitch should be encouraged
    - mock the database
- react library item classifier
