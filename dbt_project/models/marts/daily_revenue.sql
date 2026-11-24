select
    order_date,
    count(*) as completed_order_count,
    sum(gross_amount) as revenue
from {{ ref('int_order_details') }}
where order_status = 'completed'
group by order_date
