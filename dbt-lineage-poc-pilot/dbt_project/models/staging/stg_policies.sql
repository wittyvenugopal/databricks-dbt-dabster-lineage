select
    cast(policy_id as int) as policy_id,
    cast(customer_id as int) as customer_id,
    cast(quote_id as int) as quote_id,
    cast(effective_date as date) as effective_date,
    lower(trim(policy_status)) as policy_status,
    cast(annual_premium as decimal(12, 2)) as annual_premium
from {{ ref('raw_policies') }}
