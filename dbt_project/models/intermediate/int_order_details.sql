select
    orders.order_id,
    orders.order_date,
    orders.order_status,
    orders.quantity,
    customers.customer_id,
    customers.country,
    products.product_id,
    products.category,
    products.unit_price,
    {{ calculate_amount('orders.quantity', 'products.unit_price') }} as gross_amount
from {{ ref('stg_orders') }} as orders
inner join {{ ref('stg_customers') }} as customers
    on orders.customer_id = customers.customer_id
inner join {{ ref('stg_products') }} as products
    on orders.product_id = products.product_id
