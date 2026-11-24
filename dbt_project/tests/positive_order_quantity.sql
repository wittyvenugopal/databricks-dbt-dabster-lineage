select order_id, quantity
from {{ ref('stg_orders') }}
where order_status = 'completed'
    and (quantity is null or quantity <= 0)
