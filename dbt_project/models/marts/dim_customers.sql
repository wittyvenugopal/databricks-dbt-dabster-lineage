select
    customers.customer_id,
    customers.customer_name,
    customers.country,
    count(orders.order_id) as completed_order_count,
    coalesce(sum(orders.gross_amount), 0) as lifetime_spend
from {{ ref('stg_customers') }} as customers
left join {{ ref('int_order_details') }} as orders
    on customers.customer_id = orders.customer_id
    and orders.order_status = 'completed'
group by customers.customer_id, customers.customer_name, customers.country
