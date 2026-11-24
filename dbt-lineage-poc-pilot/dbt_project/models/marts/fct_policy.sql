select
    policies.policy_id,
    policies.customer_id,
    policies.quote_id,
    customers.country,
    quotes.cover_type,
    policies.effective_date,
    policies.policy_status,
    quotes.currency,
    quotes.quoted_premium,
    policies.annual_premium
from {{ ref('stg_policies') }} as policies
inner join {{ ref('stg_customers') }} as customers
    on policies.customer_id = customers.customer_id
inner join {{ ref('stg_quotes') }} as quotes
    on policies.quote_id = quotes.quote_id
    and policies.customer_id = quotes.customer_id
