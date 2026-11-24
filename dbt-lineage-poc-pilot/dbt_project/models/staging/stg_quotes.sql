select
    cast(quote_id as int) as quote_id,
    cast(customer_id as int) as customer_id,
    lower(trim(cover_type)) as cover_type,
    upper(trim(currency)) as currency,
    cast(quoted_premium as decimal(12, 2)) as quoted_premium
from {{ ref('raw_quotes') }}
