select
    cast(product_id as int) as product_id,
    trim(product_name) as product_name,
    trim(category) as category,
    cast(unit_price as decimal(10, 2)) as unit_price
from {{ ref('raw_products') }}
