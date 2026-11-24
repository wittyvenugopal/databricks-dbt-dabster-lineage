select policies.policy_id, policies.customer_id, policies.quote_id
from {{ ref('stg_policies') }} as policies
inner join {{ ref('stg_quotes') }} as quotes
    on policies.quote_id = quotes.quote_id
where policies.customer_id <> quotes.customer_id
