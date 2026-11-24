select
    order_id,
    order_date,
    customer_id,
    country,
    product_id,
    category,
    quantity,
    unit_price,
    gross_amount
from {{ ref('int_order_details') }}
where order_status = 'completed'
