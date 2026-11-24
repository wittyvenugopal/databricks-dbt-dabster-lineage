-- Adjust the seven-day window to include the run under investigation.
select distinct
    source_table_full_name as upstream,
    target_table_full_name as downstream
from system.access.table_lineage
where event_date >= date_sub(current_date(), 7)
    and source_table_full_name is not null
    and target_table_full_name is not null
    and (
        startswith(source_table_full_name, 'sandbox_catalog.dbt_lineage_poc.')
        or startswith(target_table_full_name, 'sandbox_catalog.dbt_lineage_poc.')
    )
order by downstream, upstream;

select distinct
    source_table_full_name,
    source_column_name,
    target_table_full_name,
    target_column_name
from system.access.column_lineage
where event_date >= date_sub(current_date(), 7)
    and startswith(target_table_full_name, 'sandbox_catalog.dbt_lineage_poc.')
order by target_table_full_name, target_column_name, source_table_full_name, source_column_name;
